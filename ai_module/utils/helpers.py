from datetime import date
from typing import Optional


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    if denominator is None or denominator == 0:
        return default
    return numerator / denominator


def calculate_amount_paid_percent(
    amount_paid: float,
    sanctioned_cost: float,
) -> float:
    return round(safe_divide(amount_paid, sanctioned_cost) * 100, 2)


def calculate_days_since(
    value_date: Optional[date],
    reference_date: Optional[date] = None,
) -> Optional[int]:
    if value_date is None:
        return None

    reference_date = reference_date or date.today()
    return (reference_date - value_date).days