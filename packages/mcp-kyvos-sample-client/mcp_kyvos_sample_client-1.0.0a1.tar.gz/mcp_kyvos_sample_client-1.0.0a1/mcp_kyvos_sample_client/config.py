import os
import logging
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class DebugOnlyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == logging.DEBUG

def truncate_log_file(log_file: str, max_bytes: int):
    if os.path.isfile(log_file):
        size = os.path.getsize(log_file)
        if size > max_bytes:
            with open(log_file, "rb") as f:
                f.seek(-max_bytes, os.SEEK_END)
                data = f.read()
            with open(log_file, "wb") as f:
                f.write(data)

def setup_logger(
    name: str = "openai.agents",
    *,
    max_bytes: int = 10 * 1024 * 1024,
    log_file: Optional[str] = None,
    level: str
) -> logging.Logger:
    # Default log path if none provided
    if not log_file:
        log_file = os.path.join("log", "client-log.log")

    if level is None:
        level = 'DEBUG'

    # Ensure directory exists
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)

    truncate_log_file(log_file, max_bytes)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.DEBUG))
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
