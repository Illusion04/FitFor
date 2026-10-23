"""Headless adapters for desktop forms and confirmation-driven actions."""

from collections.abc import Callable, Mapping
from math import isfinite
from typing import Literal

from fitfor.models import Meal, Workout
from fitfor.storage import Storage
from fitfor.validation import (
    validate_date,
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
