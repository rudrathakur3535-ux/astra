import logging
import sys
from pathlib import Path
from rich.logging import RichHandler

def setup_logger(
    name: str = "Astra",
    log_file: str = "app/logs/astra.log",
    level: str = "INFO"
) -> logging.Logger:
    """Configures and returns a production-ready logger for Project Astra.
    
    Args:
        name: Name of the logger instance.
        log_file: Path to log output file.
        level: Logging level (e.g. INFO, DEBUG, ERROR).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if logger is already configured
    if logger.hasHandlers():
        return logger

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File Handler - Structured text format
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    # Console Handler - Rich color formatting
    rich_handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        show_time=False,
        show_level=True,
        markup=True
    )
    rich_handler.setLevel(log_level)
    logger.addHandler(rich_handler)

    return logger

# Global default logger instance
logger = setup_logger()
