# FitFor testing evidence

## Verified scope

On 22 October 2026 (session date), Codex ran:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Environment: Python 3.12.10, pytest 9.1.1. Latest full-suite result:
**88 passed, 0 failed** (models and validation). All test entries are synthetic.
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
