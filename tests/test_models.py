"""Model behaviour checked using synthetic entries only."""

from datetime import date

import pytest

from fitfor.models import Meal, Workout


def test_workout_creation():
    workout = Workout(date(2026, 10, 22), "Sample press", 3, 8, 12.5)

    assert workout.log_date == date(2026, 10, 22)
    assert workout.exercise == "Sample press"
    assert workout.sets == 3
    assert workout.reps == 8
    assert workout.weight_kg == 12.5
    assert workout.id is None
    assert workout.notes == ""


def test_workout_accepts_an_id_and_notes():
    workout = Workout(
        date(2026, 10, 22), "Sample press", 3, 8, 12.5,
        id=7, notes="Synthetic entry",
    )

    assert workout.id == 7
    assert workout.notes == "Synthetic entry"


@pytest.mark.parametrize(
    ("sets", "reps", "weight", "expected"),
    [(3, 8, 12.5, 300.0), (2, 4, 0.25, 2.0), (1, 10, 0.0, 0.0)],
)
def test_volume_uses_sets_reps_and_recorded_load(sets, reps, weight, expected):
    workout = Workout(date(2026, 10, 22), "Sample press", sets, reps, weight)

    assert workout.volume == expected


def test_volume_recalculates_after_an_input_changes():
    workout = Workout(date(2026, 10, 22), "Sample press", 3, 8, 12.5)

    workout.reps = 10

    assert workout.volume == 375.0


def test_volume_is_read_only():
    workout = Workout(date(2026, 10, 22), "Sample press", 3, 8, 12.5)

    with pytest.raises(AttributeError):
        workout.volume = 5


def test_workout_without_a_recorded_load_has_no_volume():
    workout = Workout(date(2026, 10, 22), "Sample bodyweight exercise", 2, 10)

    assert workout.weight_kg is None
    assert workout.volume is None


def test_meal_creation_with_default_optional_fields():
    meal = Meal(date(2026, 10, 22), "lunch", "Sample wrap", 520, 35.0)

    assert meal.log_date == date(2026, 10, 22)
    assert meal.meal_type == "lunch"
    assert meal.food == "Sample wrap"
    assert meal.calories == 520
    assert meal.protein_g == 35.0
    assert meal.id is None
    assert meal.carbs_g == 0.0
    assert meal.fat_g == 0.0
    assert meal.notes == ""


def test_meal_accepts_all_nutrients_an_id_and_notes():
    meal = Meal(
        date(2026, 10, 22), "lunch", "Sample wrap", 520, 35.0,
        id=7, carbs_g=60.5, fat_g=15.0, notes="Synthetic entry",
    )

    assert meal.id == 7
    assert meal.carbs_g == 60.5
    assert meal.fat_g == 15.0
    assert meal.notes == "Synthetic entry"
