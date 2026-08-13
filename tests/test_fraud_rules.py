from src.fraud_rules import (
    calculate_risk_score,
    clamp,
    deduplicate_transactions,
    risk_level_from_score,
    standardize_category,
    standardize_location,
    validate_transaction,
)


def test_risk_score_clamps_to_bounds():
    assert clamp(-5, 0, 100) == 0
    assert clamp(120, 0, 100) == 100


def test_risk_level_boundaries():
    assert risk_level_from_score(0) == "LOW"
    assert risk_level_from_score(30) == "LOW"
    assert risk_level_from_score(31) == "MEDIUM"
    assert risk_level_from_score(70) == "MEDIUM"
    assert risk_level_from_score(71) == "HIGH"
    assert risk_level_from_score(100) == "HIGH"


def test_risk_score_calculation():
    payload = {
        "high_amount_flag": True,
        "velocity_flag": True,
        "location_hop_flag": True,
        "unusual_hour_flag": True,
        "amount_deviation_flag": True,
        "merchant_frequency_flag": True,
    }
    result = calculate_risk_score(payload)
    assert result["risk_score"] == 100
    assert result["risk_level"] == "HIGH"
    assert len(result["triggered_rules"]) == 6


def test_amount_validation_rejects_invalid_values():
    valid, errors = validate_transaction({
        "transaction_id": "T1",
        "customer_id": "C1",
        "card_id": "CARD1",
        "amount": 0,
        "transaction_time": "2026-04-30 10:00:00",
        "merchant_category": "Food",
        "location": "Delhi",
    })
    assert not valid
    assert "amount_invalid" in errors


def test_duplicate_handling_keeps_last_value():
    rows = [
        {"transaction_id": "T1", "amount": 100},
        {"transaction_id": "T1", "amount": 200},
        {"transaction_id": "T2", "amount": 300},
    ]
    deduped = deduplicate_transactions(rows)
    assert len(deduped) == 2
    assert {row["transaction_id"] for row in deduped} == {"T1", "T2"}
    assert deduped[0]["amount"] == 200


def test_category_and_location_normalization():
    assert standardize_category("  E-commerce ") == "e-commerce"
    assert standardize_location("bangalore") == "Bengaluru"
    assert standardize_location("delhi") == "Delhi"
