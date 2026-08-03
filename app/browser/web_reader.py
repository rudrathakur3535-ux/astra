import re
from bs4 import BeautifulSoup
from app.utils.logger import logger

class WebReader:
    """Intelligent Page Reader converting raw HTML into clean Markdown for LLMs and Voice."""

    @staticmethod
    def extract_markdown_content(html_content: str, max_length: int = 4000) -> str:
        """Strips scripts, styles, ads, and navigations; returns clean markdown text.
        
        Args:
            html_content: Raw HTML text from page DOM.
            max_length: Maximum characters to truncate for LLM context window.
            
        Returns:
            str: Cleaned structured text content.
        """
        if not html_content or not html_content.strip():
            return "No content available on page."

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove non-content tags
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg", "noscript", "iframe"]):
                element.decompose()

            # Extract main or body content
            main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup

            # Convert headings & text
            lines = []
            for element in main_content.find_all(["h1", "h2", "h3", "p", "li"]):
                text = element.get_text().strip()
                if not text:
                    continue

                if element.name == "h1":
                    lines.append(f"\n# {text}\n")
                elif element.name == "h2":
                    lines.append(f"\n## {text}\n")
                elif element.name == "h3":
                    lines.append(f"\n### {text}\n")
                elif element.name == "li":
                    lines.append(f"* {text}")
                else:
                    lines.append(text)

            result_text = "\n".join(lines)
            if not result_text:
                # Fallback for pages using td/span/div text instead of h1-h3/p/li
                raw_text = main_content.get_text(separator="\n", strip=True)
                result_text = re.sub(r"\n{3,}", "\n\n", raw_text)

            result_text = re.sub(r"\n{3,}", "\n\n", result_text).strip()

            if len(result_text) > max_length:
                result_text = result_text[:max_length] + "\n\n... [Content Truncated]"

            logger.info(f"Extracted cleaned web text ({len(result_text)} chars)")
            return result_text if result_text else "Page content is empty."

        except Exception as e:
            logger.error(f"Error extracting web reader content: {e}")
            return "Failed to parse page content."
