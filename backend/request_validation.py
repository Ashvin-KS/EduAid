from typing import Any, Iterable

from flask import Request
from werkzeug.exceptions import BadRequest


def json_error(message: str, status: int = 400) -> tuple[dict[str, Any], int]:
    return {"error": message, "status": status}, status


def parse_json_body(
    request: Request,
    required_fields: Iterable[str] | None = None,
) -> tuple[dict[str, Any] | None, tuple[dict[str, Any], int] | None]:
    if not request.is_json:
        return None, json_error("Request must be JSON", 400)

    try:
        data = request.get_json(silent=False)
    except BadRequest:
        return None, json_error("Malformed JSON payload", 400)

    if data is None:
        return None, json_error("JSON body cannot be empty", 400)

    if not isinstance(data, dict):
        return None, json_error("JSON body must be an object", 400)

    if not data:
        return None, json_error("JSON body cannot be empty", 400)

    required = list(required_fields or [])
    missing_fields = [field for field in required if field not in data]
    if missing_fields:
        return None, json_error(
            f"Missing required field(s): {', '.join(missing_fields)}",
            400,
        )

    return data, None