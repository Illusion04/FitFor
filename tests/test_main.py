"""Run the real entry point against temporary, synthetic storage."""

from pathlib import Path
import subprocess
import sys

from fitfor.storage import Storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_app(path, commands, working_directory):
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"),
         "--data-file", str(path)],
        input="\n".join(commands) + "\n", text=True, capture_output=True,
        cwd=working_directory, timeout=10, check=False,
    )


def test_main_launches_and_exits_without_creating_data(tmp_path):
    path = tmp_path / "records.json"

    result = run_app(path, ["0"], tmp_path)

    assert result.returncode == 0, result.stderr
    assert "FITFOR" in result.stdout
    assert "Goodbye." in result.stdout
    assert not path.exists()


def test_importing_main_does_not_start_the_menu():
    result = subprocess.run(
        [sys.executable, "-c", "import main; print('imported')"],
        input="", text=True, capture_output=True, cwd=PROJECT_ROOT,
        timeout=10, check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "imported"


def test_records_survive_restart_and_can_be_reported_and_deleted(tmp_path):
    path = tmp_path / "records.json"
    added = run_app(path, [
        "1", "2026-10-22", "Sample press", "3", "8", "12.5", "Sample note",
        "4", "2026-10-22", "lunch", "Sample wrap", "520", "35", "60.5",
        "15", "", "0",
    ], tmp_path)

    assert added.returncode == 0, added.stderr
    assert len(Storage(path).load_workouts()) == 1
    assert len(Storage(path).load_meals()) == 1

    reopened = run_app(path, [
        "2", "5", "7", "", "", "8", "", "",
        "3", "1", "y", "6", "1", "y", "0",
    ], tmp_path)

    assert reopened.returncode == 0, reopened.stderr
    assert "Sample press" in reopened.stdout
    assert "Sample wrap" in reopened.stdout
    assert "Recorded volume (kg x reps): 300.0" in reopened.stdout
    assert "Total calories (kcal): 520" in reopened.stdout
    assert "Workout deleted." in reopened.stdout
    assert "Meal deleted." in reopened.stdout
    assert Storage(path).load_workouts() == []
    assert Storage(path).load_meals() == []
