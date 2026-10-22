# FitFor development log

This records implementation and verification performed by Codex. It does not
claim to be the student's personal learning log. Reflection prompts must be
completed by the student in their own words.

## Repository inspection

- Date: 22 October 2026 (session date).
- Task: Inspect the existing repository before making changes.
- Files changed: None during inspection.
- Findings: Clean `master` branch tracking `origin/master`; origin is
  `https://github.com/Illusion04/FitFor.git`; setup commit `423ea17`.
  The `fitfor` package, entry point and existing test modules were empty.
- Problem encountered: Sandboxed commands could not access the virtual
  environment's base Python installation.
- How it was solved: Ran the existing virtual environment with approved access
  outside the sandbox; confirmed Python 3.12.10 and pytest 9.1.1.
- Tests performed: Baseline pytest run collected no tests.
- Git commit: Existing `423ea17` (`chore: project setup`).
- What I learned: Student reflection pending; consider why repository and
  environment checks come before implementation.

## Step 1: Data models

- Date: 22 October 2026 (session date).
- Task: Implement workout and meal models without UI or persistence logic.
- Files changed: `fitfor/models.py`, `tests/test_models.py`, this log and
  `docs/testing.md`.
- What was implemented: Dataclasses retaining the earlier field names, optional
  IDs and notes, meal carbohydrates/fat, and a read-only workout volume property.
  Volume is sets × reps × recorded load; an unrecorded load produces `None`.
  This is a recorded-load calculation, not total physiological workload.
- Problem encountered: The new brief adds notes and nutrients to the earlier
  model specification and permits exercises without a recorded load.
- How it was solved: Kept the earlier constructor arguments compatible and
  added defaulted fields. Distinguished missing load from a recorded zero load.
- Tests performed: `python -m pytest -v` using `.venv\Scripts\python.exe`;
  10 passed, 0 failed. All inputs were synthetic.
- Git commit: `feat: add Workout and Meal models` (see Git history for the hash).
- What I learned: Student reflection pending; explain dataclass defaults,
  `int | None`, and why a calculated property avoids stale stored values.

## Step 2: Input validation

- Date: 22 October 2026 (session date).
- Task: Centralise date, text, integer, nutrient and optional-load validation.
- Files changed: `fitfor/validation.py`, `tests/test_validation.py`, this log
  and `docs/testing.md`.
- What was implemented: Strict YYYY-MM-DD parsing, trimmed required/optional
  text, positive sets/reps, non-negative integer calories, finite non-negative
  nutrient values, and blank load handling. Errors name the offending field.
- Problem encountered: Python treats booleans as integers, permits non-finite
  floats, and accepts some ISO date forms outside the requested format.
- How it was solved: Reject booleans, check finiteness, require the explicit
  date pattern, and avoid truncating fractional integer inputs.
- Tests performed: Full `python -m pytest -v` run: 88 passed, 0 failed.
- Git commit: `feat: add input validation for workouts and meals`.
- Repository note: Fetch succeeded after manual authentication. At inspection,
  `origin/master` still pointed to `423ea17`; the normal push will also include
  the existing Step 1 commit `babd4ea`.
- What I learned: Student reflection pending; consider why parsing boundaries
  need tests for types, formats and non-finite numbers.

## Step 3: JSON storage

- Date: 22 October 2026 (session date).
- Task: Persist both collections locally without mixing storage and UI.
- Files changed: `fitfor/storage.py`, `tests/test_storage.py`, `.gitignore`,
  this log and `docs/testing.md`.
- What was implemented: Lazy directory creation on save, load/add/delete APIs,
  assigned IDs, ISO dates, validated JSON records and atomic file replacement.
  Empty/missing storage loads as empty; corrupt storage raises a clear error
  and is not silently reset. Runtime data and environment files are ignored.
- Problem encountered: Truncating a file before completing a write risks
  losing existing records; malformed records must not be silently discarded.
- How it was solved: Write and flush a temporary sibling file before replacing
  the destination, and validate both collections before any save.
- Tests performed: Full suite: 118 passed, 0 failed, including 30 storage cases
  using temporary directories and a simulated replacement failure.
- Git commit: `feat: add persistent JSON storage`.
- What I learned: Student reflection pending; compare atomic replacement with
  overwriting a file directly and explain the limits of single-writer storage.

## Step 4: Reports

- Date: 22 October 2026 (session date).
- Task: Calculate workout and nutrition summaries independently of the CLI.
- Files changed: `fitfor/reports.py`, `tests/test_reports.py`, this log and
  `docs/testing.md`.
- What was implemented: Entry/day/exercise counts, total sets and repetitions
  across sets, recorded-load volume, total kcal/macronutrients, daily nutrition
  totals, and inclusive optional date boundaries.
- Problem encountered: Exercise entries do not represent whole workout
  sessions, and missing loads must not imply known zero workload.
- How it was solved: Report entries and recorded days separately; report both
  known-load and missing-load entry counts. Document the volume formula.
- Tests performed: Full suite: 132 passed, 0 failed; 14 report cases verify
  exact totals, empty inputs, range boundaries, rounding and generators.
- Git commit: `feat: add workout and nutrition reports`.
- What I learned: Student reflection pending; explain why returned results and
  explicit metric definitions make reports easier to test and interpret.

## Step 5: Interactive menu

- Date: 22 October 2026 (session date).
- Task: Implement the menu in the existing `fitfor/cli.py` module.
- Files changed: `fitfor/cli.py`, `tests/test_cli.py`, this log and
  `docs/testing.md`.
- What was implemented: Add/view/delete workflows, field retries, optional
  notes/load, date-filtered reports, aligned tables, confirmation before
  deletion, and graceful EOF/Ctrl+C and storage-error handling.
- Problem encountered: Input interrupted midway through entry must not leave
  partial records, and invalid input should not terminate the menu.
- How it was solved: Gather and validate a complete entry before saving; catch
  expected errors at the UI boundary. Supply input/output functions in tests.
- Tests performed: Full suite: 146 passed, 0 failed, including 14 CLI cases.
  Live terminal check: invalid choice returned to the menu; `0` exited normally.
- Git commit: `feat: add interactive FitFor CLI menu`.
- What I learned: Student reflection pending; explain the separation between
  prompts, validation, persistence and calculations.

## Publication status during development

The Step 2 push returned `Cannot prompt because user interactivity has been
disabled` / `unable to get password from user`. Commits `babd4ea` and `8d3da7a`
were still local at that attempt. The Step 3 push failed for the same reason;
`e01b1fe` is also pending. The Step 4 push also failed with that error, leaving
`da6fa38` local. Development continues under the user's updated
instruction. Credentials are not modified; each stage attempts a normal push.
The final audit will list all commits still awaiting manual publication.
