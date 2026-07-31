from typing import Optional
from app.ports.browser_port import BrowserPort
from app.adapters.playwright_adapter import PlaywrightAdapter
from app.utils.logger import logger

class BrowserManager:
    """Manager providing access to active BrowserPort adapter instance."""

    def __init__(self, adapter: Optional[BrowserPort] = None):
        self._adapter = adapter or PlaywrightAdapter(headless=False)

    @property
    def adapter(self) -> BrowserPort:
        return self._adapter

    def shutdown(self) -> None:
        """Shuts down browser engine."""
        try:
            self._adapter.close()
            logger.info("Browser engine shutdown successfully.")
        except Exception as e:
            logger.error(f"Error shutting down browser manager: {e}")

# Global browser manager instance
browser_manager = BrowserManager()
