# FitFor

FitFor is a Python workout and meal logger with a **command-line interface**
and a **Tkinter desktop interface**, developed for **PFD200 Professional
Development**. Both interfaces record entries locally and summarise the
information entered by the user.

## Purpose

The application gives a user one place to record exercise entries and food
intake, review past records and calculate totals over selected dates. The
project provides practical evidence of modular Python design, input validation,
automated testing, local persistence and incremental Git development. The
student's own reflection should connect that work to their individual skill gap.

## Features

- Add, view and delete workout entries with dates, exercise names, sets,
  repetitions per set, optional recorded weight in kg and optional notes.
- Add, view and delete meals with dates, meal types, food names, integer kcal,
  protein, carbohydrates and fat in grams, and optional notes.
- Require valid calendar dates (`YYYY-MM-DD`), non-empty names, positive
  integer sets/reps and finite, non-negative nutrition/load values.
- Persist both collections in local JSON, assigning IDs within each collection.
- Summarise exercise entries, recorded workout days, unique exercises, sets,
  repetitions across sets and recorded-load volume.
- Summarise calories and nutrients, including daily totals.
- Filter reports using inclusive start/end dates; either boundary can be blank.
- Show the full target date/name/ID before deletion. The CLI requires `y`;
  the GUI requires Yes and defaults to No. Cancellation preserves the record.
- Display **Protect Your Progress** through CLI option 9 and the Privacy tab.
- Report storage errors without silently replacing corrupt records.
- Navigate five desktop tabs: Dashboard, Workouts, Meals, Reports and Privacy.
- Use validated forms, scrollable tables, save/clear feedback and refreshed
  dashboards/reports after each save or deletion.
- See all-time workout metrics, today's nutrient totals and recent activity
  on the desktop dashboard.

## Technology

Runtime uses Python's standard library: `dataclasses`, `datetime`, `json`,
`pathlib`, `argparse`, `tkinter`/`ttk` and supporting modules. There are no
third-party runtime packages to install. Tests use pytest and its dependencies
from `requirements.txt`.
Development uses Git/GitHub.

Verified environment: **Windows, Python 3.12.10, Tk 8.6 and pytest 9.1.1**.
Use a Python installation that includes Tcl/Tk for the desktop interface.
Other operating systems have not been visually tested in this project.

## Project architecture

```text
FitFor/
├── main.py                 # CLI entry point and data-file argument
├── gui.py                  # Tkinter desktop entry point and widgets
├── fitfor/
│   ├── __init__.py
│   ├── models.py           # Workout and Meal dataclasses
│   ├── validation.py       # Reusable parsing and validation
│   ├── storage.py          # JSON persistence and record validation
│   ├── reports.py          # Pure summary calculations
│   ├── cli.py              # Menu, prompts, tables and privacy guidance
│   └── gui_support.py      # Headless form/report/deletion adapters
├── tests/                  # Synthetic unit and integration tests
├── docs/                   # Development, test and assessment evidence
│   └── screenshots/        # Genuine screenshots to be captured manually
├── data/                   # Created on first save; excluded from Git
├── requirements.txt
└── .gitignore
```

The existing package layout is retained; there is no second nested project.
Both interfaces use the same `Workout`/`Meal` dataclasses, reusable validators,
atomic JSON `Storage` and pure report functions. `gui.py` owns widgets and
callbacks; `gui_support.py` converts form strings and coordinates reporting
and confirmation without importing Tkinter. No separate GUI models, database
or validation rules were introduced. The existing CLI modules are preserved.

## Installation

Install Python 3.12, then open PowerShell:

```powershell
git clone https://github.com/Illusion04/FitFor.git
cd FitFor
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Windows exposes Python through its launcher instead of `python`, create
the environment with `py -3.12 -m venv .venv`. An existing virtual environment
should not be recreated unnecessarily.

Activation is optional when using the explicit interpreter path above:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, `python` refers to the environment's interpreter.

## Running

With the virtual environment activated:

```powershell
python main.py  # CLI
python gui.py   # Desktop GUI
```

Without activation, use the environment's interpreter explicitly:

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe gui.py
```

With the environment activated, the equivalent command is `python main.py`.
Choose a numbered option and follow the prompts. Use option 0, Ctrl+C or EOF
to exit. A partially entered record is not saved.

To use an isolated file for a demonstration with synthetic data:

```powershell
.\.venv\Scripts\python.exe main.py --data-file data\demo.json
.\.venv\Scripts\python.exe gui.py --data-file data\demo.json
```

The normal file is `data/fitfor_data.json` relative to the project directory,
even when the program is launched from another directory. An explicitly
supplied relative `--data-file` path is relative to the current directory.
The directory/file is created when an entry is first saved.
Both launchers use this same default. Use one application instance at a time;
after switching between interfaces, use Refresh to reload saved changes.

## Desktop workflow

- **Dashboard:** all-date exercise entries, sets, total reps and recorded-load
  volume; today's calories/nutrients; the latest eight dated entries.
- **Workouts:** enter date, exercise, positive sets/reps and optional kg/notes.
  Save Workout persists the entry, clears the form and refreshes all views.
- **Meals:** enter date, meal type, food, integer kcal and nutrient grams.
  Carbohydrates/fat start at zero; notes are optional. Save Meal refreshes all
  views and clears the form. Invalid input remains available for correction.
- **Reports:** leave either date blank for an open boundary. Generate Report
  applies valid inclusive dates; All Dates resets the filter. Daily nutrition
  totals appear below both summaries. Typed filters take effect on Generate.
- **Privacy:** read Protect Your Progress and the storage/security limitations.

Select a table row before Delete Selected. Check the confirmation's full date,
name and ID, then choose Yes or No. Clear Form affects only unsaved inputs.
The window opens at 1100 × 740 logical pixels and supports resizing with a
960 × 740 minimum; tables have vertical/horizontal scrollbars. Larger screen
scaling can require more physical screen space.

## Interpreting reports

Each workout record is **one exercise entry**, not necessarily an entire
session. Reports count exercise entries and distinct recorded dates separately.
Unique exercise names are compared without case sensitivity.

Recorded volume is:

```text
sets × reps per set × recorded weight in kg
```

For example, synthetic values of 3 sets, 8 reps and 12.5 kg produce 300.0.
An unknown load is stored as `null` and excluded from volume. A recorded zero
load is retained as zero. The metric does not represent total physiological
workload. Nutrient totals are rounded to two decimal places; values are
recorded as entered, not estimated from a nutrition database.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

With activation, use `python -m pytest -v`. The suite covers models, validation,
temporary-file persistence, known report totals, CLI input/error handling,
safe deletion and real entry-point subprocesses. GUI support tests run without
opening a Tk window and verify conversions, summaries, filters, deletion and
shared CLI/GUI persistence. Tests use synthetic data and temporary directories
rather than the normal user data file.

Desktop enhancement result: **229 passed, 0 failed**, including all original
182 tests and 47 new GUI support/integration cases. See the
[GUI smoke-test report](docs/gui-smoke-test.md) for observed real-window flows
and [full pytest output](docs/gui-pytest-results.txt).

See [testing evidence](docs/testing.md) for actual results and live terminal
checks, including the initially failing regression cases and their fixes.

## Data and privacy

Records are local plain-text JSON. There is **no encryption or application
login**. Anyone with access to the file can read or edit it.

- Avoid passwords, financial details or medical information in notes.
- Review records, screenshots and files before sharing them.
- Restrict access to your account/data folder and store backups securely.
- Check the full target preview before confirming permanent deletion.

The default `data/` directory, `.venv/`, caches and `.env` files are ignored by
Git. A custom data path may fall outside these rules; inspect `git status`
before committing. Ignore rules are not encryption or access controls.

If storage cannot be read or contains invalid JSON/records, FitFor shows an
error and does not silently clear it. Exit all instances, preserve a copy of
the affected file and restore a trusted backup or repair it before continuing.
A missing or blank file is treated as empty storage. Backups and recovery are
manual; the application does not create backups automatically.

## Assessment context and evidence

```text
Module: PFD200 Professional Development
Project type: Python mini-project
```

- [Development log](docs/development-log.md): implementation activity, problems,
  tests and commit subjects; student reflection is clearly left pending.
- [Testing document](docs/testing.md): expected/actual results and live checks.
- [Captured pytest output](docs/pytest-results.txt) and
  [live CLI smoke-test transcript](docs/final-smoke-test.txt): historical
  pre-GUI runs operated by Codex, using synthetic data.
- [Desktop verification](docs/gui-smoke-test.md) and
  [GUI-era pytest output](docs/gui-pytest-results.txt): actual native GUI
  observations and the expanded 229-test result.
- [Threat model](docs/threat-model.md): technical and human vulnerabilities,
  implemented controls and residual risks.
- [Protect Your Progress campaign](docs/privacy-campaign.md): in-app messages
  linked directly to the artefact; effectiveness is not claimed.
- [Assessment checklist](docs/assessment-checklist.md): completed artefact
  evidence and work still requiring the student's action.

## Screenshots

No screenshots have been fabricated or embedded. Capture genuine runs using
synthetic entries and save the images under `docs/screenshots/`. Useful views
are the main menu, workout/nutrition reports, deletion preview, privacy guidance
and pytest summary. Review each image for personal information before sharing.

### GUI screenshots

Screenshot files are **pending genuine capture**. The real desktop was visually
tested; the repository contains the factual smoke-test report rather than
invented images. Use a separate synthetic data file and capture:

| Suggested file in `docs/screenshots/` | Evidence |
| --- | --- |
| `gui-dashboard.png` | Workout metrics, today's nutrition and recent activity |
| `gui-add-workout.png` | Completed synthetic workout form before Save |
| `gui-workout-list.png` | Saved row, computed volume and success status |
| `gui-meals.png` | Meal form/list with kcal, protein, carbohydrates and fat |
| `gui-reports.png` | Both summaries, date filters and daily totals |
| `gui-delete-confirmation.png` | Full target preview and default No |
| `gui-privacy.png` | Protect Your Progress guidance and limitations |
| `gui-tests.png` | Actual full-suite result in the terminal |

These filenames describe planned captures; they are not existing image links.

## Limitations

- Desktop GUI and CLI; one local user and one writer at a time. Concurrent instances can
  overwrite each other's changes; atomic saves are not a locking mechanism.
- No authentication, encryption, external services or nutrition database.
- No edit, export, undo, automatic backup or automatic corruption repair.
- IDs are unique within a current collection; they may be reused after deletion
  and are not permanent audit identifiers.
- Workout/meal models hold data; validation occurs at input/storage boundaries.
- No medical recommendations, diagnosis or diet prescriptions.

## Possible future development

Potential extensions include SQLite, a web interface, encrypted storage and
richer analytics. None is part of this implementation.
