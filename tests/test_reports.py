"""Report calculations checked against known synthetic totals."""

from datetime import date

import pytest

from fitfor.models import Meal, Workout
from fitfor.reports import (
    daily_nutrition_summary,
    nutrition_summary,
    workout_summary,
)


@pytest.fixture
def workouts():
    return [
        Workout(date(2026, 10, 20), "Sample press", 3, 8, 12.5),
        Workout(date(2026, 10, 22), "sample PRESS", 2, 5, 20.0),
        Workout(date(2026, 10, 22), "Sample bodyweight", 2, 10),
    ]


@pytest.fixture
def meals():
    return [
        Meal(date(2026, 10, 20), "breakfast", "Sample oats", 200, 10.0,
             carbs_g=30.0, fat_g=5.0),
        Meal(date(2026, 10, 22), "lunch", "Sample wrap", 520, 35.0,
             carbs_g=60.5, fat_g=15.0),
        Meal(date(2026, 10, 22), "snack", "Sample snack", 100, 5.0,
             carbs_g=10.25, fat_g=2.5),
    ]


def test_workout_totals_distinguish_entries_days_and_unknown_loads(workouts):
    assert workout_summary(workouts) == {
        "workout_entries": 3,
        "workout_days": 2,
        "unique_exercises": 2,
        "total_sets": 7,
        "total_reps": 54,
        "entries_with_load": 2,
        "entries_without_load": 1,
        "recorded_volume": 500.0,
    }


def test_empty_workouts_have_zero_totals():
    summary = workout_summary([])

    assert summary
    assert all(value == 0 for value in summary.values())


def test_workout_date_range_is_inclusive(workouts):
    summary = workout_summary(workouts, date(2026, 10, 22), date(2026, 10, 22))

    assert summary["workout_entries"] == 2
    assert summary["total_sets"] == 4
    assert summary["total_reps"] == 30
    assert summary["recorded_volume"] == 200.0


def test_open_ended_workout_ranges(workouts):
    assert workout_summary(workouts, end=date(2026, 10, 20))[
        "workout_entries"
    ] == 1
    assert workout_summary(workouts, start=date(2026, 10, 23))[
        "workout_entries"
    ] == 0


def test_recorded_zero_load_is_not_a_missing_load():
    summary = workout_summary([
        Workout(date(2026, 10, 22), "Sample exercise", 2, 10, 0.0),
    ])

    assert summary["entries_with_load"] == 1
    assert summary["entries_without_load"] == 0
    assert summary["recorded_volume"] == 0.0


def test_nutrition_totals(meals):
    assert nutrition_summary(meals) == {
        "meal_entries": 3,
        "total_calories": 820,
        "total_protein_g": 50.0,
        "total_carbs_g": 100.75,
        "total_fat_g": 22.5,
    }


def test_empty_meals_have_zero_totals_and_no_days():
    assert nutrition_summary([]) == {
        "meal_entries": 0,
        "total_calories": 0,
        "total_protein_g": 0.0,
        "total_carbs_g": 0.0,
        "total_fat_g": 0.0,
    }
    assert daily_nutrition_summary([]) == {}


def test_daily_totals_are_correct_and_sorted(meals):
    summary = daily_nutrition_summary(reversed(meals))

    assert list(summary) == [date(2026, 10, 20), date(2026, 10, 22)]
    assert summary[date(2026, 10, 22)] == {
        "meal_entries": 2,
        "total_calories": 620,
        "total_protein_g": 40.0,
        "total_carbs_g": 70.75,
        "total_fat_g": 17.5,
    }


def test_nutrition_date_range_is_inclusive(meals):
    start = end = date(2026, 10, 20)

    assert nutrition_summary(meals, start, end)["total_calories"] == 200
    assert list(daily_nutrition_summary(meals, start, end)) == [start]


@pytest.mark.parametrize(
    "report", [workout_summary, nutrition_summary, daily_nutrition_summary],
)
def test_reversed_date_ranges_are_rejected(report):
    with pytest.raises(ValueError, match="Start date"):
        report([], date(2026, 10, 22), date(2026, 10, 20))


def test_fractional_nutrients_are_rounded_at_the_total():
    meals = [Meal(date(2026, 10, 22), "snack", "Sample food", 0, value)
             for value in (0.1, 0.2)]

    assert nutrition_summary(meals)["total_protein_g"] == 0.3


def test_generators_are_consumed_only_once(workouts, meals):
    assert workout_summary(iter(workouts)) == workout_summary(workouts)
    assert nutrition_summary(iter(meals)) == nutrition_summary(meals)


@pytest.mark.parametrize("weight", [1e308, 1.0])
def test_overflowing_workout_volume_has_a_clear_error(weight):
    sets = 3 if weight == 1e308 else 10 ** 400
    entries = [Workout(date(2026, 10, 22), "Sample exercise", sets, 8, weight)]

    with pytest.raises(ValueError, match="numeric range"):
        workout_summary(entries)


@pytest.mark.parametrize(
    "report", [nutrition_summary, daily_nutrition_summary],
)
def test_overflowing_nutrient_totals_have_a_clear_error(report):
    entries = [Meal(date(2026, 10, 22), "snack", "Sample food", 0, 1e308)
               for _ in range(2)]

    with pytest.raises(ValueError, match="numeric range"):
        report(entries)
