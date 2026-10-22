# Protect Your Progress

## Audience and delivery

This small awareness campaign is implemented inside FitFor as menu option 9,
**Privacy and data guidance**. The audience is people recording their own
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
controls preserve records on cancellation or interruption. A live final
smoke test is recorded separately in `docs/testing.md` when performed.

Campaign reach, comprehension and behaviour change have not been measured.
Screenshots and any assessment evaluation must come from real use; no survey
results, user feedback or effectiveness claims are invented here.
