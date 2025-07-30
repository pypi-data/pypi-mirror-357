import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import colorlog  

def setup_logger(name: str = "MCPServerLogger", level: int = logging.INFO) -> logging.Logger:
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    LOG_DIR = "logs"
    LOG_FILEPATH = os.path.join(LOG_DIR, "mcp_kyvos_server_logs.log")
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = RotatingFileHandler(
        LOG_FILEPATH, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    stream_handler = logging.StreamHandler(sys.stdout)

    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(module)s: %(message)s",
        datefmt=DATE_FORMAT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "EXCEPTION": "red",
            "CRITICAL": "bold_red",
        },
    )

    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:  # Prevent duplicate handlers
        file_handler.setFormatter(file_formatter)
        stream_handler.setFormatter(color_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    logger.propagate = False

    return logger