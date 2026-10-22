"""Local JSON persistence with validated records and atomic replacement."""

from dataclasses import asdict, fields, replace
from datetime import date
import json
import os
from pathlib import Path
import tempfile
from typing import TypeVar

from fitfor.models import Meal, Workout
from fitfor.validation import (
    validate_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_positive_int,
    validate_text,
)

DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "fitfor_data.json"
)
Entry = TypeVar("Entry", Workout, Meal)


class StorageError(Exception):
    """A storage operation failed without deliberately discarding records."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}.")
        result[key] = value
    return result


def _stored_int(value: object, name: str, *, positive: bool = False) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be stored as an integer.")
    if positive:
        return validate_positive_int(value, name)
    return validate_non_negative_int(value, name)


def _stored_number(value: object, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be stored as a number.")
    return validate_non_negative_float(value, name)


def _decode_record(raw: object, model: type[Entry]) -> Entry:
    try:
        if not isinstance(raw, dict):
            raise ValueError("Each entry must be an object.")
        if set(raw) - {field.name for field in fields(model)}:
            raise ValueError("Entry contains unrecognised fields.")
        values = dict(raw)
        values["id"] = _stored_int(raw.get("id"), "ID", positive=True)
        values["log_date"] = validate_date(raw["log_date"])
        values["notes"] = validate_text(
            raw.get("notes", ""), "Notes", required=False,
        )
        if model is Workout:
            values["exercise"] = validate_text(raw["exercise"], "Exercise")
            values["sets"] = _stored_int(raw["sets"], "Sets", positive=True)
            values["reps"] = _stored_int(raw["reps"], "Reps", positive=True)
            weight = raw.get("weight_kg")
            values["weight_kg"] = (
                None if weight is None else _stored_number(weight, "Weight")
            )
        else:
            values["meal_type"] = validate_text(raw["meal_type"], "Meal type")
            values["food"] = validate_text(raw["food"], "Food")
            values["calories"] = _stored_int(raw["calories"], "Calories")
            values["protein_g"] = _stored_number(raw["protein_g"], "Protein")
            for name in ("carbs_g", "fat_g"):
                values[name] = _stored_number(raw.get(name, 0.0), name)
        return model(**values)
    except (KeyError, TypeError, ValueError) as error:
        raise StorageError(
            f"Invalid {model.__name__} record: {error}"
        ) from error


def _encode_record(entry: Workout | Meal) -> dict:
    if type(entry.log_date) is not date:
        raise StorageError("A record's log_date must be a date object.")
    values = asdict(entry)
    values["log_date"] = entry.log_date.isoformat()
    return values


def _validate_data(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != {"workouts", "meals"}:
        raise StorageError("Storage must contain workout and meal lists.")
    for name, model in (("workouts", Workout), ("meals", Meal)):
        if not isinstance(data[name], list):
            raise StorageError(f"Stored {name} must be a list.")
        identifiers = set()
        for raw in data[name]:
            entry = _decode_record(raw, model)
            if entry.id in identifiers:
                raise StorageError(f"Duplicate ID in stored {name}.")
            identifiers.add(entry.id)
    return data


class Storage:
    """Store one user's entries; concurrent writers are not supported."""

    def __init__(self, path: str | Path = DEFAULT_DATA_PATH) -> None:
        self.path = Path(path)

    def _read(self) -> dict:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {"workouts": [], "meals": []}
        except (OSError, UnicodeError) as error:
            raise StorageError(f"Cannot read {self.path}: {error}") from error
        if not text.strip():
            return {"workouts": [], "meals": []}
        try:
            data = json.loads(text, object_pairs_hook=_unique_object)
        except (ValueError, RecursionError) as error:
            raise StorageError(
                f"Invalid JSON in {self.path}; the file was left unchanged."
            ) from error
        return _validate_data(data)

    def _write(self, data: dict) -> None:
        _validate_data(data)
        temporary_path = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                json.dump(data, stream, indent=2, ensure_ascii=False,
                          allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, self.path)
        except (OSError, ValueError) as error:
            raise StorageError(
                f"Cannot save {self.path}; previous data was not replaced: "
                f"{error}"
            ) from error
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass  # A cleanup failure must not hide the original error.

    def load_workouts(self) -> list[Workout]:
        """Load validated exercise entries without changing the data file."""
        return [_decode_record(raw, Workout)
                for raw in self._read()["workouts"]]

    def load_meals(self) -> list[Meal]:
        """Load validated food entries without changing the data file."""
        return [_decode_record(raw, Meal) for raw in self._read()["meals"]]

    def _add(self, entry: Entry, collection: str) -> Entry:
        data = self._read()
        next_id = max((raw["id"] for raw in data[collection]), default=0) + 1
        saved = _decode_record(
            _encode_record(replace(entry, id=next_id)), type(entry),
        )
        data[collection].append(_encode_record(saved))
        self._write(data)
        return saved

    def add_workout(self, workout: Workout) -> Workout:
        """Save an exercise and return a copy with its assigned ID."""
        return self._add(workout, "workouts")

    def add_meal(self, meal: Meal) -> Meal:
        """Save a food entry with an assigned ID; return the saved copy."""
        return self._add(meal, "meals")

    def _delete(self, identifier: int, collection: str) -> bool:
        _stored_int(identifier, "ID", positive=True)
        data = self._read()
        retained = [raw for raw in data[collection] if raw["id"] != identifier]
        if len(retained) == len(data[collection]):
            return False
        data[collection] = retained
        self._write(data)
        return True

    def delete_workout(self, identifier: int) -> bool:
        """Delete an exercise by ID after the UI has obtained confirmation."""
        return self._delete(identifier, "workouts")

    def delete_meal(self, identifier: int) -> bool:
        """Delete a meal by ID after the UI has obtained confirmation."""
        return self._delete(identifier, "meals")
