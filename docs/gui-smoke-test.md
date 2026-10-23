# FitFor desktop verification

## Baseline

23 October 2026: before GUI changes, the existing suite passed **182 tests,
0 failed** on Python 3.12.10. Tk 8.6 is available. Tests use synthetic data.

## Early verification (historical)

The initial shell launched successfully using
`python gui.py --data-file data/gui-assessment-smoke.json`. Windows discovery
returned its `FitFor - Workout & Nutrition Tracker` window. Initial capture
timed out awaiting app approval; the user then approved access. Actual captures
confirmed shell rendering and tab switching through Dashboard, Workouts and
Meals. The preview closed normally. Complete data workflows remain to be
checked after implementation; no unperformed workflow is claimed as passed.
No screenshot files have been saved yet.

The full suite after the shell milestone passed 182 tests, 0 failed.
Further milestone results and final workflow checks will be recorded here.

## Workout milestone

Full suite: **200 passed, 0 failed**, including 18 headless adapter cases.
Actual form/table rendering was inspected. The inspection identified footer
clipping; the outer layout was changed to a weighted grid. Final resizing and
complete save/delete flows will be checked against the finished application.
`python gui.py --help` passed without opening a Tk window.

## Completed native workflows — 23 October 2026

Test environment: Windows, Python 3.12.10, Tk 8.6. The real application window
was operated through Computer Use after the user approved access. These are
observed UI results, separate from headless pytest results.

Launch command (the default personal data file was not used):

```powershell
.\.venv\Scripts\python.exe gui.py --data-file data\gui-assessment-smoke.json
```

All inputs below are synthetic. The isolated file initially did not exist.
Reading it displayed zero summaries and friendly empty states. It was created
only after a successful save. The runtime file remains ignored by Git.

| Check | Observed result |
| --- | --- |
| Navigation and launch | All five tabs opened; the window closed normally without a traceback. |
| Empty exercise | Save showed `Exercise cannot be empty.`; application remained open. |
| Negative sets | `-1` showed `Sets must be a positive integer.`; other fields remained filled. |
| Non-number reps | `eight` showed `Reps must be a positive integer.`; form retained input. |
| Invalid calendar date | `2026-02-29` showed the valid-date/`YYYY-MM-DD` message. |
| Workout save | `2026-10-23`, Assessment press, 3 sets, 8 reps, 12.5 kg saved as ID 1. Form cleared; table displayed 300.00 volume and success status. |
| Persistence | Closing and reopening the GUI retained the saved workout; reopening also retained the later meal. |
| Workout dashboard/report | 1 exercise entry, 3 sets, 24 total reps and 300.00 kg × reps. |
| Negative calories | `-1` showed `Calories must be a non-negative integer.` without saving. |
| Negative protein | `-1` showed `Protein must be a finite, non-negative number.` without saving. |
| Meal save | Lunch / Assessment bowl, 520 kcal, 35 g protein, 60 g carbohydrates and 15 g fat saved as ID 1. Form cleared; table and success status updated. |
| Immediate dashboard refresh | Today's nutrition became 520 / 35.00 / 60.00 / 15.00. Both entries appeared in recent activity. |
| Nutrition report | All-date totals matched the meal; daily table showed the same totals for 2026-10-23. |
| Date filter | Start `2026-10-24` excluded both earlier entries, giving zero totals and no daily rows. All Dates restored both summaries. |
| No selected record | Delete Selected showed `Select a workout in the table first.`; no deletion occurred. |
| Cancel workout deletion | Confirmation showed type, ID, full name and date; No was the default. Pressing Enter cancelled and retained the table row. |
| Confirm workout deletion | Clicking Yes removed the selected workout and displayed `Workout deleted.` |
| Confirm meal deletion | Confirmation showed the meal ID, date and name; Yes removed the selected meal. |
| Refresh after deletions | Both lists became empty; Dashboard and Reports returned to zero, with no recent/daily rows. |
| Privacy | All guidance was readable: local JSON, no encryption/login, minimal notes, sharing, access controls, backups, review before deletion and no diagnosis. |
| Layout and resizing | Default 1100 × 740 layout and maximized/restored Reports were inspected. Tables and footer remained visible in the final layout. |

Visual issues found and fixed during this session: initially clipped footer,
small selected-tab padding, excessive meal form height and too little report
table space at display scaling. The final layout uses a weighted outer grid,
compact forms, dashboard tiles, compact report summaries and a single filter
bar. Minimum height is 740 logical pixels to preserve visible controls.

CLI interoperability was also exercised against the same GUI-created file:

```powershell
@'
2
5
0
'@ | .\.venv\Scripts\python.exe main.py --data-file data\gui-assessment-smoke.json
```

The CLI displayed Assessment press (3 × 8 × 12.50, volume 300.00) and Assessment
bowl (520 kcal, 35.00/60.00/15.00 g), then exited normally. After the GUI deletion
checks the isolated file contains no entries. No genuine personal record was
created, edited or deleted.

## Automated verification

Final integration run: `python -m pytest -v`: **229 passed, 0 failed** in 1.30 s.
All original 182 tests remain; 47 new tests cover GUI conversions, validation,
dashboard/report summaries, dates, safe deletion, shared CLI/GUI persistence,
corrupt-file preservation and launcher help. Full output:
[gui-pytest-results.txt](gui-pytest-results.txt).

Headless tests do not establish visual accessibility or behaviour on every
operating system. Numeric overflow, corrupt storage and changed/reused IDs
are covered automatically; those edge conditions were not injected into the
native smoke-test file. Meal cancellation is covered automatically; the native
cancellation check used a workout. Dedicated Clear Form buttons were not
separately exercised; automatic post-save clearing was observed on both forms.

## Screenshot evidence to capture

No screenshot files were saved or fabricated during this session. Actual
Computer Use captures were inspected in the conversation. For submission,
capture genuine screenshots using a separate synthetic data file:

1. Dashboard with both types of entry and today's nutrient totals.
2. Filled workout form before Save.
3. Saved workout row with calculated volume and success status.
4. Filled meal form or saved meal row with all nutrient fields.
5. Reports with summaries and the daily nutrition row.
6. Delete confirmation showing the full synthetic target and default No.
7. Protect Your Progress with all privacy guidance visible.
8. Terminal showing the full-suite result (229 passed in this run).

Review screenshots for unrelated personal information before including them
in assessment evidence. Add your own learning reflection; no student reflection
or campaign-effectiveness result was invented.
