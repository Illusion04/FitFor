"""Pure calculations over recorded entries, with inclusive date filtering."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from math import fsum
from typing import TypeVar

from fitfor.models import Meal, Workout

Entry = TypeVar("Entry", Workout, Meal)


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
    volumes = [entry.volume for entry in entries if entry.volume is not None]
    return {
        "workout_entries": len(entries),
        "workout_days": len({entry.log_date for entry in entries}),
        "unique_exercises": len({entry.exercise.casefold() for entry in entries}),
        "total_sets": sum(entry.sets for entry in entries),
        "total_reps": sum(entry.sets * entry.reps for entry in entries),
        "entries_with_load": len(volumes),
        "entries_without_load": len(entries) - len(volumes),
        "recorded_volume": round(fsum(volumes), 2),
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
        "total_protein_g": round(fsum(entry.protein_g for entry in entries), 2),
        "total_carbs_g": round(fsum(entry.carbs_g for entry in entries), 2),
        "total_fat_g": round(fsum(entry.fat_g for entry in entries), 2),
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
