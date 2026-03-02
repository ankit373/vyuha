import logging
import sys
from rich.logging import RichHandler

def setup_logger(name: str):
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            RichHandler(rich_tracebacks=True),
            logging.FileHandler("vyuha.log")
        ]
    )
    return logging.getLogger(name)

logger = setup_logger("A2A")
