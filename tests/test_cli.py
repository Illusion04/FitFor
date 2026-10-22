"""CLI workflows with supplied input and temporary synthetic storage."""

from datetime import date

import pytest

from fitfor.cli import Menu
from fitfor.models import Meal, Workout
from fitfor.storage import Storage


def run_cli(storage, replies):
    answers = iter(replies)
    output = []

    def read(prompt):
        output.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    Menu(storage, read, output.append).run()
    return "\n".join(output)


def test_workout_add_view_and_report(tmp_path):
    storage = Storage(tmp_path / "records.json")
    output = run_cli(storage, [
        "1", "2026-10-22", "Sample press", "3", "8", "12.5", "Sample note",
        "2", "7", "", "", "0",
    ])

    assert storage.load_workouts() == [Workout(
        date(2026, 10, 22), "Sample press", 3, 8, 12.5,
        id=1, notes="Sample note",
    )]
    assert "Workout saved with ID 1." in output
    assert "Sample press" in output
    assert "Recorded volume (kg x reps): 300.0" in output
    assert "Goodbye." in output


def test_meal_add_view_and_report(tmp_path):
    storage = Storage(tmp_path / "records.json")
    output = run_cli(storage, [
        "4", "2026-10-22", "lunch", "Sample wrap", "520", "35", "60.5",
        "15", "", "5", "8", "", "", "0",
    ])

    assert storage.load_meals() == [Meal(
        date(2026, 10, 22), "lunch", "Sample wrap", 520, 35.0,
        id=1, carbs_g=60.5, fat_g=15.0,
    )]
    assert "Meal saved with ID 1." in output
    assert "Sample wrap" in output
    assert "Total calories (kcal): 520" in output
    assert "2026-10-22: 520 kcal" in output


def test_invalid_menu_choice_returns_to_menu(tmp_path):
    output = run_cli(Storage(tmp_path / "records.json"), ["wrong", "0"])

    assert "Invalid choice" in output
    assert "Goodbye." in output


def test_invalid_workout_fields_are_retried(tmp_path):
    storage = Storage(tmp_path / "records.json")
    output = run_cli(storage, [
        "1", "2026-02-29", "2026-10-22", " ", "Sample exercise",
        "0", "3", "word", "8", "-1", "", "", "0",
    ])

    assert output.count("Invalid input") == 5
    assert len(storage.load_workouts()) == 1
    assert storage.load_workouts()[0].weight_kg is None


@pytest.mark.parametrize("answer", ["n", "yes", "", "invalid"])
def test_workout_deletion_requires_explicit_y(tmp_path, answer):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(
        Workout(date(2026, 10, 22), "Sample exercise", 1, 1, 1.0),
    )
    output = run_cli(storage, ["3", "1", answer, "0"])

    assert storage.load_workouts() == [saved]
    assert "Deletion cancelled." in output


def test_confirmed_meal_deletion(tmp_path):
    storage = Storage(tmp_path / "records.json")
    storage.add_meal(Meal(date(2026, 10, 22), "lunch", "Sample meal", 0, 0.0))

    output = run_cli(storage, ["6", "1", "y", "0"])

    assert storage.load_meals() == []
    assert "Meal deleted." in output


def test_missing_delete_id_does_not_delete_another_entry(tmp_path):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(
        Workout(date(2026, 10, 22), "Sample exercise", 1, 1),
    )

    output = run_cli(storage, ["3", "999", "0"])

    assert "No workout found with ID 999." in output
    assert storage.load_workouts() == [saved]


def test_empty_views_and_reports(tmp_path):
    output = run_cli(Storage(tmp_path / "records.json"), [
        "2", "5", "7", "", "", "8", "", "", "0",
    ])

    assert "No workouts recorded." in output
    assert "No meals recorded." in output
    assert "Exercise entries: 0" in output
    assert "No meals in the selected period." in output


def test_storage_error_is_shown_without_overwriting_file(tmp_path):
    path = tmp_path / "records.json"
    path.write_text("not JSON", encoding="utf-8")

    output = run_cli(Storage(path), ["2", "0"])

    assert "Unable to complete action" in output
    assert "Goodbye." in output
    assert path.read_text(encoding="utf-8") == "not JSON"


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_interrupted_add_does_not_save_a_partial_record(tmp_path, error_type):
    storage = Storage(tmp_path / "records.json")
    answers = iter(["1", "2026-10-22", "Sample exercise"])
    output = []

    def read(prompt):
        try:
            return next(answers)
        except StopIteration:
            raise error_type from None

    Menu(storage, read, output.append).run()

    assert storage.load_workouts() == []
    assert "Exiting FitFor." in "\n".join(output)


def test_meal_fields_retry_invalid_values(tmp_path):
    storage = Storage(tmp_path / "records.json")
    output = run_cli(storage, [
        "4", "2026-10-22", "", "lunch", " ", "Sample wrap",
        "-1", "520", "nan", "35", "-2", "60.5", "inf", "15", "", "0",
    ])

    assert output.count("Invalid input") == 6
    assert len(storage.load_meals()) == 1
    assert storage.load_meals()[0].protein_g == 35.0
    assert storage.load_meals()[0].fat_g == 15.0


def test_report_retries_invalid_dates_and_reversed_range(tmp_path):
    storage = Storage(tmp_path / "records.json")
    storage.add_workout(
        Workout(date(2026, 10, 22), "Sample exercise", 1, 1, 2.0),
    )

    output = run_cli(storage, [
        "7", "invalid date", "2026-10-23", "2026-10-22",
        "2026-10-22", "2026-10-22", "0",
    ])

    assert "Invalid input" in output
    assert "Start date must be on or before end date." in output
    assert "Recorded volume (kg x reps): 2.0" in output


def test_views_show_full_names_when_table_cells_are_truncated(tmp_path):
    storage = Storage(tmp_path / "records.json")
    exercise = "Sample exercise with a long descriptive name"
    food = "Sample food with a long descriptive name"
    meal_type = "Sample extended meal type"
    storage.add_workout(Workout(date(2026, 10, 22), exercise, 1, 1))
    storage.add_meal(Meal(date(2026, 10, 22), meal_type, food, 0, 0.0))

    output = run_cli(storage, ["2", "5", "0"])

    assert exercise in output
    assert food in output
    assert meal_type in output
