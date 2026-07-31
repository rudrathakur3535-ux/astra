from pathlib import Path
from typing import List
from app.utils.logger import logger

class DownloadManager:
    """Manages browser download directory and tracks downloaded files."""

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or (Path.home() / "Downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def list_recent_downloads(self, count: int = 5) -> List[Path]:
        """Returns list of recent files in download directory."""
        try:
            files = [f for f in self.download_dir.iterdir() if f.is_file()]
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return files[:count]
        except Exception as e:
            logger.error(f"Error listing downloads: {e}")
            return []
