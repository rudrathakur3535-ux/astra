import urllib.parse

class NavigationHelper:
    """Helper formatting URLs for domain-specific searches and navigation."""

    @staticmethod
    def build_google_search_url(query: str) -> str:
        encoded = urllib.parse.quote_plus(query.strip())
        return f"https://www.google.com/search?q={encoded}"

    @staticmethod
    def build_youtube_search_url(query: str) -> str:
        encoded = urllib.parse.quote_plus(query.strip())
        return f"https://www.youtube.com/results?search_query={encoded}"

    @staticmethod
    def build_github_search_url(query: str) -> str:
        encoded = urllib.parse.quote_plus(query.strip())
        return f"https://github.com/search?q={encoded}"

    @staticmethod
    def normalize_url(url: str) -> str:
        clean = url.strip()
        if not clean.startswith("http://") and not clean.startswith("https://"):
            return f"https://{clean}"
        return clean
