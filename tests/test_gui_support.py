"""GUI adapters tested without importing Tkinter or opening a window."""

from dataclasses import replace
from datetime import date

import pytest

from fitfor.gui_support import (
    dashboard_data, delete_record, meal_from_form, volume_text, workout_from_form,
)
from fitfor.models import Meal, Workout
from fitfor.storage import Storage


@pytest.fixture
def workout_fields():
    return {
        "log_date": "2026-10-23", "exercise": " Sample press ",
        "sets": "3", "reps": "8", "weight_kg": "12.5", "notes": " Sample ",
    }


def test_workout_form_converts_strings_into_existing_model(workout_fields):
    assert workout_from_form(workout_fields) == Workout(
        date(2026, 10, 23), "Sample press", 3, 8, 12.5, notes="Sample",
    )


def test_workout_form_keeps_optional_fields_optional(workout_fields):
    workout_fields.pop("weight_kg")
    workout_fields.pop("notes")
    workout = workout_from_form(workout_fields)

    assert workout.weight_kg is None
    assert workout.notes == ""


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [("log_date", "2026-02-29", "Date"), ("exercise", " ", "Exercise"),
     ("sets", "-1", "Sets"), ("reps", "word", "Reps"),
     ("weight_kg", "-1", "Weight")],
)
def test_workout_form_uses_shared_validation(
    workout_fields, field, value, message,
):
    workout_fields[field] = value
    with pytest.raises(ValueError, match=message):
        workout_from_form(workout_fields)


def test_cancelled_gui_delete_preserves_records(tmp_path):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(Workout(
        date(2026, 10, 23), "Sample press", 3, 8, 12.5,
    ))
    seen = []

    def cancel(target):
        seen.append(target)
        return False

    assert delete_record(storage, "workout", saved.id, cancel) is False
    assert seen == [saved]
    assert storage.load_workouts() == [saved]


def test_confirmed_gui_delete_targets_only_selected_record(tmp_path):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(Workout(
        date(2026, 10, 23), "Sample press", 3, 8, 12.5,
    ))
    other = storage.add_workout(replace(saved, exercise="Other sample"))
    meal = storage.add_meal(Meal(
        date(2026, 10, 23), "lunch", "Sample food", 100, 10.0,
    ))

    assert delete_record(storage, "workout", saved.id, lambda target: True)
    assert storage.load_workouts() == [other]
    assert storage.load_meals() == [meal]


def test_stale_gui_selection_is_not_deleted(tmp_path):
    storage = Storage(tmp_path / "records.json")
    old = storage.add_workout(Workout(date(2026, 10, 23), "Old sample", 1, 1))
    storage.delete_workout(old.id)
    current = storage.add_workout(replace(old, exercise="New sample"))
    seen = []

    with pytest.raises(ValueError, match="changed"):
        delete_record(storage, "workout", old.id,
                      lambda target: seen.append(target), expected=old)
    assert seen == []
    assert storage.load_workouts() == [current]


def test_record_changed_during_confirmation_is_preserved(tmp_path):
    storage = Storage(tmp_path / "records.json")
    old = storage.add_workout(Workout(date(2026, 10, 23), "Old sample", 1, 1))

    def change_during_confirmation(target):
        storage.delete_workout(target.id)
        storage.add_workout(replace(target, exercise="New sample"))
        return True

    with pytest.raises(ValueError, match="during confirmation"):
        delete_record(storage, "workout", old.id, change_during_confirmation)
    assert storage.load_workouts()[0].exercise == "New sample"


def test_missing_gui_target_is_reported(tmp_path):
    with pytest.raises(ValueError, match="no longer available"):
        delete_record(Storage(tmp_path / "records.json"), "workout", 1,
                      lambda target: True)


def test_truthy_non_boolean_is_not_confirmation(tmp_path):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(Workout(date(2026, 10, 23), "Sample", 1, 1))

    assert delete_record(storage, "workout", saved.id,
                         lambda target: "yes") is False
    assert storage.load_workouts() == [saved]


@pytest.mark.parametrize(
    ("weight", "expected"), [(None, "-"), (0.0, "0.00"), (12.5, "300.00")],
)
def test_gui_volume_display_uses_the_model_property(weight, expected):
    assert volume_text(Workout(date(2026, 10, 23), "Sample", 3, 8, weight)) == (
        expected
    )


@pytest.mark.parametrize(("sets", "weight"), [(3, 1e308), (10 ** 400, 1.0)])
def test_gui_volume_display_handles_overflow(sets, weight):
    assert volume_text(Workout(
        date(2026, 10, 23), "Sample", sets, 8, weight,
    )) == "Out of range"


@pytest.fixture
def meal_fields():
    return {
        "log_date": "2026-10-23", "meal_type": " lunch ", "food": " Sample bowl ",
        "calories": "520", "protein_g": "35.5", "carbs_g": "60", "fat_g": "15",
        "notes": " synthetic ",
    }


def test_meal_form_round_trips_through_shared_storage(tmp_path, meal_fields):
    storage = Storage(tmp_path / "records.json")
    meal = meal_from_form(meal_fields)
    assert meal == Meal(date(2026, 10, 23), "lunch", "Sample bowl", 520, 35.5,
                        carbs_g=60.0, fat_g=15.0, notes="synthetic")
    saved = storage.add_meal(meal)
    assert storage.load_meals() == [saved]


@pytest.mark.parametrize(("field", "value", "message"), [
    ("log_date", "23/10/2026", "Date"), ("meal_type", " ", "Meal type"),
    ("food", " ", "Food"), ("calories", "-1", "Calories"),
    ("calories", "2.5", "Calories"), ("protein_g", "-1", "Protein"),
    ("carbs_g", "nan", "Carbohydrates"), ("fat_g", "-1", "Fat"),
])
def test_meal_form_uses_shared_validation(meal_fields, field, value, message):
    meal_fields[field] = value
    with pytest.raises(ValueError, match=message):
        meal_from_form(meal_fields)


@pytest.mark.parametrize("confirmed", [False, True])
def test_gui_meal_deletion_keeps_other_records(tmp_path, confirmed):
    storage = Storage(tmp_path / "records.json")
    first = storage.add_meal(Meal(date(2026, 10, 23), "lunch", "Sample", 100, 10))
    other = storage.add_meal(replace(first, food="Other sample"))
    workout = storage.add_workout(Workout(date(2026, 10, 23), "Sample", 1, 1))
    assert delete_record(storage, "meal", first.id, lambda target: confirmed) is confirmed
    assert storage.load_meals() == ([other] if confirmed else [first, other])
    assert storage.load_workouts() == [workout]


def test_empty_dashboard_has_zero_totals_and_no_activity():
    data = dashboard_data([], [], today=date(2026, 10, 23))
    assert data["workouts"]["workout_entries"] == 0
    assert data["workouts"]["recorded_volume"] == 0.0
    assert data["nutrition"]["total_calories"] == 0
    assert data["recent"] == []


def test_dashboard_uses_all_workouts_but_only_todays_nutrition():
    today = date(2026, 10, 23)
    old = date(2026, 10, 22)
    workouts = [Workout(old, "Sample", 3, 8, 12.5), Workout(today, "Sample", 2, 5)]
    meals = [Meal(old, "lunch", "Old sample", 100, 10),
             Meal(today, "lunch", "Current sample", 520, 35, carbs_g=60, fat_g=15)]
    data = dashboard_data(workouts, meals, today=today)
    assert data["workouts"]["workout_entries"] == 2
    assert data["workouts"]["total_sets"] == 5
    assert data["workouts"]["total_reps"] == 34
    assert data["workouts"]["recorded_volume"] == 300
    assert data["nutrition"] == {
        "meal_entries": 1, "total_calories": 520, "total_protein_g": 35.0,
        "total_carbs_g": 60.0, "total_fat_g": 15.0,
    }
    assert [row[0] for row in data["recent"]] == [today, today, old, old]


def test_dashboard_limits_recent_activity_without_mutating_source():
    workouts = [Workout(date(2026, 10, day), f"Sample {day}", 1, 1) for day in range(1, 15)]
    data = dashboard_data(workouts, [], today=date(2026, 10, 23))
    assert len(data["recent"]) == 8
    assert data["recent"][0][2] == "Sample 14"
    assert workouts[0].exercise == "Sample 1"
