import json
import logging
import sys
import traceback
from pathlib import Path

from loguru import logger

from core.config import settings
from core.logging.intercept import InterceptHandler

UVICORN_LOGGERS = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "fastapi",
)


def _ensure_correlation_id(record: dict) -> None:
    from asgi_correlation_id import correlation_id

    cid = correlation_id.get()
    if cid:
        record["extra"]["correlation_id"] = cid
    else:
        record["extra"].setdefault("correlation_id", "-")


def _json_sink_format(record: dict) -> str:
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "file": record["file"].name,
        "function": record["function"],
        "line": record["line"],
        "extra": dict(record["extra"]),
    }

    exception = record["exception"]
    if exception is not None:
        payload["exception"] = {
            "type": exception.type.__name__ if exception.type else None,
            "value": str(exception.value) if exception.value else None,
            "traceback": "".join(
                traceback.format_exception(
                    exception.type,
                    exception.value,
                    exception.traceback,
                )
            ),
        }

    # Returned string is a Loguru format template; escape braces so JSON
    # survives formatting ({{ -> {) without being treated as fields.
    return (
        json.dumps(payload, ensure_ascii=False, default=str)
        .replace("{", "{{")
        .replace("}", "}}")
        + "\n"
    )


def setup_logging() -> None:
    logger.remove()
    logger.configure(patcher=_ensure_correlation_id)

    level = settings.LOG_LEVEL.upper()

    logger.add(
        sys.stderr,
        level=level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> | "
            "cid={extra[correlation_id]} | "
            "<level>{message}</level>"
        ),
    )

    log_dir = Path(settings.LOG_DIR)
    if not log_dir.is_absolute():
        # Resolve relative to the app package root (…/app)
        log_dir = Path(__file__).resolve().parents[2] / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_dir / "app.jsonl",
        level=level,
        enqueue=True,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        format=_json_sink_format,
        backtrace=True,
        diagnose=False,
    )

    intercept_handler = InterceptHandler()
    logging.basicConfig(
        handlers=[intercept_handler],
        level=0,
        force=True,
    )

    for name in UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = [intercept_handler]
        uvicorn_logger.propagate = False
        uvicorn_logger.setLevel(logging.INFO)
