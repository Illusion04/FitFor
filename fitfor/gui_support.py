"""Headless adapters for desktop forms and confirmation-driven actions."""

from collections.abc import Callable, Mapping
from datetime import date
from math import isfinite
from typing import Literal

from fitfor.models import Meal, Workout
from fitfor.reports import nutrition_summary, workout_summary
from fitfor.storage import Storage
from fitfor.validation import (
    validate_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_positive_int,
    validate_text,
    validate_weight,
)


def workout_from_form(values: Mapping[str, str]) -> Workout:
    """Convert GUI text through the same validators used by the CLI."""
    return Workout(
        log_date=validate_date(values.get("log_date", "")),
        exercise=validate_text(values.get("exercise", ""), "Exercise"),
        sets=validate_positive_int(values.get("sets", ""), "Sets"),
        reps=validate_positive_int(values.get("reps", ""), "Reps"),
        weight_kg=validate_weight(values.get("weight_kg", "")),
        notes=validate_text(values.get("notes", ""), "Notes", required=False),
    )


def volume_text(workout: Workout) -> str:
    """Format the model's property without crashing on extreme records."""
    try:
        volume = workout.volume
    except OverflowError:
        return "Out of range"
    if volume is None:
        return "-"
    return f"{volume:,.2f}" if isfinite(volume) else "Out of range"


def meal_from_form(values: Mapping[str, str]) -> Meal:
    """Build the existing meal model using shared numeric and text rules."""
    return Meal(
        log_date=validate_date(values.get("log_date", "")),
        meal_type=validate_text(values.get("meal_type", ""), "Meal type"),
        food=validate_text(values.get("food", ""), "Food"),
        calories=validate_non_negative_int(values.get("calories", ""), "Calories"),
        protein_g=validate_non_negative_float(values.get("protein_g", ""), "Protein"),
        carbs_g=validate_non_negative_float(values.get("carbs_g", "0"), "Carbohydrates"),
        fat_g=validate_non_negative_float(values.get("fat_g", "0"), "Fat"),
        notes=validate_text(values.get("notes", ""), "Notes", required=False),
    )


def dashboard_data(
    workouts: list[Workout], meals: list[Meal], *, today: date,
) -> dict:
    """Combine existing summaries with the eight most recent dated entries."""
    recent = [
        (entry.log_date, "Workout", entry.exercise, entry.id or 0)
        for entry in workouts
    ] + [
        (entry.log_date, "Meal", entry.food, entry.id or 0) for entry in meals
    ]
    recent.sort(key=lambda row: (row[0], row[3]), reverse=True)
    return {
        "workouts": workout_summary(workouts),
        "nutrition": nutrition_summary(meals, today, today),
        "recent": recent[:8],
    }


def delete_record(
    storage: Storage,
    kind: Literal["workout", "meal"],
    identifier: int,
    confirm: Callable[[Workout | Meal], bool],
    *,
    expected: Workout | Meal | None = None,
) -> bool:
    """Delete only a current target that receives explicit confirmation."""
    if kind not in ("workout", "meal"):
        raise ValueError("Unknown record type.")
    identifier = validate_positive_int(identifier, "ID")
    load = storage.load_workouts if kind == "workout" else storage.load_meals
    delete = (storage.delete_workout if kind == "workout"
              else storage.delete_meal)
    target = next((item for item in load() if item.id == identifier), None)
    if target is None:
        raise ValueError("This record is no longer available. Refresh the list.")
    if expected is not None and target != expected:
        raise ValueError("This record has changed. Refresh before deleting.")
    if confirm(target) is not True:
        return False
    current = next((item for item in load() if item.id == identifier), None)
    if current != target:
        raise ValueError("This record changed during confirmation. Refresh.")
    if not delete(identifier):
        raise ValueError("This record is no longer available. Refresh the list.")
    return True
