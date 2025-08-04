import logging
import os
from datetime import datetime

"""
This module sets up a reusable logger that writes logs to:
1. A log file with a unique timestamped name for each test run
2. The console (stdout)

Log files are stored in a 'logs/' directory located one level above the current file.
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_LOG_DIR = os.path.realpath(os.path.join(BASE_DIR, "..", "logs"))

os.makedirs(ROOT_LOG_DIR, exist_ok=True)


def get_logger(name: str):

    """
    Returns a logger instance configured with:
    - DEBUG level
    - Timestamped log file handler (writes to logs/test_log_YYYY-MM-DD_HH-MM-SS.log)
    - Console handler (prints logs to terminal)

    Each call with a unique `name` will return a logger named accordingly.
    Ensures that duplicate handlers are not added if logger already exists.

    Args:
        name (str): The name of the logger (typically __name__)

    Returns:
        logging.Logger: A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        """
        Set up the logger only once per name (avoids duplicate handlers).
        Log file is named using current datetime to keep logs organized and unique per run.
        """

        # Generate filename like '2025-08-04_21-52-13.log'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{timestamp}.log"
        file_path = os.path.join(ROOT_LOG_DIR, log_filename)

        # FileHandler: logs to file with full timestamp + level + message
        file_handler = logging.FileHandler(file_path, mode="a")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

        # StreamHandler: logs to terminal with level + message
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(console_handler)

    return logger
