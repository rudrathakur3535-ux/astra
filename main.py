"""
Project Astra - Main Entrypoint
Day 3: Ears & Natural Voice Subsystem Integration.
"""

import sys
import io

# Enforce UTF-8 output encoding for Windows compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
