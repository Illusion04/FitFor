"""Exercise the GUI boundary and unchanged CLI against shared temporary JSON."""

from datetime import date
from pathlib import Path
import subprocess
import sys

import pytest

from fitfor.cli import Menu
from fitfor.gui_support import dashboard_data, delete_record, meal_from_form, workout_from_form
from fitfor.storage import Storage, StorageError


def test_gui_created_records_are_visible_to_cli(tmp_path):
    path = tmp_path / "shared.json"
    gui_storage = Storage(path)
    gui_storage.add_workout(workout_from_form({
        "log_date": "2026-10-23", "exercise": "GUI sample", "sets": "3",
        "reps": "8", "weight_kg": "12.5",
    }))
    gui_storage.add_meal(meal_from_form({
        "log_date": "2026-10-23", "meal_type": "lunch", "food": "GUI bowl",
        "calories": "520", "protein_g": "35", "carbs_g": "60", "fat_g": "15",
    }))
    replies = iter(["2", "5", "7", "", "", "8", "", "", "0"])
    output = []
    Menu(Storage(path), lambda prompt: next(replies), output.append).run()
    transcript = "\n".join(output)
    assert "GUI sample" in transcript
    assert "GUI bowl" in transcript
    assert "Recorded volume (kg x reps): 300.0" in transcript
    assert "Total calories (kcal): 520" in transcript


def test_cli_created_records_feed_gui_dashboard_and_safe_delete(tmp_path):
    path = tmp_path / "shared.json"
    replies = iter([
        "1", "2026-10-23", "CLI sample", "2", "5", "", "", "4", "2026-10-23",
        "lunch", "CLI bowl", "200", "10", "20", "5", "", "0",
    ])
    Menu(Storage(path), lambda prompt: next(replies), lambda text: None).run()
    gui_storage = Storage(path)
    data = dashboard_data(gui_storage.load_workouts(), gui_storage.load_meals(),
                          today=date(2026, 10, 23))
    assert data["workouts"]["entries_without_load"] == 1
    assert data["nutrition"]["total_calories"] == 200
    assert {row[2] for row in data["recent"]} == {"CLI sample", "CLI bowl"}
    assert delete_record(gui_storage, "meal", 1, lambda target: True)
    assert Storage(path).load_meals() == []
    assert len(Storage(path).load_workouts()) == 1


def test_gui_delete_preserves_corrupt_storage_without_confirmation(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not JSON", encoding="utf-8")
    seen = []
    with pytest.raises(StorageError):
        delete_record(Storage(path), "meal", 1, lambda target: seen.append(target))
    assert seen == []
    assert path.read_text(encoding="utf-8") == "not JSON"


@pytest.mark.parametrize("launcher", ["main.py", "gui.py"])
def test_launchers_help_is_headless_and_does_not_create_data(tmp_path, launcher):
    path = tmp_path / "not-created.json"
    result = subprocess.run([
        sys.executable, str(Path(__file__).resolve().parents[1] / launcher),
        "--data-file", str(path), "--help",
    ], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert "--data-file" in result.stdout
    assert not path.exists()
