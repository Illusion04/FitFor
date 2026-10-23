"""Launch FitFor's Tkinter desktop interface alongside the existing CLI."""

import argparse
from collections.abc import Sequence
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from fitfor.gui_support import (
    dashboard_data, delete_record, meal_from_form, volume_text, workout_from_form,
)
from fitfor.models import Workout
from fitfor.storage import DEFAULT_DATA_PATH, Storage, StorageError

BACKGROUND = "#f3f6f8"
CARD = "#ffffff"
TEXT = "#172b3a"
MUTED = "#617482"
ACCENT = "#137c73"


class FitForApp(ttk.Frame):
    """Desktop presentation of the same local records used by the CLI."""

    def __init__(self, root: tk.Tk, storage: Storage) -> None:
        super().__init__(root)
        self.root = root
        self.storage = storage
        self.forms = {}
        self.trees = {}
        self.records = {}
        self._style()
        self.root.title("FitFor - Workout & Nutrition Tracker")
        self.root.geometry("1100x740")
        self.root.minsize(960, 660)
        self.root.configure(background=BACKGROUND)
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Brand.TFrame", padding=(28, 20))
        header.grid(row=0, column=0, sticky="ew")
        brand = ttk.Frame(header, style="Brand.TFrame")
        brand.pack(side="left")
        ttk.Label(brand, text="FITFOR", style="BrandTitle.TLabel").pack(
            anchor="w",
        )
        ttk.Label(
            brand, text="Workout & Nutrition Tracker",
            style="BrandSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))
        ttk.Label(
            header, text="LOCAL WORKSPACE", style="BrandBadge.TLabel",
            padding=(14, 8),
        ).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew",
                           padx=24, pady=(20, 12))
        self.tabs = {}
        for name in ("Dashboard", "Workouts", "Meals", "Reports", "Privacy"):
            tab = ttk.Frame(self.notebook, padding=(22, 18))
            self.notebook.add(tab, text=name)
            self.tabs[name] = tab
        self._build_dashboard()
        self._build_workouts()
        self._build_meals()
        self._build_reports()
        self._build_privacy()

        self.status = tk.StringVar(root, value="Ready. Choose a tab to begin.")
        ttk.Separator(self).grid(row=2, column=0, sticky="ew")
        ttk.Label(
            self, textvariable=self.status, style="Status.TLabel",
            padding=(26, 9),
        ).grid(row=3, column=0, sticky="ew")
        self.root.after_idle(self.refresh_all)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), foreground=TEXT)
        style.configure("TFrame", background=BACKGROUND)
        style.configure("TLabel", background=BACKGROUND)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("PageTitle.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Card.TFrame", background=CARD)
        style.configure("Card.TLabel", background=CARD)
        style.configure("CardTitle.TLabel", background=CARD,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Brand.TFrame", background="#153b43")
        style.configure("BrandTitle.TLabel", background="#153b43",
                        foreground=CARD, font=("Segoe UI", 25, "bold"))
        style.configure("BrandSubtitle.TLabel", background="#153b43",
                        foreground="#c2d7da")
        style.configure("BrandBadge.TLabel", background="#24535a",
                        foreground="#def3ec", font=("Segoe UI", 9, "bold"))
        style.configure("TNotebook", background=BACKGROUND, borderwidth=0)
        style.configure("TNotebook.Tab", background="#e5edef",
                        foreground=MUTED, padding=(24, 11))
        style.map("TNotebook.Tab", background=[("selected", CARD)],
                  foreground=[("selected", ACCENT)],
                  padding=[("selected", (24, 11))])
        style.configure("TButton", padding=(14, 9))
        style.configure("Accent.TButton", background=ACCENT, foreground=CARD)
        style.map("Accent.TButton", background=[("active", "#0e665e")])
        style.configure("Danger.TButton", foreground="#a43c3c")
        style.configure("TEntry", padding=(8, 7))
        style.configure("TCombobox", padding=(8, 7))
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#e8eff1",
                        foreground=MUTED, font=("Segoe UI", 9, "bold"),
                        padding=(8, 9))
        style.map("Treeview", background=[("selected", "#d4ebe6")],
                  foreground=[("selected", "#134d47")])
        style.configure("Status.TLabel", background=CARD, foreground=MUTED)

    def _page_header(self, tab: ttk.Frame, title: str, subtitle: str):
        header = ttk.Frame(tab)
        header.pack(fill="x", pady=(0, 18))
        text = ttk.Frame(header)
        text.pack(side="left", fill="x", expand=True)
        ttk.Label(text, text=title, style="PageTitle.TLabel").pack(anchor="w")
        ttk.Label(text, text=subtitle, style="Muted.TLabel").pack(
            anchor="w", pady=(5, 0),
        )
        return header

    def _build_dashboard(self) -> None:
        header = self._page_header(
            self.tabs["Dashboard"], "Your activity at a glance",
            "An overview of your recorded workouts and nutrition.",
        )
        ttk.Button(header, text="Refresh", command=self.refresh_all).pack(side="right")
        tab = self.tabs["Dashboard"]
        cards = ttk.Frame(tab)
        cards.pack(fill="x")
        cards.columnconfigure((0, 1), weight=1)
        self.dashboard_workout = self._summary_card(cards, "WORKOUTS / ALL DATES", [
            ("workout_entries", "Exercise entries"), ("total_sets", "Total sets"),
            ("total_reps", "Total reps"), ("recorded_volume", "Recorded volume (kg × reps)"),
        ], 0)
        self.dashboard_nutrition = self._summary_card(cards, "NUTRITION / TODAY", [
            ("total_calories", "Calories (kcal)"), ("total_protein_g", "Protein (g)"),
            ("total_carbs_g", "Carbohydrates (g)"), ("total_fat_g", "Fat (g)"),
        ], 1)
        self.dashboard_note = tk.StringVar(self.root)
        ttk.Label(tab, textvariable=self.dashboard_note, style="Muted.TLabel").pack(
            anchor="w", pady=(12, 14),
        )
        recent = ttk.Frame(tab, style="Card.TFrame", padding=16)
        recent.pack(fill="both", expand=True)
        ttk.Label(recent, text="Recent activity / latest 8 entries",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.trees["recent"] = self._table(recent, [
            ("date", "Date", 130), ("type", "Type", 120),
            ("entry", "Recorded entry", 600),
        ])

    def _summary_card(self, parent, title, specs, column):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(18, 14))
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0, 8) if column == 0 else (8, 0))
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text=title, style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8),
        )
        variables = {}
        for row, (key, label) in enumerate(specs, start=1):
            ttk.Label(card, text=label, style="Card.TLabel").grid(
                row=row, column=0, sticky="w", pady=4,
            )
            variables[key] = tk.StringVar(self.root, value="—")
            ttk.Label(card, textvariable=variables[key], style="CardTitle.TLabel").grid(
                row=row, column=1, sticky="e", padx=(12, 0), pady=4,
            )
        return variables

    @staticmethod
    def _set_metrics(variables, values):
        for key, variable in variables.items():
            value = values.get(key)
            variable.set("—" if value is None else
                         f"{value:,}" if isinstance(value, int) else f"{value:,.2f}")

    def _refresh_dashboard(self, workouts, meals) -> None:
        tree = self.trees["recent"]
        tree.delete(*tree.get_children())
        try:
            data = dashboard_data(workouts, meals, today=date.today())
        except ValueError as error:
            self._set_metrics(self.dashboard_workout, {})
            self._set_metrics(self.dashboard_nutrition, {})
            self.dashboard_note.set(f"Summary unavailable: {error}")
            return
        self._set_metrics(self.dashboard_workout, data["workouts"])
        self._set_metrics(self.dashboard_nutrition, data["nutrition"])
        self.dashboard_note.set(
            "No activity recorded yet. Start in Workouts or Meals."
            if not data["recent"] else
            f"Today: {date.today().isoformat()} · Unknown workout loads are excluded from volume."
        )
        for index, (day, kind, name, _) in enumerate(data["recent"]):
            tree.insert("", "end", values=(day.isoformat(), kind, name),
                        tags=("even" if index % 2 == 0 else "odd",))

    def _build_workouts(self) -> None:
        tab = self.tabs["Workouts"]
        self._page_header(
            tab, "Workout log",
            "Record an exercise, then review your entries below.",
        )
        card = ttk.Frame(tab, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 16))
        fields = {}
        self.forms["workout"] = fields
        specs = [
            ("log_date", "Date (YYYY-MM-DD)"),
            ("exercise", "Exercise"),
            ("sets", "Sets"),
            ("reps", "Reps / set"),
            ("weight_kg", "Weight (kg, optional)"),
        ]
        for column, (name, label) in enumerate(specs):
            card.columnconfigure(column, weight=3 if name == "exercise" else 1)
            self._form_field(card, fields, name, label, 0, column)
        self._form_field(card, fields, "notes", "Notes (optional)", 1, 0, 5)
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=5, sticky="w", pady=(10, 0))
        ttk.Button(actions, text="Save Workout", style="Accent.TButton",
                   command=self._save_workout).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Clear Form",
                   command=lambda: self._clear_form("workout")).pack(
                       side="left",
                   )
        listing = ttk.Frame(tab, style="Card.TFrame", padding=16)
        listing.pack(fill="both", expand=True)
        toolbar = ttk.Frame(listing, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(0, 12))
        self.workout_count = tk.StringVar(self.root, value="No workouts yet")
        ttk.Label(toolbar, textvariable=self.workout_count,
                  style="CardTitle.TLabel").pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=self.refresh_all).pack(
            side="right", padx=(8, 0),
        )
        ttk.Button(toolbar, text="Delete Selected", style="Danger.TButton",
                   command=lambda: self._delete_selected("workout")).pack(
                       side="right",
                   )
        self.trees["workout"] = self._table(listing, [
            ("date", "Date", 100), ("exercise", "Exercise", 190),
            ("sets", "Sets", 50), ("reps", "Reps / set", 75),
            ("weight", "Weight (kg)", 95), ("volume", "Volume", 105),
            ("notes", "Notes", 220),
        ])

    def _form_field(
        self, parent, fields, name, label, row, column, columnspan=1,
    ):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.grid(row=row, column=column, columnspan=columnspan,
                   sticky="ew", padx=(0, 12), pady=(0, 9))
        ttk.Label(frame, text=label, style="Card.TLabel").pack(anchor="w")
        value = (date.today().isoformat() if name == "log_date"
                 else "0" if name in ("carbs_g", "fat_g") else "")
        fields[name] = tk.StringVar(self.root, value=value)
        entry = ttk.Entry(frame, textvariable=fields[name], width=12)
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def _table(self, parent, columns):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tree = ttk.Treeview(
            frame, columns=[key for key, _, _ in columns],
            show="headings", selectmode="browse", height=8,
        )
        for key, label, width in columns:
            tree.heading(key, text=label)
            tree.column(key, width=width, minwidth=45, anchor="w")
        vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal",
                                   command=tree.xview)
        tree.configure(yscrollcommand=vertical.set,
                       xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        tree.tag_configure("even", background=CARD)
        tree.tag_configure("odd", background="#f5f8f9")
        return tree

    def _clear_form(self, kind: str) -> None:
        for name, variable in self.forms[kind].items():
            variable.set(date.today().isoformat() if name == "log_date"
                         else "0" if name in ("carbs_g", "fat_g") else "")
        self.status.set("Form cleared. Saved records are unchanged.")

    def _show_error(self, title: str, message: str) -> None:
        self.status.set(message)
        messagebox.showerror(title, message, parent=self.root)

    def _save_workout(self) -> None:
        try:
            workout = workout_from_form({
                name: value.get() for name, value in self.forms["workout"].items()
            })
            saved = self.storage.add_workout(workout)
        except (ValueError, StorageError) as error:
            self._show_error("Workout not saved", str(error))
            return
        refreshed = self.refresh_all()
        self._clear_form("workout")
        self.status.set(
            f"Workout {saved.id} saved."
            if refreshed else "Workout saved; list could not refresh."
        )

    def refresh_all(self) -> bool:
        """Reload shared storage; never silently reset an unreadable file."""
        try:
            workouts = self.storage.load_workouts()
            meals = self.storage.load_meals()
        except StorageError as error:
            self._show_error("Unable to load records", str(error))
            return False
        self.records["workout"] = {entry.id: entry for entry in workouts}
        tree = self.trees["workout"]
        tree.delete(*tree.get_children())
        for index, entry in enumerate(sorted(
            workouts, key=lambda item: (item.log_date, item.id), reverse=True,
        )):
            tree.insert("", "end", iid=str(entry.id), tags=(
                "even" if index % 2 == 0 else "odd",
            ), values=(
                entry.log_date.isoformat(), entry.exercise, entry.sets,
                entry.reps,
                "-" if entry.weight_kg is None else f"{entry.weight_kg:,.2f}",
                volume_text(entry), entry.notes,
            ))
        count = len(workouts)
        self.workout_count.set(
            "No workouts yet" if count == 0 else f"Workout entries ({count})"
        )
        self.records["meal"] = {entry.id: entry for entry in meals}
        tree = self.trees["meal"]
        tree.delete(*tree.get_children())
        for index, entry in enumerate(sorted(
            meals, key=lambda item: (item.log_date, item.id), reverse=True,
        )):
            tree.insert("", "end", iid=str(entry.id), tags=(
                "even" if index % 2 == 0 else "odd",
            ), values=(
                entry.log_date.isoformat(), entry.meal_type, entry.food,
                entry.calories, f"{entry.protein_g:,.1f}",
                f"{entry.carbs_g:,.1f}", f"{entry.fat_g:,.1f}", entry.notes,
            ))
        count = len(meals)
        self.meal_count.set(
            "No meals yet" if count == 0 else f"Meal entries ({count})"
        )
        self._refresh_dashboard(workouts, meals)
        self.status.set("Records refreshed.")
        return True

    def _delete_selected(self, kind: str) -> None:
        selected = self.trees[kind].selection()
        if not selected:
            messagebox.showinfo(
                "No selection", f"Select a {kind} in the table first.",
                parent=self.root,
            )
            return
        identifier = int(selected[0])

        def confirm(entry):
            name = entry.exercise if isinstance(entry, Workout) else entry.food
            return messagebox.askyesno(
                f"Delete {kind.title()}",
                "You are about to permanently delete:\n\n"
                f"{kind.title()} #{entry.id}\n"
                f"{entry.log_date.isoformat()} - {name}\n\n"
                "This cannot be undone. Continue?",
                icon="warning", default="no", parent=self.root,
            )

        try:
            deleted = delete_record(
                self.storage, kind, identifier, confirm,
                expected=self.records[kind].get(identifier),
            )
        except (ValueError, StorageError) as error:
            self._show_error("Unable to delete record", str(error))
            return
        if deleted:
            self.refresh_all()
            self.status.set(f"{kind.title()} deleted.")
        else:
            self.status.set("Deletion cancelled. Record preserved.")

    def _build_meals(self) -> None:
        tab = self.tabs["Meals"]
        self._page_header(
            tab, "Meal log",
            "Keep food entries and their recorded nutrients together.",
        )
        card = ttk.Frame(tab, style="Card.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 14))
        for column in range(4):
            card.columnconfigure(column, weight=1)
        fields = {}
        self.forms["meal"] = fields
        self._form_field(card, fields, "log_date", "Date (YYYY-MM-DD)", 0, 0)
        self._form_field(card, fields, "meal_type", "Meal type (e.g. lunch)", 0, 1)
        self._form_field(card, fields, "food", "Food / meal name", 0, 2, 2)
        for column, (name, label) in enumerate([
            ("calories", "Calories (kcal)"), ("protein_g", "Protein (g)"),
            ("carbs_g", "Carbohydrates (g)"), ("fat_g", "Fat (g)"),
        ]):
            self._form_field(card, fields, name, label, 1, column)
        self._form_field(card, fields, "notes", "Notes (optional)", 2, 0, 4)
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=3, column=0, columnspan=4, sticky="w", pady=(4, 0))
        ttk.Button(actions, text="Save Meal", style="Accent.TButton",
                   command=self._save_meal).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Clear Form",
                   command=lambda: self._clear_form("meal")).pack(side="left")
        listing = ttk.Frame(tab, style="Card.TFrame", padding=14)
        listing.pack(fill="both", expand=True)
        toolbar = ttk.Frame(listing, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        self.meal_count = tk.StringVar(self.root, value="No meals yet")
        ttk.Label(toolbar, textvariable=self.meal_count,
                  style="CardTitle.TLabel").pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=self.refresh_all).pack(
            side="right", padx=(8, 0),
        )
        ttk.Button(toolbar, text="Delete Selected", style="Danger.TButton",
                   command=lambda: self._delete_selected("meal")).pack(side="right")
        self.trees["meal"] = self._table(listing, [
            ("date", "Date", 100), ("type", "Type", 80),
            ("food", "Food / meal", 190), ("calories", "kcal", 75),
            ("protein", "Protein (g)", 90), ("carbs", "Carbs (g)", 90),
            ("fat", "Fat (g)", 75), ("notes", "Notes", 180),
        ])

    def _save_meal(self) -> None:
        try:
            meal = meal_from_form({
                name: value.get() for name, value in self.forms["meal"].items()
            })
            saved = self.storage.add_meal(meal)
        except (ValueError, StorageError) as error:
            self._show_error("Meal not saved", str(error))
            return
        refreshed = self.refresh_all()
        self._clear_form("meal")
        self.status.set(
            f"Meal {saved.id} saved."
            if refreshed else "Meal saved; list could not refresh."
        )

    def _build_reports(self) -> None:
        self._page_header(
            self.tabs["Reports"], "Reports",
            "Explore the information you recorded over a selected period.",
        )

    def _build_privacy(self) -> None:
        self._page_header(
            self.tabs["Privacy"], "Protect Your Progress",
            "Small habits that help you manage personal records carefully.",
        )


def main(argv: Sequence[str] | None = None) -> None:
    """Select the shared data file and launch the independent desktop UI."""
    parser = argparse.ArgumentParser(description="FitFor desktop tracker")
    parser.add_argument(
        "--data-file", type=Path, default=DEFAULT_DATA_PATH,
        help="JSON file shared with the CLI (default: data/fitfor_data.json)",
    )
    arguments = parser.parse_args(argv)
    root = tk.Tk()
    FitForApp(root, Storage(arguments.data_file))
    root.mainloop()


if __name__ == "__main__":
    main()
