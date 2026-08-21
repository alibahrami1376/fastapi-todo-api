import json
import traceback
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def json_sink(message):
    record = message.record

    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "file": record["file"].name,
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"],
    }

    exception = record["exception"]

    if exception:
        log_data["exception"] = {
            "type": exception.type.__name__,
            "value": str(exception.value),
            "traceback": "".join(
                traceback.format_exception(
                    exception.type,
                    exception.value,
                    exception.traceback,
                )
            ),
        }

    with open(
        LOG_DIR / "app.log",
        "a",
        encoding="utf-8",
    ) as file:
        json.dump(
            log_data,
            file,
            ensure_ascii=False,
            indent=4,
            default=str,
        )
        file.write("\n\n")
