

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

_CURRENCY_SYMBOLS = ("$", "€", "£", "¥", "USD", "EUR", "GBP", "INR")
_NULL_TOKENS = {"", "na", "n/a", "nan", "none", "null", "-"}

def _clean_number(value: Any) -> str:

    text = str(value).strip()
    for symbol in _CURRENCY_SYMBOLS:
        text = text.replace(symbol, "")
    text = text.strip()
    if re.fullmatch(r"\d{1,3}(,\d{3})+\.?\d*", text):
        text = text.replace(",", "")
    elif re.fullmatch(r"\d+,\d{1,2}", text):
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    return text

def _is_bad_float(value: float) -> bool:
    return value != value or value in (float("inf"), float("-inf"))

def to_float(value: Any, default: float = 0.0) -> float:

    if value is None:
        return default
    if isinstance(value, float) and _is_bad_float(value):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = _clean_number(value)
    if text.lower() in _NULL_TOKENS:
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default

def to_int(value: Any, default: int = 0) -> int:

    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float) and _is_bad_float(value):
        return default
    if isinstance(value, (int, float)):
        return int(value)
    text = _clean_number(value)
    if text.lower() in _NULL_TOKENS:
        return default
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default

def normalize_text(value: Any) -> str:

    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in _NULL_TOKENS:
        return ""
    return " ".join(text.split())

def is_valid_email(value: Any) -> bool:

    if value is None:
        return False
    email = str(value).strip()
    if not email or email.count("@") != 1:
        return False
    local, _, domain = email.partition("@")
    if not local or not domain or "." not in domain:
        return False
    if any(char.isspace() for char in email):
        return False
    return True

def write_frame(frame: pd.DataFrame, path: Path, index: bool = False) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=index, encoding="utf-8")
    logger.info("Wrote %s rows to %s", len(frame), path)

def read_frame(path: Path, **kwargs: Any) -> pd.DataFrame:

    return pd.read_csv(path, encoding="utf-8", **kwargs)
