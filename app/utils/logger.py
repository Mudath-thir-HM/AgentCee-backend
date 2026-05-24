import logging
import sys
from functools import lru_cache


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s:%(lineno)d | %(message)s"
)


@lru_cache
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger


logger = get_logger("AgentCee")
