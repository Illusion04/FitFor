# Protect Your Progress

## Audience and delivery

This small awareness campaign is implemented inside FitFor as menu option 9,
**Privacy and data guidance**, and the desktop **Privacy** tab. The audience is people recording their own
fitness information on a local computer. The deletion preview reinforces
the same review-before-action message at the point of use.

## Four messages connected to the artefact

| Human risk | Message and action | Implemented delivery |
| --- | --- | --- |
| Accidental deletion | Pause; check the full date, name and ID before entering y | Deletion preview and explicit confirmation; cancellation preserves records |
| Oversharing | Review records and screenshots before sharing them | Menu 9 guidance |
| Unnecessary sensitive notes | Record only what is useful; avoid passwords, financial and medical details | Optional notes and menu 9 guidance |
| Insecure backups | Store backups securely and restrict access to the account/data folder | Menu 9 guidance and transparent storage limitations |

## Evaluation and evidence

Automated tests verify that the guidance is reachable and that confirmation
controls preserve records on cancellation or interruption. The actual final
live check is recorded in `docs/testing.md` and `docs/final-smoke-test.txt`.

Campaign reach, comprehension and behaviour change have not been measured.
Screenshots and any assessment evaluation must come from real use; no survey
results, user feedback or effectiveness claims are invented here.

The desktop enhancement also places full-target confirmations before GUI
deletions, defaulting to No. The Privacy tab covers the same four messages,
plain local storage and actual security limitations. Real-window rendering,
workout cancellation and confirmed deletions were observed and recorded in
`docs/gui-smoke-test.md`; this verifies delivery and control behaviour, not
campaign effectiveness.
