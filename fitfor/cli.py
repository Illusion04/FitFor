"""Interactive prompts and display for the FitFor command-line application."""

from collections.abc import Callable
from datetime import date
from typing import TypeVar

from fitfor.models import Meal, Workout
from fitfor.reports import (
    daily_nutrition_summary,
    nutrition_summary,
    workout_summary,
)
from fitfor.storage import Storage, StorageError
from fitfor.validation import (
    validate_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_positive_int,
    validate_text,
    validate_weight,
)

MENU_TEXT = """
FITFOR
1. Add workout
2. View workouts
3. Delete workout
4. Add meal
5. View meals
6. Delete meal
7. Workout report
8. Nutrition report
9. Privacy and data guidance
0. Exit
"""

PRIVACY_TEXT = """
Protect Your Progress

FitFor stores your workout and nutrition records locally.
- Review the date, name and ID before confirming deletion.
- Avoid passwords, financial details or medical information in notes.
- Review files and screenshots before sharing your fitness data.
- Store backups securely and restrict access to your account and data folder.

Records are not encrypted and there is no application login.
FitFor records information; it does not provide medical recommendations.
"""

Value = TypeVar("Value")


class Menu:
    """Coordinate UI actions; input/output can be supplied for testing."""

    def __init__(
        self,
        storage: Storage,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.storage = storage
        self.input = input_fn
        self.output = output_fn

    def _prompt(self, label: str, validator: Callable[[str], Value]) -> Value:
        while True:
            try:
                return validator(self.input(label))
            except ValueError as error:
                self.output(f"Invalid input: {error}")

    def _text(self, label: str, *, required: bool = True) -> str:
        return self._prompt(
            f"{label}: ",
            lambda value: validate_text(value, label, required=required),
        )

    def run(self) -> None:
        """Run until exit or interruption, handling expected errors."""
        actions = {
            "1": self._add_workout,
            "2": self._view_workouts,
            "3": lambda: self._delete("workout"),
            "4": self._add_meal,
            "5": self._view_meals,
            "6": lambda: self._delete("meal"),
            "7": self._workout_report,
            "8": self._nutrition_report,
            "9": lambda: self.output(PRIVACY_TEXT),
        }
        try:
            while True:
                self.output(MENU_TEXT)
                choice = self.input("Choose an option: ").strip()
                if choice == "0":
                    self.output("Goodbye.")
                    return
                action = actions.get(choice)
                if action is None:
                    self.output(
                        "Invalid choice. Enter one of the menu numbers."
                    )
                    continue
                try:
                    action()
                except (StorageError, ValueError, OverflowError) as error:
                    self.output(f"Unable to complete action: {error}")
        except (EOFError, KeyboardInterrupt):
            self.output("\nExiting FitFor.")

    def _add_workout(self) -> None:
        log_date = self._prompt("Date (YYYY-MM-DD): ", validate_date)
        exercise = self._text("Exercise")
        sets = self._prompt("Sets: ",
                            lambda value: validate_positive_int(value, "Sets"))
        reps = self._prompt("Reps per set: ",
                            lambda value: validate_positive_int(value, "Reps"))
        weight = self._prompt("Weight in kg (blank if unrecorded): ",
                              validate_weight)
        notes = self._text("Notes (optional)", required=False)
        saved = self.storage.add_workout(
            Workout(log_date, exercise, sets, reps, weight, notes=notes),
        )
        self.output(f"Workout saved with ID {saved.id}.")

    def _add_meal(self) -> None:
        log_date = self._prompt("Date (YYYY-MM-DD): ", validate_date)
        meal_type = self._text("Meal type")
        food = self._text("Food")
        calories = self._prompt(
            "Calories (kcal): ",
            lambda value: validate_non_negative_int(value, "Calories"),
        )
        nutrients = []
        for name in ("Protein", "Carbohydrates", "Fat"):
            nutrients.append(self._prompt(
                f"{name} (g): ",
                lambda value, field=name: validate_non_negative_float(
                    value, field,
                ),
            ))
        notes = self._text("Notes (optional)", required=False)
        saved = self.storage.add_meal(Meal(
            log_date, meal_type, food, calories, nutrients[0],
            carbs_g=nutrients[1], fat_g=nutrients[2], notes=notes,
        ))
        self.output(f"Meal saved with ID {saved.id}.")

    def _view_workouts(self) -> None:
        entries = self.storage.load_workouts()
        if not entries:
            self.output("No workouts recorded.")
            return
        self.output(
            f"{'ID':>4}  {'Date':10}  {'Exercise':24}  "
            f"{'Sets':>4} {'Reps':>4} {'kg':>9} {'Volume':>12}"
        )
        for entry in entries:
            weight = (
                "-" if entry.weight_kg is None else f"{entry.weight_kg:.2f}"
            )
            volume = "-" if entry.volume is None else f"{entry.volume:.2f}"
            self.output(
                f"{entry.id:>4}  {entry.log_date.isoformat()}  "
                f"{entry.exercise:<24.24}  {entry.sets:>4} {entry.reps:>4} "
                f"{weight:>9} {volume:>12}"
            )
            if len(entry.exercise) > 24:
                self.output(f"  Exercise: {entry.exercise}")
            if entry.notes:
                self.output(f"  Notes: {entry.notes}")

    def _view_meals(self) -> None:
        entries = self.storage.load_meals()
        if not entries:
            self.output("No meals recorded.")
            return
        self.output(
            f"{'ID':>4}  {'Date':10}  {'Type':10} {'Food':22} {'kcal':>7}"
        )
        for entry in entries:
            self.output(
                f"{entry.id:>4}  {entry.log_date.isoformat()}  "
                f"{entry.meal_type:<10.10} {entry.food:<22.22} "
                f"{entry.calories:>7}"
            )
            if len(entry.meal_type) > 10 or len(entry.food) > 22:
                self.output(f"  Meal: {entry.meal_type} - {entry.food}")
            self.output(
                f"  Protein: {entry.protein_g:.2f} g | "
                f"Carbs: {entry.carbs_g:.2f} g | Fat: {entry.fat_g:.2f} g"
            )
            if entry.notes:
                self.output(f"  Notes: {entry.notes}")

    def _delete(self, kind: str) -> None:
        entries = (self.storage.load_workouts() if kind == "workout"
                   else self.storage.load_meals())
        if not entries:
            self.output(f"No {kind}s recorded.")
            return
        identifier = self._prompt(
            f"{kind.title()} ID to delete: ",
            lambda value: validate_positive_int(value, "ID"),
        )
        entry = next((item for item in entries if item.id == identifier), None)
        if entry is None:
            self.output(f"No {kind} found with ID {identifier}.")
            return
        self.output("You are about to permanently delete:")
        self.output(f"{kind.title()} ID {identifier}:")
        name = entry.exercise if isinstance(entry, Workout) else entry.food
        self.output(f"{entry.log_date.isoformat()} - {name}")
        if isinstance(entry, Workout):
            load = "unrecorded" if entry.weight_kg is None else entry.weight_kg
            self.output(f"Sets: {entry.sets}; reps: {entry.reps}; kg: {load}")
        else:
            self.output(
                f"Meal type: {entry.meal_type}; kcal: {entry.calories}"
            )
        answer = self.input("Continue? (y/n): ").strip().casefold()
        if answer != "y":
            self.output("Deletion cancelled.")
            return
        delete = (self.storage.delete_workout if kind == "workout"
                  else self.storage.delete_meal)
        if delete(identifier):
            self.output(f"{kind.title()} deleted.")
        else:
            self.output(f"No {kind} found with ID {identifier}.")

    def _period(self) -> tuple[date | None, date | None]:
        def optional_date(value: str) -> date | None:
            return None if not value.strip() else validate_date(value)

        while True:
            start = self._prompt("Start date (YYYY-MM-DD, blank for all): ",
                                 optional_date)
            end = self._prompt("End date (YYYY-MM-DD, blank for all): ",
                               optional_date)
            if start is None or end is None or start <= end:
                return start, end
            self.output("Start date must be on or before end date.")

    def _workout_report(self) -> None:
        start, end = self._period()
        summary = workout_summary(self.storage.load_workouts(), start, end)
        labels = {
            "workout_entries": "Exercise entries",
            "workout_days": "Recorded workout days",
            "unique_exercises": "Unique exercises",
            "total_sets": "Total sets",
            "total_reps": "Total repetitions across sets",
            "entries_with_load": "Entries with recorded load",
            "entries_without_load": "Entries without recorded load",
            "recorded_volume": "Recorded volume (kg x reps)",
        }
        for key, label in labels.items():
            self.output(f"{label}: {summary[key]}")
        self.output(
            "Volume = sets x reps x recorded kg; unknown loads excluded."
        )

    def _nutrition_report(self) -> None:
        start, end = self._period()
        meals = self.storage.load_meals()
        summary = nutrition_summary(meals, start, end)
        labels = {
            "meal_entries": "Meal entries",
            "total_calories": "Total calories (kcal)",
            "total_protein_g": "Total protein (g)",
            "total_carbs_g": "Total carbohydrates (g)",
            "total_fat_g": "Total fat (g)",
        }
        for key, label in labels.items():
            self.output(f"{label}: {summary[key]}")
        self.output("Daily nutrition totals:")
        daily = daily_nutrition_summary(meals, start, end)
        if not daily:
            self.output("No meals in the selected period.")
        for day, totals in daily.items():
            self.output(
                f"{day.isoformat()}: {totals['total_calories']} kcal; "
                f"protein {totals['total_protein_g']} g; "
                f"carbs {totals['total_carbs_g']} g; "
                f"fat {totals['total_fat_g']} g"
            )
