# FitFor testing evidence

## Verified scope

On 22 October 2026 (session date), Codex ran:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Environment: Python 3.12.10, pytest 9.1.1. Latest full-suite result:
**132 passed, 0 failed** (models, validation, storage and reports).
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

No end-to-end CLI checks or screenshots have been performed for this stage.
The CLI and persistence layers are not implemented yet. Screenshots should be
captured from genuine runs after those features exist.

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
