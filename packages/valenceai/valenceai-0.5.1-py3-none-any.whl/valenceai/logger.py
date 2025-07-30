import logging
import os

def get_logger():
    level = os.getenv("VALENCE_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger("valenceai")
