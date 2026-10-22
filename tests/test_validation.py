"""Boundary cases for reusable validation, using synthetic input only."""

from datetime import date

import pytest

from fitfor.validation import (
    validate_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_positive_int,
    validate_text,
    validate_weight,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("2024-02-29", date(2024, 2, 29)),
     (" 2026-10-22 ", date(2026, 10, 22))],
)
def test_valid_dates(value, expected):
    assert validate_date(value) == expected


@pytest.mark.parametrize(
    "value",
    ["", " ", "2026-02-29", "2026-13-01", "2026-00-01", "2026-01-00",
     "2026-04-31", "0000-01-01", "22/10/2026", "2026-1-2", "20261022",
     "2026-W43-4", "2026-10-22T12:00:00", None, 20261022],
)
def test_invalid_dates(value):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date(value)


def test_required_text_is_trimmed():
    assert validate_text("  Sample entry  ", "Exercise") == "Sample entry"


@pytest.mark.parametrize("value", ["", " \t\n", None, 12])
def test_required_text_rejects_missing_or_wrong_types(value):
    with pytest.raises(ValueError, match="Exercise"):
        validate_text(value, "Exercise")


def test_optional_notes_allow_blank_text():
    assert validate_text("  ", "Notes", required=False) == ""
    assert validate_text(" Example ", "Notes", required=False) == "Example"


@pytest.mark.parametrize("value", [1, "1", " +12 "])
def test_positive_integers(value):
    assert validate_positive_int(value, "Sets") == int(value)


@pytest.mark.parametrize(
    "value", [0, "0", -1, "-1", "", " ", "two", "1.5", 1.5, 1.0,
              True, False, None],
)
def test_invalid_positive_integers(value):
    with pytest.raises(ValueError, match="Sets.*positive integer"):
        validate_positive_int(value, "Sets")


@pytest.mark.parametrize("value", [0, "0", 520, " 520 "])
def test_non_negative_integers(value):
    assert validate_non_negative_int(value, "Calories") == int(value)


@pytest.mark.parametrize("value", [-1, "-1", "", "2.5", 2.5, True, None])
def test_invalid_non_negative_integers(value):
    with pytest.raises(ValueError, match="Calories.*non-negative integer"):
        validate_non_negative_int(value, "Calories")


@pytest.mark.parametrize("value", [0, "0", 0.25, " 35.5 ", "1e2"])
def test_non_negative_numbers(value):
    assert validate_non_negative_float(value, "Protein") == float(value)


@pytest.mark.parametrize(
    "value", [-1, "-0.1", "", "word", "nan", "inf", "-inf", "1e999",
              float("nan"), float("inf"), True, None, [],
              pytest.param(10 ** 400, id="overflowing-integer")],
)
def test_invalid_non_negative_numbers(value):
    with pytest.raises(ValueError, match="Protein.*finite, non-negative"):
        validate_non_negative_float(value, "Protein")


@pytest.mark.parametrize("value", [None, "", "  "])
def test_unrecorded_weight(value):
    assert validate_weight(value) is None


def test_zero_and_fractional_weights_are_retained():
    assert validate_weight("0") == 0.0
    assert validate_weight("12.5") == 12.5


@pytest.mark.parametrize("value", ["-1", "nan", "inf", "word", True])
def test_invalid_weights(value):
    with pytest.raises(ValueError, match="Weight"):
        validate_weight(value)
