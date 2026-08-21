# Logging Flow & Structure

## Flow (one request)

```text
CorrelationIdMiddleware
  → sets / reads X-Request-ID (ContextVar + request header)

CorrelationIdLoggingMiddleware
  → restores correlation_id (ContextVar may be lost inside BaseHTTPMiddleware)
  → logger.contextualize(correlation_id=...)

Service / use-case (optional, 0..n)
  → short business-step logs via logger.bind(...).info("...")

RequestLoggingMiddleware
  → success: one HTTP audit log
  → unhandled error: one HTTP failed log + return 500 (do not re-raise)
```

Search all events for a request with `extra.correlation_id` / `X-Request-ID`.

---

## Where to log

| Layer | What | Count |
|-------|------|-------|
| Correlation middlewares | Context only (no event) | — |
| Service / use-case | Important decisions & side effects | 0..n |
| Request logging middleware | HTTP completed / failed | 1 |
| Router / repository | Usually nothing | — |

---

## Output shape (NDJSON / `app.jsonl`)

```json
{
  "timestamp": "ISO-8601",
  "level": "INFO",
  "logger": "module.name",
  "message": "stable short text",
  "file": "...",
  "function": "...",
  "line": 1,
  "extra": {
    "correlation_id": "<id>",
    "event": "<event_name>",
    "...": "structured fields"
  }
}
```

Rules:

- Put details in `extra` with `logger.bind(...)`, not in the message string.
- Never: `logger.info("...", key=value)` (Loguru treats kwargs as format args).
- Mask secrets in headers (`authorization`, `cookie`, …).

---

## Event types

### 1) HTTP audit (middleware)

```python
logger.bind(
    correlation_id=cid,  # explicit bind; do not rely on context alone after call_next
    event="http_request_completed",  # or http_request_failed
    method="POST",
    path="/api/v1/...",
    query=None,
    status=201,
    response_time_ms=24.5,
    client_ip="127.0.0.1",
    # request_headers / response_headers: writes or status >= 400
).info("HTTP request")
```

On unhandled 500: log once with `.exception(...)`, return JSON 500, **do not re-raise** (avoids Uvicorn duplicate traceback). `X-Request-ID` is attached on the way out.

### 2) Business step (service)

```python
logger.bind(
    event="task_created",
    operation="tasks.create",
    task_id=1,
    user_id=42,
).info("Task created")
```

Keep it short. Do not repeat full HTTP request/response payloads.

### 3) Error

```python
logger.bind(
    event="task_create_failed",
    operation="tasks.create",
    user_id=42,
).exception("Task create failed")
```

Use `request.state.exception_logged` so middleware and `unhandled_exception_handler` do not both emit a full traceback.
