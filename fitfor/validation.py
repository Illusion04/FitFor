"""Reusable input validation shared by the CLI and storage boundary."""

from datetime import date
import math
import re


def validate_date(value: object) -> date:
    """Parse a real calendar date written as YYYY-MM-DD."""
    message = "Date must be a valid calendar date in YYYY-MM-DD format."
    if not isinstance(value, str):
        raise ValueError(message)
    text = value.strip()
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text) is None:
        raise ValueError(message)
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(message) from None


def validate_text(
    value: object, field_name: str = "Name", *, required: bool = True,
) -> str:
    """Trim text, rejecting a blank value when the field is required."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")
    text = value.strip()
    if required and not text:
        raise ValueError(f"{field_name} cannot be empty.")
    return text


def _validate_integer(value: object, field_name: str, minimum: int) -> int:
    message = (
        f"{field_name} must be a positive integer."
        if minimum == 1
        else f"{field_name} must be a non-negative integer."
    )
    if type(value) is int:
        number = value
    elif isinstance(value, str) and re.fullmatch(
        r"[+-]?[0-9]+", value.strip(),
    ):
        try:
            number = int(value.strip())
        except ValueError:
            raise ValueError(message) from None
    else:
        raise ValueError(message)
    if number < minimum:
        raise ValueError(message)
    return number


def validate_positive_int(value: object, field_name: str = "Value") -> int:
    """Require an integer of at least one, without rounding or truncation."""
    return _validate_integer(value, field_name, 1)


def validate_non_negative_int(value: object, field_name: str = "Value") -> int:
    """Require an integer of at least zero, for example recorded calories."""
    return _validate_integer(value, field_name, 0)


def validate_non_negative_float(
    value: object, field_name: str = "Value",
) -> float:
    """Require a finite number of at least zero, excluding booleans."""
    message = f"{field_name} must be a finite, non-negative number."
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(message)
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise ValueError(message) from None
    if not math.isfinite(number) or number < 0:
        raise ValueError(message)
    return number


def validate_weight(value: object) -> float | None:
    """Allow a blank load; otherwise require finite, non-negative kilograms."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return validate_non_negative_float(value, "Weight (kg)")
