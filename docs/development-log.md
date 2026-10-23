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

## Step 6: Application entry point

- Date: 22 October 2026 (session date).
- Task: Start the existing package from a small `main.py`.
- Files changed: `main.py`, `tests/test_main.py`, this log and `docs/testing.md`.
- What was implemented: Main guard, storage/menu initialisation and an optional
  `--data-file` argument for isolated data files. The default path is anchored
  to the repository rather than the current working directory.
- Problem encountered: Full-program checks must not touch normal user data.
- How it was solved: Run subprocess tests against pytest temporary paths and
  the live terminal check against a new, dedicated synthetic JSON file.
- Tests performed: Full suite: 149 passed, 0 failed. Subprocesses verified
  import safety, startup/exit, persistence across restart and both CRUD/report
  flows. Live terminal flows also passed (300.0 volume, 520 kcal, both deletions).
  The synthetic smoke file was inspected as empty and removed afterwards.
- Observation for final cleanup: The meal table wraps on an 80-column terminal.
- Git commit: `feat: add FitFor application entry point`.
- What I learned: Student reflection pending; explain the main guard and why
  test storage must be separate from normal records.

## Step 7: Automated test audit

- Date: 22 October 2026 (session date).
- Task: Audit coverage of required behaviour and add useful boundary cases.
- Files changed: Storage/report modules and tests, CLI/validation tests, this
  log and `docs/testing.md`. Step 1 models were not changed.
- What was implemented: Additional checks for invalid meal records, UTF-8 and
  read errors, duplicate JSON keys, report overflow and CLI retries.
- Problem encountered: The expanded run exposed six failures: duplicate keys
  were accepted silently and extreme totals returned infinity or OverflowError.
- How it was solved: Reject duplicate JSON keys during parsing and translate
  report overflow/non-finite totals into clear ValueError messages.
- Tests performed: Initial expanded run: 162 passed, 6 failed. After fixes:
  168 passed, 0 failed. No coverage dependency was added.
- Git commit: `test: expand automated FitFor test coverage`.
- What I learned: Student reflection pending; describe a failing regression
  case, the defect it revealed and how its passing rerun supports the fix.

## Step 8: Privacy and deletion controls

- Date: 22 October 2026 (session date).
- Task: Connect genuine in-app privacy controls to the assessment threat model.
- Files changed: `fitfor/cli.py`, `tests/test_privacy.py`,
  `docs/threat-model.md`, `docs/privacy-campaign.md`, this log and testing notes.
- What was implemented: Menu 9, Protect Your Progress guidance, full target
  date/name/ID preview before permanent deletion, and explicit confirmation.
- Problem encountered: Truncated table names are insufficient when deciding
  which record to delete, and guidance must not imply encryption or a login.
- How it was solved: Preview the full target before asking; cancel on every
  non-y response or interruption. State actual privacy limitations clearly.
- Tests performed: Full suite: 180 passed, 0 failed; 12 new privacy/control
  cases verify preview order, target selection, cancellation and guidance.
- Git commit: `feat: add privacy guidance and safe deletion controls`.
- What I learned: Student reflection pending; relate the implemented controls
  to human vulnerabilities and explain the residual risks in the threat table.

## Step 9: README and assessment documentation

- Date: 22 October 2026 (session date).
- Task: Document only implemented features and genuine evidence.
- Files changed: `README.md`, `docs/assessment-checklist.md`, this log and
  `docs/testing.md`.
- What was implemented: Setup/run/test instructions, architecture, metric
  definitions, local-data/recovery guidance, limitations, evidence links and
  a clear list of remaining student assessment actions.
- Problem encountered: Agent implementation activity must not be presented as
  personal reflection, fabricated screenshots or measured campaign success.
- How it was solved: State evidence provenance and leave those items pending.
- Tests performed: Full suite: 180 passed, 0 failed. Documentation reviewed
  against actual modules, commands, privacy controls and storage behaviour.
- Git commit: `docs: complete FitFor project documentation`.
- What I learned: Student reflection pending; explain how truthful limitations
  and reproducible instructions support professional software documentation.

## Step 10: Final cleanup and smoke testing

- Date: 22 October 2026 (session date).
- Task: Audit the repository, fix observed display defects and verify the
  completed application without changing its architecture.
- Files changed: CLI/storage/report presentation and error handling, package
  docstring, entry-point formatting, relevant tests and assessment evidence.
  Step 1 model code and tests remain unchanged from `babd4ea`.
- What was implemented: Compact meal rows, full-name details beneath truncated
  table cells, nested-JSON error handling and wrapped Python lines. Actual
  final output is deliberately included as assessment evidence in
  `docs/pytest-results.txt` and `docs/final-smoke-test.txt`; runtime JSON is not.
- Problem encountered: The live 80-column meal table wrapped, and table
  truncation hid long names. A new nested-data test initially required a parser
  message even though schema validation had safely rejected the file.
- How it was solved: Move nutrients to a detail line, show full long names and
  test the storage-error/preservation contract without prescribing the layer.
- Tests performed: Final full suite: 182 passed, 0 failed. The earlier cleanup
  run had 181 passed and one over-specific assertion failure, corrected before
  commit. Final live checks passed both CRUD/report flows, invalid input,
  privacy guidance, cancellation, explicit deletion, empty views and exit.
  Default `main.py` startup/exit also passed. Both isolated smoke files were
  removed after checking that their synthetic collections were empty.
- Repository audit: Tracked files contain no environment, caches, secrets or
  runtime data. Ignore rules cover the environment, caches, `.env` and `data/`.
  Python source/test lines are at most 79 characters. No dependencies added,
  branches renamed, history rewritten or credentials changed.
- Git commit: `chore: prepare FitFor for final PFD200 assessment`.
- What I learned: Student reflection pending; discuss final verification,
  evidence provenance and remaining single-writer/plain-text storage limits.

## Publication status during development

Read-only fetch succeeded. All normal push attempts in Steps 2–9 returned:

```text
fatal: Cannot prompt because user interactivity has been disabled.
fatal: unable to get password from user
```

The last refreshed `origin/master` was `423ea17`. Before the final cleanup
commit, these implementation commits were pending publication:

```text
babd4ea feat: add Workout and Meal models
8d3da7a feat: add input validation for workouts and meals
e01b1fe feat: add persistent JSON storage
da6fa38 feat: add workout and nutrition reports
3b879ba feat: add interactive FitFor CLI menu
2582d9e feat: add FitFor application entry point
6f28841 test: expand automated FitFor test coverage
5385e8b feat: add privacy guidance and safe deletion controls
1680f5f docs: complete FitFor project documentation
```

The final cleanup commit also receives a normal push attempt; its outcome and
hash are reported in the session handoff. Obtain the current complete pending
list with `git log --oneline origin/master..HEAD`. Development continued under
the user's updated instruction; credentials and history were not modified.

## Desktop enhancement: repository inspection and baseline

- Date: 23 October 2026 (session date).
- Task: Inspect the working CLI before adding the requested Tkinter interface.
- Files inspected: Models, validation, storage, reports, CLI, entry point,
  existing tests, README, requirements and ignore rules.
- Findings: Clean `master`, tracking `origin/master` at `84f49ab`; the expected
  FitFor remote is configured. Earlier pending-push notes above are historical.
  Python 3.12.10 includes Tk 8.6. Existing business APIs are suitable for reuse.
- Tests run: Pre-GUI `python -m pytest`: 182 passed, 0 failed in 0.86 seconds.
- Implementation decision: Preserve CLI and JSON format. Add a separate GUI
  launcher and small, headless GUI adapters where they enable useful tests.
- Commit: Baseline is the existing `84f49ab`; GUI milestone commits follow.
- What was learned: Student reflection pending; explain why confirming a
  baseline matters before extending an application through another interface.

## GUI milestone 1: Shell and navigation

- Date: 23 October 2026 (session date).
- Task: Add an independent Tkinter launcher and coherent application shell.
- Files changed: `gui.py`, this log and `docs/gui-smoke-test.md`.
- Implemented: Resizable 1100 × 740 window, five Notebook tabs, consistent ttk
  styles, header/status areas and the same default JSON path as the CLI.
- Problem encountered: Computer Use capture timed out awaiting app approval.
- Resolution: User approved access. Real-window captures confirmed the shell
  rendering and tab switching (Dashboard, Workouts and Meals). The preview
  closed normally before further development.
- Tests: Full suite after shell creation: 182 passed, 0 failed. Tk 8.6 available.
- Commit: `feat: add Tkinter application shell and navigation`.
- What was learned: Student reflection pending; explain the event loop and
  why an independent GUI entry point preserves the existing CLI.

## GUI milestone 2: Workout management

- Date: 23 October 2026 (session date).
- Task: Add the workout form, saved-record table, refresh and safe deletion.
- Files changed: `gui.py`, `fitfor/gui_support.py`,
  `tests/test_gui_support.py`, this log and desktop verification notes.
- Implemented: Shared-validator form conversion, default date, optional load
  and notes, save/clear feedback, scrollable table and confirmation-driven
  deletion using the existing Storage API. Stale selections are rejected.
- Problem encountered: The real window exposed footer clipping when the table
  requested more height, and selected tabs inherited smaller theme padding.
- Resolution: Use a weighted outer grid and explicit selected-tab padding.
  Final resizing checks will follow when all views exist.
- Tests: 200 passed, 0 failed, including 18 new headless GUI adapter tests.
  Launcher --help passed. Actual workout form and empty table were inspected.
- Commit: `feat: add graphical workout management`.
- Publication: Shell commit `da20554` pushed successfully to origin/master.
- What was learned: Student reflection pending; explain mapping form text to
  existing models and why confirmation must precede the persistence call.
