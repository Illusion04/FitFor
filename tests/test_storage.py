"""Persistence tests use pytest temporary paths, never real user records."""

from dataclasses import asdict
from datetime import date
import json

import pytest

from fitfor.models import Meal, Workout
from fitfor.storage import Storage, StorageError


@pytest.fixture
def workout():
    return Workout(date(2026, 10, 22), "Sample press", 3, 8, 12.5,
                   notes="Synthetic entry")


@pytest.fixture
def meal():
    return Meal(date(2026, 10, 22), "lunch", "Sample wrap", 520, 35.0,
                carbs_g=60.5, fat_g=15.0, notes="Synthetic entry")


def test_missing_file_loads_empty_without_creating_files(tmp_path):
    path = tmp_path / "absent" / "records.json"
    storage = Storage(path)

    assert storage.load_workouts() == []
    assert storage.load_meals() == []
    assert not path.exists()


@pytest.mark.parametrize("text", ["", "  \n", '{"workouts": [], "meals": []}'])
def test_empty_storage_is_safe(tmp_path, text):
    path = tmp_path / "records.json"
    path.write_text(text, encoding="utf-8")

    assert Storage(path).load_workouts() == []
    assert Storage(path).load_meals() == []


def test_save_reload_both_collections_and_preserve_dates(tmp_path, workout, meal):
    path = tmp_path / "nested" / "records.json"
    storage = Storage(path)
    saved_workout = storage.add_workout(workout)
    saved_meal = storage.add_meal(meal)

    reopened = Storage(path)
    assert reopened.load_workouts() == [saved_workout]
    assert reopened.load_meals() == [saved_meal]
    assert saved_workout.id == 1
    assert saved_meal.id == 1
    assert workout.id is None
    assert meal.id is None
    assert json.loads(path.read_text(encoding="utf-8"))["workouts"][0][
        "log_date"
    ] == "2026-10-22"


def test_multiple_entries_receive_unique_ids(tmp_path, workout, meal):
    storage = Storage(tmp_path / "records.json")
    for _ in range(3):
        storage.add_workout(workout)
        storage.add_meal(meal)

    assert [entry.id for entry in storage.load_workouts()] == [1, 2, 3]
    assert [entry.id for entry in storage.load_meals()] == [1, 2, 3]


def test_unrecorded_load_round_trips_as_null(tmp_path):
    storage = Storage(tmp_path / "records.json")
    saved = storage.add_workout(
        Workout(date(2026, 10, 22), "Sample bodyweight exercise", 2, 10),
    )

    assert storage.load_workouts() == [saved]
    assert saved.volume is None


def test_deletion_targets_only_the_selected_collection(tmp_path, workout, meal):
    storage = Storage(tmp_path / "records.json")
    storage.add_workout(workout)
    remaining = storage.add_workout(workout)
    saved_meal = storage.add_meal(meal)

    assert storage.delete_workout(1) is True
    assert storage.delete_workout(999) is False
    assert storage.load_workouts() == [remaining]
    assert storage.load_meals() == [saved_meal]
    assert storage.delete_meal(1) is True
    assert storage.load_meals() == []


@pytest.mark.parametrize("identifier", [0, -1, True, "1"])
def test_invalid_delete_id_does_not_change_storage(
    tmp_path, workout, identifier,
):
    path = tmp_path / "records.json"
    storage = Storage(path)
    storage.add_workout(workout)
    before = path.read_bytes()

    with pytest.raises(ValueError):
        storage.delete_workout(identifier)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "text", ["not JSON", "[]", "{}", '{"workouts": {}, "meals": []}',
             '{"workouts": [null], "meals": []}',
             '{"workouts": [], "meals": [], "unknown": 1}'],
)
def test_corrupt_storage_is_reported_and_not_overwritten(tmp_path, workout, text):
    path = tmp_path / "records.json"
    path.write_text(text, encoding="utf-8")
    before = path.read_bytes()
    storage = Storage(path)

    with pytest.raises(StorageError):
        storage.load_workouts()
    with pytest.raises(StorageError):
        storage.add_workout(workout)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    ("field", "value"),
    [("id", None), ("id", True), ("sets", 0), ("reps", "8"),
     ("weight_kg", float("nan")), ("log_date", "2026-02-29"),
     ("exercise", ""), ("notes", []), ("unknown", 5)],
)
def test_invalid_workout_records_are_rejected(tmp_path, workout, field, value):
    raw = asdict(workout)
    raw.update(id=1, log_date="2026-10-22")
    raw[field] = value
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"workouts": [raw], "meals": []}),
                    encoding="utf-8")

    with pytest.raises(StorageError):
        Storage(path).load_workouts()


def test_duplicate_ids_are_rejected(tmp_path, workout):
    path = tmp_path / "records.json"
    raw = asdict(workout)
    raw.update(id=1, log_date="2026-10-22")
    path.write_text(json.dumps({"workouts": [raw, raw], "meals": []}),
                    encoding="utf-8")

    with pytest.raises(StorageError, match="Duplicate ID"):
        Storage(path).load_workouts()


def test_invalid_model_is_not_saved(tmp_path, workout):
    path = tmp_path / "records.json"
    storage = Storage(path)
    storage.add_workout(workout)
    before = path.read_bytes()
    workout.sets = 0

    with pytest.raises(StorageError):
        storage.add_workout(workout)
    assert path.read_bytes() == before


def test_failed_replacement_preserves_existing_file(
    tmp_path, monkeypatch, workout,
):
    path = tmp_path / "records.json"
    storage = Storage(path)
    storage.add_workout(workout)
    before = path.read_bytes()

    def fail_replace(source, destination):
        raise PermissionError("Synthetic write failure")

    monkeypatch.setattr("fitfor.storage.os.replace", fail_replace)
    with pytest.raises(StorageError, match="previous data was not replaced"):
        storage.add_workout(workout)

    assert path.read_bytes() == before
    assert sorted(item.name for item in tmp_path.iterdir()) == ["records.json"]
