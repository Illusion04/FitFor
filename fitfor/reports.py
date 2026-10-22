"""Pure calculations over recorded entries, with inclusive date filtering."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from math import fsum, isfinite
from typing import TypeVar

from fitfor.models import Meal, Workout

Entry = TypeVar("Entry", Workout, Meal)


def _rounded_total(values: Iterable[float]) -> float:
    message = "Recorded total exceeds the supported numeric range."
    try:
        total = fsum(values)
    except OverflowError:
        raise ValueError(message) from None
    if not isfinite(total):
        raise ValueError(message)
    return round(total, 2)


def _in_period(
    entries: Iterable[Entry], start: date | None, end: date | None,
) -> list[Entry]:
    if start is not None and end is not None and start > end:
        raise ValueError("Start date must be on or before end date.")
    return [entry for entry in entries
            if (start is None or entry.log_date >= start)
            and (end is None or entry.log_date <= end)]


def workout_summary(
    workouts: Iterable[Workout],
    start: date | None = None,
    end: date | None = None,
) -> dict[str, int | float]:
    """Summarise exercise entries; recorded volume excludes unknown loads."""
    entries = _in_period(workouts, start, end)
    try:
        volumes = [entry.volume for entry in entries if entry.volume is not None]
    except OverflowError:
        raise ValueError(
            "Recorded volume exceeds the supported numeric range."
        ) from None
    return {
        "workout_entries": len(entries),
        "workout_days": len({entry.log_date for entry in entries}),
        "unique_exercises": len({entry.exercise.casefold() for entry in entries}),
        "total_sets": sum(entry.sets for entry in entries),
        "total_reps": sum(entry.sets * entry.reps for entry in entries),
        "entries_with_load": len(volumes),
        "entries_without_load": len(entries) - len(volumes),
        "recorded_volume": _rounded_total(volumes),
    }


def nutrition_summary(
    meals: Iterable[Meal],
    start: date | None = None,
    end: date | None = None,
) -> dict[str, int | float]:
    """Total recorded kcal and grams of nutrients, rounded to two decimals."""
    entries = _in_period(meals, start, end)
    return {
        "meal_entries": len(entries),
        "total_calories": sum(entry.calories for entry in entries),
        "total_protein_g": _rounded_total(entry.protein_g for entry in entries),
        "total_carbs_g": _rounded_total(entry.carbs_g for entry in entries),
        "total_fat_g": _rounded_total(entry.fat_g for entry in entries),
    }


def daily_nutrition_summary(
    meals: Iterable[Meal],
    start: date | None = None,
    end: date | None = None,
) -> dict[date, dict[str, int | float]]:
    """Return nutrition totals by recorded day in ascending date order."""
    grouped = defaultdict(list)
    for meal in _in_period(meals, start, end):
        grouped[meal.log_date].append(meal)
    return {day: nutrition_summary(grouped[day]) for day in sorted(grouped)}
