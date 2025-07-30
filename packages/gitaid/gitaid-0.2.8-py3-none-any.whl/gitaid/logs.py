from loguru import logger
from pathlib import Path
import os
import platform
import sys

def get_log_path():
    if platform.system() == "Windows":
        base = Path(os.getenv("LOCALAPPDATA", "C:/Logs")) / "gitaid"
    else:
        # Use user home directory logs path
        base = Path.home() / ".local" / "share" / "gitaid" / "logs"
    base.mkdir(parents=True, exist_ok=True)
    return base / "gitaid.log"

def setup_logger(verbose: bool = False):
    logger.remove()  # Remove default stderr

    # Log file sink (always DEBUG)
    logger.add(
        str(get_log_path()),
        rotation="1 MB",
        retention="10 days",
        level="DEBUG",
        backtrace=True,
        diagnose=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    # Add console output only if verbose=True
    if verbose:
        logger.add(
            sink=sys.stdout,
            level="INFO",  # Or DEBUG if you want more output on console
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        )
