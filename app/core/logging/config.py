import logging
import sys

from loguru import logger

from core.logging.intercept import InterceptHandler
from core.logging.sinks import json_sink


def setup_logging() -> None:
    # Remove Loguru default handler
    logger.remove()

    # Console logs
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # JSON file logs
    logger.add(
        json_sink,
        level="INFO",
        enqueue=True,
    )

    # Redirect standard logging to Loguru
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=0,
        force=True,
    )

    # Redirect Uvicorn logs to Loguru
    for name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = False
