# Testing — isolation, shapes

> Source: `tests/`. Every test uses `tests/utils.py:TempEnv`.

## Isolation (iron law)

**All tests must use `TempEnv`. Never touch the real `~/.config` / `~/.local` /
`~/.cache`.**

`TempEnv`:

- points `HOME` and the `XDG_*` variables at a throwaway directory,
- creates `~/.config`, `~/.local/bin`, `~/.local/state/<project>`, `~/.cache`,
- creates a per-test `configs/` + `assets/` source tree (so tests never read or
  write the real repo),
- resets `core._ENV`, `core._VERSION_CACHE`, `core._LOG_FILE`, the manifest
  cache, the deploy config-item cache, the deps pacman cache, and the i18n
  language cache.

## Test shapes

| Area | Shape | File |
|---|---|---|
| atomic swap | dir swap, `__custom__` file/dir kept, `preserve` by name, symlink kept, failure rollback | `test_atomic.py` |
| manifest | defaults, overrides, sidecar, optional merge, hidden skip, bad toml non-fatal | `test_manifest.py` |
| deploy | copy, custom survives redeploy, chmod glob, manifest not shipped, missing source | `test_deploy.py` |
| snapshots | create/list, rollback, delete, prune to max | `test_backup.py` |
| uninstall | keep-data vs purge | `test_uninstall.py` |
| i18n | zh/en identical keys, no missing, no orphans | `test_i18n.py` |
| cli | handler exit codes, invalid args, config-mode deploy | `test_cli.py` |
| doctor | runs without crashing, report written | `test_doctor.py` |

## Required commands

```bash
python3 -m compileall zekniri tests
bash -n install.sh
python3 -m unittest discover -s tests -q
HOME=$(mktemp -d) ./install.sh test
```
