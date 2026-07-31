"""
Project Astra - Main Entrypoint
Day 2: Conversational Brain with Terminal Interface and Streaming Responses.
"""

import sys
from app.ui.cli import TerminalUI
from app.utils.logger import logger

def main():
    """Initializes and runs Project Astra AI OS."""
    try:
        logger.info("Starting Project Astra Application...")
        cli = TerminalUI()
        cli.run()
    except Exception as e:
        logger.critical(f"Fatal error starting Astra: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
