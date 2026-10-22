"""Deletion review and privacy guidance tests with synthetic records only."""

from datetime import date

import pytest

from fitfor.cli import Menu
from fitfor.models import Meal, Workout
from fitfor.storage import Storage
from tests.test_cli import run_cli


def seed(storage):
    workout = storage.add_workout(Workout(
        date(2026, 10, 22),
        "Sample exercise with a long descriptive name", 3, 8,
    ))
    meal = storage.add_meal(Meal(
        date(2026, 10, 22), "lunch",
        "Sample food with a long descriptive name", 520, 35.0,
    ))
    return workout, meal


@pytest.mark.parametrize("kind", ["workout", "meal"])
def test_deletion_previews_full_target_before_confirmation(tmp_path, kind):
    storage = Storage(tmp_path / "records.json")
    workout, meal = seed(storage)
    option = "3" if kind == "workout" else "6"
    name = workout.exercise if kind == "workout" else meal.food

    output = run_cli(storage, [option, "1", " Y ", "0"])

    preview = f"2026-10-22 - {name}"
    assert "You are about to permanently delete:" in output
    assert f"{kind.title()} ID 1:" in output
    assert output.index(preview) < output.index("Continue? (y/n):")
    assert storage.load_workouts() == ([] if kind == "workout" else [workout])
    assert storage.load_meals() == ([] if kind == "meal" else [meal])


@pytest.mark.parametrize("answer", ["n", "N", "yes", "", "invalid"])
def test_meal_deletion_cancels_on_every_non_y_response(tmp_path, answer):
    storage = Storage(tmp_path / "records.json")
    workout, meal = seed(storage)

    output = run_cli(storage, ["6", "1", answer, "0"])

    assert "Deletion cancelled." in output
    assert storage.load_workouts() == [workout]
    assert storage.load_meals() == [meal]


@pytest.mark.parametrize("option", ["3", "6"])
@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_interrupted_confirmation_preserves_both_collections(
    tmp_path, option, error_type,
):
    storage = Storage(tmp_path / "records.json")
    workout, meal = seed(storage)
    answers = iter([option, "1"])
    output = []

    def read(prompt):
        output.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise error_type from None

    Menu(storage, read, output.append).run()

    assert "Continue? (y/n): " in output
    assert storage.load_workouts() == [workout]
    assert storage.load_meals() == [meal]


def test_privacy_menu_explains_human_risks_and_actual_limits(tmp_path):
    path = tmp_path / "records.json"

    output = run_cli(Storage(path), ["9", "0"])

    assert "Protect Your Progress" in output
    assert "Review the date, name and ID" in output
    warning = "Avoid passwords, financial details or medical information"
    assert warning in output
    assert "before sharing" in output
    assert "Store backups securely" in output
    assert "not encrypted" in output
    assert "no application login" in output
    assert not path.exists()
