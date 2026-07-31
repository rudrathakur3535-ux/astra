import pytest
from app.browser.navigation import NavigationHelper
from app.browser.web_reader import WebReader
from app.browser.browser_session import BrowserSessionManager
from app.adapters.playwright_adapter import PlaywrightAdapter

def test_navigation_helper():
    google_url = NavigationHelper.build_google_search_url("Binary Search")
    assert "google.com/search?q=Binary+Search" in google_url

    yt_url = NavigationHelper.build_youtube_search_url("LangGraph")
    assert "youtube.com/results?search_query=LangGraph" in yt_url

    gh_url = NavigationHelper.build_github_search_url("Astra")
    assert "github.com/search?q=Astra" in gh_url

def test_web_reader_extraction():
    sample_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <script>console.log('strip me');</script>
            <h1>Main Title</h1>
            <p>This is a paragraph of important content.</p>
        </body>
    </html>
    """
    clean_text = WebReader.extract_markdown_content(sample_html)
    assert "# Main Title" in clean_text
    assert "important content" in clean_text
    assert "console.log" not in clean_text

def test_browser_session_manager():
    session = BrowserSessionManager()
    session.update_tab_info(0, "https://google.com", "Google")
    session.update_tab_info(1, "https://youtube.com", "YouTube")

    assert session.find_tab_by_domain("youtube") == 1
    assert session.find_tab_by_domain("google") == 0

    info = session.get_current_tab_info()
    assert info["active_index"] == 0
    assert info["total_tabs"] == 2

def test_playwright_adapter_headless():
    adapter = PlaywrightAdapter(headless=True)
    try:
        res = adapter.open_url("https://example.com")
        assert res["status"] == "success"
        assert "example.com" in res["url"].lower()

        title = adapter.page_title()
        assert len(title) > 0

        current = adapter.current_page()
        assert current["active_index"] == 0

        # Intelligent reader content
        content = adapter.read_page(max_length=500)
        assert len(content) > 0

    finally:
        adapter.close()
