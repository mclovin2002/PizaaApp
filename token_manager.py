from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Tuple


def _load(tokens_file: Path) -> dict:
    if not tokens_file.exists():
        return {}
    try:
        return json.loads(tokens_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(tokens_file: Path, data: dict) -> None:
    tokens_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _current_month_str() -> str:
    now = datetime.now()
    return f"{now.year:04d}-{now.month:02d}"


def get_tokens(tokens_file: str = "tokens.json", monthly_limit: int = 500) -> Tuple[int, int]:
    """Return (tokens_left, monthly_limit). Ensures monthly reset."""
    p = Path(tokens_file)
    data = _load(p)
    month = _current_month_str()
    if data.get("month") != month:
        data = {"month": month, "tokens_left": monthly_limit}
        _save(p, data)
        return monthly_limit, monthly_limit
    left = data.get("tokens_left", monthly_limit)
    return int(left), int(monthly_limit)


def consume_tokens(n: int = 1, tokens_file: str = "tokens.json", monthly_limit: int = 500) -> bool:
    """Consume n tokens if available. Returns True on success, False if not enough tokens."""
    p = Path(tokens_file)
    data = _load(p)
    month = _current_month_str()
    if data.get("month") != month:
        data = {"month": month, "tokens_left": monthly_limit}
    left = int(data.get("tokens_left", monthly_limit))
    if left < n:
        return False
    data["tokens_left"] = left - n
    _save(p, data)
    return True


def refill_monthly(tokens_file: str = "tokens.json", monthly_limit: int = 500) -> None:
    p = Path(tokens_file)
    data = {"month": _current_month_str(), "tokens_left": monthly_limit}
    _save(p, data)
