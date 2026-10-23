# FitFor testing evidence

## Verified scope

On 22 October 2026 (session date), Codex ran:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Environment: Python 3.12.10, pytest 9.1.1. Pre-GUI full-suite result:
**182 passed, 0 failed**. The desktop enhancement on 23 October 2026 passed
**229 tests, 0 failed**, preserving all original cases. See the desktop section
below for the current result; the earlier stage results remain historical.
All test entries are synthetic.
Stage 1 originally passed 10 model tests; its results are retained below.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| M01 | Workout creation | Date, name, 3 sets, 8 reps, 12.5 kg | Fields retained; ID is None; notes empty | Matched | Pass |
| M02 | Workout optional fields | ID 7 and synthetic notes | Both values retained | Matched | Pass |
| M03 | Volume | 3 × 8 × 12.5 | 300.0 | 300.0 | Pass |
| M04 | Fractional load | 2 × 4 × 0.25 | 2.0 | 2.0 | Pass |
| M05 | Recorded zero load | 1 × 10 × 0.0 | 0.0 | 0.0 | Pass |
| M06 | Recalculation | Change reps from 8 to 10 at 3 sets and 12.5 kg | 375.0 | 375.0 | Pass |
| M07 | Read-only volume | Assign 5 to volume | AttributeError | AttributeError | Pass |
| M08 | Missing load | Omit weight_kg | Load and volume are None | Matched | Pass |
| M09 | Meal creation | Date, meal type, sample food, 520 kcal, 35 g protein | Required values retained; optional defaults applied | Matched | Pass |
| M10 | Meal optional fields | ID, carbohydrates, fat and synthetic notes | Values retained | Matched | Pass |

## Manual evidence

Live terminal checks after Steps 5–6 and 10 verified both complete
add/view/report/delete workflows through `main.py`, date filtering, invalid
input retries, privacy guidance, cancelled deletions, empty views and exit.
Isolated synthetic smoke files were removed afterwards. No screenshots have
been captured. The final live session was operated by Codex, not claimed as
student-authored manual evidence.

Actual captured output: [pytest results](pytest-results.txt) and
[final smoke-test transcript](final-smoke-test.txt).

## Step 2: Validation

The full suite passed 88 tests after this stage, including 78 validation cases.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| V01 | Dates | Leap date and surrounding whitespace | Correct date objects | Matched | Pass |
| V02 | Invalid dates | Impossible days, months, alternate formats and wrong types | Clear ValueError | Matched | Pass |
| V03 | Text | Trimmed names, blank required names and optional notes | Names required; blank notes allowed | Matched | Pass |
| V04 | Sets/reps | Integers, zero, negatives, fractions and booleans | Positive integers only; no truncation | Matched | Pass |
| V05 | Calories | Zero, positive integers, negatives and fractions | Non-negative integers only | Matched | Pass |
| V06 | Nutrients | Zero, decimals, text, NaN, infinities and overflowing numeric input | Finite non-negative numbers only | Matched | Pass |
| V07 | Load | Blank, zero, fractional, negative and non-finite values | None or valid non-negative kg | Matched | Pass |

## Step 3: Storage

Full suite: 118 passed, 0 failed; 30 storage cases use temporary directories.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| S01 | Missing/empty files | Load absent, blank or empty collections | Empty lists; reads create no files | Matched | Pass |
| S02 | Persistence | Add and reopen both record types with notes and nutrients | Equal records; ISO date in JSON; date object on load | Matched | Pass |
| S03 | IDs | Add multiple records to both collections | Unique positive IDs within each collection | Matched | Pass |
| S04 | Optional load | Save an entry without weight | JSON null and None restored | Matched | Pass |
| S05 | Deletion | Delete an ID and a missing ID | Only selected collection changes; missing ID returns False | Matched | Pass |
| S06 | Invalid IDs/schema | Booleans, duplicate IDs, invalid fields and malformed JSON | Clear error; existing data not overwritten | Matched | Pass |
| S07 | Invalid model | Set sets to zero before saving | Save rejected; existing bytes unchanged | Matched | Pass |
| S08 | Write failure | Simulate failure during atomic replacement | Existing bytes retained; temporary file cleaned up | Matched | Pass |

## Step 4: Reports

Full suite: 132 passed, 0 failed; 14 report cases.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| R01 | Workout totals | Three entries across two dates, including an unknown load | 3 entries, 2 days, 2 exercise names, 7 sets, 54 reps, 500.0 volume | Matched | Pass |
| R02 | Empty data | Empty workout/meal inputs | Zero totals and no daily groups | Matched | Pass |
| R03 | Date filtering | Single-day and open-ended ranges | Inclusive boundaries; no out-of-range entries | Matched | Pass |
| R04 | Load interpretation | Recorded zero load vs omitted load | Zero counted as recorded; missing load excluded | Matched | Pass |
| R05 | Nutrition | Three synthetic meals | 820 kcal, 50 g protein, 100.75 g carbs, 22.5 g fat | Matched | Pass |
| R06 | Daily totals | Unordered dates | Correct daily totals in ascending date order | Matched | Pass |
| R07 | Invalid range | Start date after end date for all report APIs | Clear ValueError | Matched | Pass |
| R08 | Numeric/input boundaries | Fractional nutrients and single-use iterators | Correct rounded totals; no lost entries | Matched | Pass |

## Step 5: CLI menu

Full suite: 146 passed, 0 failed; 14 CLI cases.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| C01 | Workout workflow | Add, view and report a sample entry | Saved ID, displayed entry and 300.0 volume | Matched | Pass |
| C02 | Meal workflow | Add, view and report a sample meal | Saved nutrients, 520 kcal and daily totals | Matched | Pass |
| C03 | Input retries | Invalid choice, date, text, sets, reps and weight | Errors explained; valid retry saved | Matched | Pass |
| C04 | Deletion | n, yes, blank, invalid, y and absent ID | Only explicit y deletes an existing target | Matched | Pass |
| C05 | Empty collections | View and report no records | Clear empty messages and zero totals | Matched | Pass |
| C06 | Corrupt storage | View invalid JSON | Error shown; file unchanged; menu remains usable | Matched | Pass |
| C07 | Cancellation | EOF and Ctrl+C during entry | Normal exit; no partial record saved | Matched | Pass |
| C08 | Live menu smoke check | Enter invalid, then 0 in a real terminal session | Retry message then Goodbye and exit | Observed | Pass |

## Step 6: Entry point and live flows

Full suite: 149 passed, 0 failed; three entry-point subprocess tests.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| E01 | Startup/exit | Launch main.py with temporary path and enter 0 | Exit 0; no unnecessary data file | Matched | Pass |
| E02 | Main guard | Import main in a subprocess | Import completes without launching menu | Matched | Pass |
| E03 | Restart persistence | Add both types, restart, view/report/delete | Saved records survive; correct totals; empty after deletion | Matched | Pass |
| E04 | Live workout flow | Add 3 × 8 × 12.5, view, report, confirm deletion | Displayed entry, 300.0 volume, successful delete | Observed | Pass |
| E05 | Live meal flow | Add 520 kcal, 35 g protein, 60.5 g carbs, 15 g fat; view/report/delete | Correct entry and nutrient totals; successful delete | Observed | Pass |

The Step 6 live meal table wrapped at 80 columns. This was resolved and
verified with a compact display in Step 10.

## Step 7: Test audit and regression fixes

The expanded run initially produced **162 passed, 6 failed**. Two duplicate-key
cases and four numeric-overflow cases exposed defects. After the fixes, the
full suite produced **168 passed, 0 failed**. No coverage tool was added.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| A01 | Meal corruption | Negative nutrients/calories, wrong types, empty names | Save blocked; existing bytes unchanged | Matched | Pass |
| A02 | Unreadable storage | Invalid UTF-8, directory path and simulated denied read | Clear StorageError; no reset | Matched | Pass |
| A03 | Model date type | Try saving a string instead of date | Rejected before file creation | Matched | Pass |
| A04 | Duplicate JSON keys | Repeated collection keys | Reject and preserve original bytes | Failed initially; fixed and passed | Pass |
| A05 | Numeric overflow | Extreme load, huge set count and overflowing nutrient sum | Clear numeric-range ValueError | Failed initially; fixed and passed | Pass |
| A06 | Meal retries | Invalid names, calories and each nutrient | Retry only invalid fields; save valid entry | Matched | Pass |
| A07 | Report retries | Invalid date and reversed range | Explain error; accept corrected date range | Matched | Pass |

## Step 8: Privacy and safe deletion

Full suite: 180 passed, 0 failed; 12 additional privacy/control cases.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| P01 | Target review | Select each record type with a long name | Full date/name/ID precedes confirmation | Matched | Pass |
| P02 | Explicit confirmation | Enter y with surrounding whitespace and uppercase | Only the selected record type is deleted | Matched | Pass |
| P03 | Safe default | Enter n, N, yes, blank or invalid for a meal | Cancellation; both collections unchanged | Matched | Pass |
| P04 | Interrupted confirmation | EOF/Ctrl+C for either record type | No deletion | Matched | Pass |
| P05 | Privacy guidance | Choose menu option 9 | Human-risk guidance and actual login/encryption limitations displayed | Matched | Pass |

The threat model and campaign document describe implemented controls and
residual risks. Campaign effectiveness has not been measured.

## Step 9: Documentation review

Required full-suite rerun: **180 passed, 0 failed**. No runtime code was changed
for this stage and no tests were added merely to mirror documentation text.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| D01 | README accuracy | Compare instructions/features with source and earlier live checks | Reproducible commands; implemented features only | Reviewed and matched | Pass |
| D02 | Evidence provenance | Review assessment checklist and linked documents | Personal reflection, screenshots and external assessment tasks left pending | Matched | Pass |

## Step 10: Final audit and live smoke test

The final full suite passed **182 tests, 0 failed**. Two new regression tests
cover full names in views and safe rejection of deeply nested storage. The
first cleanup run passed 181 tests with one over-specific error-message
assertion failure; correcting that assertion produced the final passing run.

The following were observed in a real terminal session using a newly created
synthetic data file, then repeated default startup/exit. The actual transcript
is retained; no screenshots or user feedback are fabricated.

| Test ID | Feature | Input/action | Expected result | Actual result | Pass/fail |
| --- | --- | --- | --- | --- | --- |
| F01 | Invalid menu choice | Enter invalid | Explain and show menu again | Observed | Pass |
| F02 | Invalid date/sets | Enter 2026-02-29 and sets 0, then correct them | Reject invalid values and retry fields | Observed | Pass |
| F03 | Workout add/view/report | Add 3 × 8 × 12.5 on 2026-10-22; filter to that date | Saved ID 1; 24 reps; volume 300.0 | Observed | Pass |
| F04 | Meal add/view/report | Add 520 kcal, 35/60.5/15 g nutrients; filter to date | Correct entry, total and daily values | Observed | Pass |
| F05 | Meal display | View the sample meal in an 80-column terminal | Table/nutrient details fit without the prior wrapping | Observed | Pass |
| F06 | Privacy guidance | Choose 9 | Protect Your Progress messages and actual limitations | Observed | Pass |
| F07 | Cancel workout deletion | Inspect preview; enter n; view again | Record remains | Observed | Pass |
| F08 | Invalid meal confirmation | Inspect preview; enter invalid; view again | Record remains | Observed | Pass |
| F09 | Confirm deletion | Preview each record and enter y | Only target deleted; both final views empty | Observed | Pass |
| F10 | Exit/default startup | Enter 0; separately launch main.py normally and exit | Goodbye; return code 0 | Observed | Pass |
| F11 | Full-name/deep-data regressions | Run new automated tests | Full names available; invalid nested storage preserved | Matched | Pass |
| F12 | Repository hygiene | Inspect tracked files and check-ignore output | No runtime/private data, environments or caches tracked | Matched | Pass |
| F13 | Step 1 preservation | Compare model code/tests to babd4ea | No changes | Matched | Pass |

Screenshots and personal learning reflections remain student actions. The
threat table covers controls and residual risks; it is not a claim that the
application is fully secure or that campaign effectiveness was measured.

## Desktop enhancement: automated and native verification

23 October 2026, Python 3.12.10 / Tk 8.6 / pytest 9.1.1:

| GUI milestone | Full suite passed | Failed | New cases at that milestone |
| --- | ---: | ---: | ---: |
| Shell/navigation | 182 | 0 | 0 |
| Workout management | 200 | 0 | 18 |
| Meal management | 211 | 0 | 11 |
| Dashboard | 214 | 0 | 3 |
| Reports | 224 | 0 | 10 |
| Privacy/feedback | 224 | 0 | 0 |
| Integration | 229 | 0 | 5 |

`tests/test_gui_support.py` exercises shared-validator conversion, blank
optional values, invalid dates/text/numbers, report/date calculations,
unknown loads, overflow, ordering and safe confirmation. Deletion tests
reject missing/changed/reused IDs and preserve other records/collections.
`tests/test_gui_integration.py` verifies GUI-to-CLI viewing/reporting,
CLI-to-GUI summaries/deletion, corrupt-file preservation and launcher help.
All new tests are headless and use temporary synthetic files.

The native Windows window was operated through Computer Use with user approval.
Observed workflows included valid saves, automatic form clearing, retained
invalid values, six required validation messages, persistence after restart,
both dashboards/reports, daily nutrition totals, date filtering, no selection,
default-No cancellation, confirmed deletion of both types, privacy guidance,
maximize/restore and clean exit. The existing CLI also read both GUI-created
records from the same isolated JSON file. No private/default records were used.

The native test found layout clipping that automated logic tests could not
detect; compact forms/filters and a minimum logical height corrected it.
Full observations and explicit limits: [GUI smoke test](gui-smoke-test.md).
Complete integration run output (229 passed in 1.30 s):
[GUI pytest results](gui-pytest-results.txt).

These results were agent-operated, not claimed as student-authored testing or
personal reflection. Screenshot files and student learning entries remain
pending. Historical CLI evidence files are retained without relabelling them
as desktop evidence.
