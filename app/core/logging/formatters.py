import json
from typing import Any


def format_log(record: dict[str, Any]) -> str:
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        **record["extra"],
    }

    return json.dumps(
        log_data,
        ensure_ascii=False,
        indent=4,
        default=str,
    )
