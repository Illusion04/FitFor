"""Data models for locally recorded workout and meal entries."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Workout:
    """One exercise entry, with an optional recorded load in kilograms."""

    log_date: date
    exercise: str
    sets: int
    reps: int
    weight_kg: float | None = None
    id: int | None = None
    notes: str = ""

    @property
    def volume(self) -> float | None:
        """Return sets × reps × load, or None when load was not recorded."""
        if self.weight_kg is None:
            return None
        return self.sets * self.reps * self.weight_kg


@dataclass
class Meal:
    """One food entry, with energy in kcal and macronutrients in grams."""

    log_date: date
    meal_type: str
    food: str
    calories: int
    protein_g: float
    id: int | None = None
    carbs_g: float = 0.0
    fat_g: float = 0.0
    notes: str = ""
