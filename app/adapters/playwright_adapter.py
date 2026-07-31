import asyncio
import threading
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page, Error as PlaywrightError

from app.ports.browser_port import BrowserPort
from app.browser.browser_session import BrowserSessionManager
from app.browser.navigation import NavigationHelper
from app.browser.web_reader import WebReader
from app.utils.logger import logger

class PlaywrightAdapter(BrowserPort):
    """Hexagonal Adapter implementing BrowserPort using Playwright Chromium."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.session = BrowserSessionManager()
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._pages: List[Page] = []
        self._lock = threading.Lock()

    def _ensure_browser(self) -> None:
        """Launches or recovers persistent Playwright browser session if closed."""
        with self._lock:
            try:
                if self._browser and self._browser.is_connected() and self._context:
                    # Filter closed pages
                    self._pages = [p for p in self._pages if not p.is_closed()]
                    if self._pages:
                        return

                logger.info("Initializing Playwright Chromium browser instance...")
                if not self._playwright:
                    self._playwright = sync_playwright().start()

                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=["--start-maximized"]
                )
                self._context = self._browser.new_context(no_viewport=True)
                initial_page = self._context.new_page()
                self._pages = [initial_page]
                self.session.active_tab_index = 0
                self.session.update_tab_info(0, initial_page.url, initial_page.title() or "New Tab")
                logger.info("Playwright browser session started.")

            except Exception as e:
                logger.error(f"Failed to start Playwright browser: {e}")
                raise RuntimeError(f"Playwright initialization error: {e}")

    def _get_active_page(self) -> Page:
        """Returns the currently active page object."""
        self._ensure_browser()
        idx = min(self.session.active_tab_index, len(self._pages) - 1)
        page = self._pages[idx]
        if page.is_closed():
            logger.warning(f"Page at index {idx} was closed. Recovering...")
            self._pages.pop(idx)
            if not self._pages and self._context:
                self._pages.append(self._context.new_page())
            idx = max(0, len(self._pages) - 1)
            self.session.active_tab_index = idx
            page = self._pages[idx]
        return page

    def open_url(self, url: str) -> Dict[str, Any]:
        """Navigates current active tab to target URL."""
        target_url = NavigationHelper.normalize_url(url)
        page = self._get_active_page()
        try:
            logger.info(f"Navigating to: '{target_url}'")
            page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            title = page.title() or target_url
            self.session.update_tab_info(self.session.active_tab_index, page.url, title)
            return {
                "url": page.url,
                "title": title,
                "status": "success",
                "tab_index": self.session.active_tab_index
            }
        except PlaywrightError as e:
            logger.error(f"Failed to open URL '{target_url}': {e}")
            return {"error": str(e), "url": target_url, "status": "failed"}

    def google_search(self, query: str) -> Dict[str, Any]:
        """Performs Google search in browser."""
        url = NavigationHelper.build_google_search_url(query)
        return self.open_url(url)

    def youtube_search(self, query: str) -> Dict[str, Any]:
        """Performs YouTube search, reusing YouTube tab if open."""
        yt_tab_idx = self.session.find_tab_by_domain("youtube")
        if yt_tab_idx is not None:
            self.switch_tab(yt_tab_idx)

        url = NavigationHelper.build_youtube_search_url(query)
        return self.open_url(url)

    def github_search(self, query: str) -> Dict[str, Any]:
        """Performs GitHub search, reusing GitHub tab if open."""
        gh_tab_idx = self.session.find_tab_by_domain("github")
        if gh_tab_idx is not None:
            self.switch_tab(gh_tab_idx)

        url = NavigationHelper.build_github_search_url(query)
        return self.open_url(url)

    def current_page(self) -> Dict[str, Any]:
        """Returns details of current page."""
        page = self._get_active_page()
        title = page.title() or page.url
        self.session.update_tab_info(self.session.active_tab_index, page.url, title)
        return self.session.get_current_tab_info()

    def page_title(self) -> str:
        """Returns title of current active page."""
        page = self._get_active_page()
        return page.title() or page.url

    def read_page(self, max_length: int = 4000) -> str:
        """Extracts cleaned Markdown text content from current DOM."""
        page = self._get_active_page()
        try:
            html = page.content()
            return WebReader.extract_markdown_content(html, max_length=max_length)
        except Exception as e:
            logger.error(f"Error reading page content: {e}")
            return f"Failed to read page content: {e}"

    def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Opens a new browser tab."""
        self._ensure_browser()
        if not self._context:
            raise RuntimeError("Browser context uninitialized")

        new_p = self._context.new_page()
        self._pages.append(new_p)
        new_index = len(self._pages) - 1
        self.session.active_tab_index = new_index

        if url:
            return self.open_url(url)

        new_p.goto("about:blank")
        self.session.update_tab_info(new_index, "about:blank", "New Tab")
        return {"tab_index": new_index, "url": "about:blank", "title": "New Tab"}

    def close_tab(self, tab_index: Optional[int] = None) -> Dict[str, Any]:
        """Closes specified or active tab."""
        idx = tab_index if tab_index is not None else self.session.active_tab_index
        if 0 <= idx < len(self._pages):
            target_page = self._pages.pop(idx)
            if not target_page.is_closed():
                target_page.close()
            self.session.remove_tab_info(idx)
            logger.info(f"Closed tab index {idx}")

        if not self._pages and self._context:
            new_p = self._context.new_page()
            self._pages.append(new_p)
            self.session.active_tab_index = 0
            self.session.update_tab_info(0, "about:blank", "New Tab")

        return self.session.get_current_tab_info()

    def switch_tab(self, tab_index: int) -> Dict[str, Any]:
        """Switches active page focus to target tab index."""
        self._ensure_browser()
        if 0 <= tab_index < len(self._pages):
            self.session.active_tab_index = tab_index
            target_page = self._pages[tab_index]
            target_page.bring_to_front()
            logger.info(f"Switched active tab to index {tab_index}")
            return self.session.get_current_tab_info()
        return {"error": f"Tab index {tab_index} out of range (0-{len(self._pages)-1})"}

    def refresh(self) -> Dict[str, Any]:
        """Refreshes active page."""
        page = self._get_active_page()
        page.reload()
        return self.current_page()

    def back(self) -> Dict[str, Any]:
        """Navigates back in browser history."""
        page = self._get_active_page()
        page.go_back()
        return self.current_page()

    def forward(self) -> Dict[str, Any]:
        """Navigates forward in browser history."""
        page = self._get_active_page()
        page.go_forward()
        return self.current_page()

    def close(self) -> None:
        """Closes browser session and Playwright driver."""
        with self._lock:
            try:
                if self._browser:
                    self._browser.close()
                if self._playwright:
                    self._playwright.stop()
            except Exception as e:
                logger.error(f"Error shutting down Playwright: {e}")
            finally:
                self._browser = None
                self._playwright = None
                self._pages = []
