# FitFor threat model

Scope: one person running a local CLI, with plain-text JSON storage. There is
no application authentication, encryption, cloud service or network API.
This table describes limited controls and remaining risks, not a guarantee
of security. All examples in the tests and documentation are synthetic.

| Asset | Threat | Vulnerability | Mitigation | Residual user-dependent risk |
| --- | --- | --- | --- | --- |
| Workout and meal records | Accidental permanent deletion | **Human:** selecting the wrong ID or confirming without reading | Show the full name, date and ID; require explicit y; invalid, blank, EOF and Ctrl+C do not delete | A user can still deliberately confirm the wrong entry; no undo or automatic backup |
| Private notes | Disclosure of unnecessary sensitive information | **Human:** entering passwords, financial or medical details in free text | Menu 9 advises data minimisation; notes are optional | Guidance cannot detect or prevent sensitive text being entered |
| Shared files and screenshots | Oversharing fitness information | **Human:** sharing an unreviewed screenshot or data file | Protect Your Progress prompts users to review content before sharing; default data directory is Git-ignored | Users can override ignore rules, choose another data path or share files themselves |
| Backups | Disclosure or loss through insecure copies | **Human:** storing backups in shared locations or without access controls | In-app advice to store backups securely and restrict account/folder access | FitFor does not create, encrypt, verify or manage backups |
| Stored JSON | Partial save after interruption or write failure | Directly overwriting an existing file would truncate it | Flush a temporary sibling file, then atomically replace the destination; write-failure regression test | A failed operation may not save the latest change; disk loss and concurrent writers are outside this design |
| Stored JSON | Lost or misinterpreted records after corruption | Invalid encoding, malformed schema, duplicate keys/IDs or invalid values | Reject invalid records and show an error without silently resetting or overwriting the file | User must restore a trusted backup or repair the file; no automatic recovery |
| Local records | Access by another device user | Clear-text file and no application login | Explain the limitation and advise use of OS account/folder access controls | Anyone with file access can read or change records; device security remains the user's responsibility |

Relevant evidence: `tests/test_privacy.py`, `tests/test_cli.py`,
`tests/test_storage.py` and `docs/testing.md`.

The JSON store supports a single writer. Atomic replacement reduces partial
write risk; it is not protection against two instances overwriting each
other's changes. IDs identify current records within a collection and may be
reused after records are deleted; they are not permanent audit identifiers.
