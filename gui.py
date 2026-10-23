"""Launch FitFor's Tkinter desktop interface alongside the existing CLI."""

import argparse
from collections.abc import Sequence
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from fitfor.storage import DEFAULT_DATA_PATH, Storage

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
        self._style()
        self.root.title("FitFor - Workout & Nutrition Tracker")
        self.root.geometry("1100x740")
        self.root.minsize(960, 660)
        self.root.configure(background=BACKGROUND)
        self.pack(fill="both", expand=True)

        header = ttk.Frame(self, style="Brand.TFrame", padding=(28, 20))
        header.pack(fill="x")
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
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(20, 12))
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
        ttk.Separator(self).pack(fill="x")
        ttk.Label(
            self, textvariable=self.status, style="Status.TLabel",
            padding=(26, 9),
        ).pack(fill="x")

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
                  foreground=[("selected", ACCENT)])
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
        self._page_header(
            self.tabs["Dashboard"], "Your activity at a glance",
            "An overview of your recorded workouts and nutrition.",
        )

    def _build_workouts(self) -> None:
        self._page_header(
            self.tabs["Workouts"], "Workout log",
            "Record an exercise, then review your entries below.",
        )

    def _build_meals(self) -> None:
        self._page_header(
            self.tabs["Meals"], "Meal log",
            "Keep food entries and their recorded nutrients together.",
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
