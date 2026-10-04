# File Preservation — Dunder + manifest preserve

> Two mechanisms keep user files alive across deploys. They are intentionally
> separate, not duplicates. Source: `zekniri/deploy/atomic.py`.

## Mechanism 1: Dunder `__custom__`

Before the swap, `atomic_replace_item` walks the **destination** and carries
forward every file and directory whose name contains `__custom__` (any depth).
It is independent of which source is deployed. Print `log_keep_custom_file` /
`log_keep_custom_dir`.

- Applies to files (copied, or symlink kept as a symlink).
- Applies to directories (whole tree).
- `preserve_custom=False` disables it (exact-restore mode).

Preservation and loading are decoupled: the engine only *keeps* the file. Each
app *loads* it with its own include syntax. To split tweaks across files, have
your main custom file include the others — the sub-files stay preserved because
their names also contain `__custom__`.

## Mechanism 2: manifest `preserve`

`.module.toml` may declare `preserve = ["monitor.conf", "effects.conf"]`. Before
the rename, those exact files are copied from the destination into the new tree.
If a preserved entry is a symlink, the link itself is kept (not dereferenced), so
runtime link state survives.

This is for files that are **referenced by exact name** and therefore cannot be
renamed into a `__custom__` name.

## Why not merge

| | Dunder | manifest preserve |
|---|---|---|
| Trigger | magic filename | explicit declaration |
| Whose | user's arbitrary files | fixed, name-referenced files |
| Walk | dest | dest, injected before rename |

Merging would force users to rename a name-referenced file — breaking the
include. Two mechanisms, two jobs.

## Race elimination

Manifest-preserved files are injected **before** the rename, so the directory
that appears at the destination path is already complete. File watchers never
observe a half-state (the old design renamed first and copied back after, which
could flash an empty default file).

## Template freeze (accepted cost)

A repo-shipped `__custom__` template (comment-only) is treated as a user file
after the first deploy, so later wording changes to it never reach installed
users. This is the price of "never touch anything the user may have edited".
Because the templates are comments only, nothing functional is lost.
