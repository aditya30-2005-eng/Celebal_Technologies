from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(float(value), maximum))


def risk_level_from_score(score: float) -> str:
    numeric_score = clamp(score, 0, 100)
    if numeric_score <= 30:
        return "LOW"
    if numeric_score <= 70:
        return "MEDIUM"
    return "HIGH"


def standardize_category(category: Optional[str]) -> Optional[str]:
    if category is None:
        return None
    cleaned = str(category).strip().lower().replace("_", " ")
    mapping = {
        "e commerce": "e-commerce",
        "e-commerce": "e-commerce",
        "electronics": "electronics",
        "luxury": "luxury",
        "food": "food",
        "shopping": "shopping",
        "groceries": "groceries",
        "travel": "travel",
        "entertainment": "entertainment",
    }
    return mapping.get(cleaned, cleaned)


def standardize_location(location: Optional[str]) -> Optional[str]:
    if location is None:
        return None
    cleaned = str(location).strip()
    mapping = {
        "bangalore": "Bengaluru",
        "bengaluru": "Bengaluru",
        "mumbai": "Mumbai",
        "delhi": "Delhi",
        "jaipur": "Jaipur",
        "hyderabad": "Hyderabad",
        "pune": "Pune",
        "chennai": "Chennai",
        "kolkata": "Kolkata",
        "ahmedabad": "Ahmedabad",
    }
    return mapping.get(cleaned.lower(), cleaned.title())


def validate_transaction(record: Dict[str, object]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not record.get("transaction_id") or not str(record.get("transaction_id")).strip():
        errors.append("transaction_id_missing")
    if not record.get("customer_id") or not str(record.get("customer_id")).strip():
        errors.append("customer_id_missing")
    if not record.get("card_id") or not str(record.get("card_id")).strip():
        errors.append("card_id_missing")
    amount = record.get("amount")
    try:
        if amount is None or float(amount) <= 0:
            errors.append("amount_invalid")
    except (TypeError, ValueError):
        errors.append("amount_invalid")
    if not record.get("transaction_time"):
        errors.append("timestamp_missing")
    if not record.get("merchant_category"):
        errors.append("merchant_category_missing")
    if not record.get("location"):
        errors.append("location_missing")
    return (len(errors) == 0, errors)


def calculate_risk_score(features: Dict[str, object]) -> Dict[str, object]:
    contributions = {
        "high_amount_flag": 25,
        "velocity_flag": 20,
        "location_hop_flag": 20,
        "unusual_hour_flag": 15,
        "amount_deviation_flag": 20,
        "merchant_frequency_flag": 10,
    }
    score = 0.0
    triggered = []
    for flag_name, weight in contributions.items():
        if bool(features.get(flag_name, False)):
            score += weight
            triggered.append(flag_name)
    score = clamp(score, 0, 100)
    return {
        "risk_score": round(score, 2),
        "risk_level": risk_level_from_score(score),
        "triggered_rules": triggered,
    }


def deduplicate_transactions(rows: Iterable[Dict[str, object]], key_field: str = "transaction_id") -> List[Dict[str, object]]:
    deduped: Dict[str, Dict[str, object]] = {}
    for row in rows:
        key = row.get(key_field)
        if key is None:
            continue
        deduped[str(key)] = row
    return list(deduped.values())
