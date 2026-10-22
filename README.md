# FitFor

FitFor is a small Python command-line workout and meal logger developed for
**PFD200 Professional Development**. It records entries locally and summarises
the information entered by the user.

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
- Show the full target date/name/ID before deletion; only an explicit `y`
  confirms. Blank, invalid responses and interrupted prompts do not delete.
- Display **Protect Your Progress** privacy guidance through menu option 9.
- Report storage errors without silently replacing corrupt records.

## Technology

Runtime uses Python's standard library: `dataclasses`, `datetime`, `json`,
`pathlib`, `argparse` and supporting modules. There are no runtime packages
to install. Tests use pytest and its dependencies from `requirements.txt`.
Development uses Git/GitHub.

Verified environment: **Python 3.12.10 and pytest 9.1.1**. Python 3.12 is the
recommended setup for reproducing the recorded results.

## Project architecture

```text
FitFor/
├── main.py                 # Application entry point and data-file argument
├── fitfor/
│   ├── __init__.py
│   ├── models.py           # Workout and Meal dataclasses
│   ├── validation.py       # Reusable parsing and validation
│   ├── storage.py          # JSON persistence and record validation
│   ├── reports.py          # Pure summary calculations
│   └── cli.py              # Menu, prompts, tables and privacy guidance
├── tests/                  # Synthetic unit and integration tests
├── docs/                   # Development, test and assessment evidence
│   └── screenshots/        # Genuine screenshots to be captured manually
├── data/                   # Created on first save; excluded from Git
├── requirements.txt
└── .gitignore
```

The existing package layout is retained; there is no second nested project.

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

```powershell
.\.venv\Scripts\python.exe main.py
```

With the environment activated, the equivalent command is `python main.py`.
Choose a numbered option and follow the prompts. Use option 0, Ctrl+C or EOF
to exit. A partially entered record is not saved.

To use an isolated file for a demonstration with synthetic data:

```powershell
.\.venv\Scripts\python.exe main.py --data-file data\demo.json
```

The normal file is `data/fitfor_data.json` relative to the project directory,
even when the program is launched from another directory. An explicitly
supplied relative `--data-file` path is relative to the current directory.
The directory/file is created when an entry is first saved.

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
safe deletion and real entry-point subprocesses. Tests use synthetic data and
temporary directories rather than the normal user data file.

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
  [live smoke-test transcript](docs/final-smoke-test.txt): actual final runs
  operated by Codex, using synthetic data.
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

## Limitations

- CLI only; one local user and one writer at a time. Concurrent instances can
  overwrite each other's changes; atomic saves are not a locking mechanism.
- No authentication, encryption, external services or nutrition database.
- No edit, export, undo, automatic backup or automatic corruption repair.
- IDs are unique within a current collection; they may be reused after deletion
  and are not permanent audit identifiers.
- Workout/meal models hold data; validation occurs at input/storage boundaries.
- No medical recommendations, diagnosis or diet prescriptions.

## Possible future development

Potential extensions include SQLite, a GUI/web interface, authentication,
encrypted storage and richer analytics. None is part of this implementation.
