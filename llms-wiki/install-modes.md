# Install Modes — repo / cache / system

> "Where you run it is the mode it is." Detection lives in
> `zekniri/core.py:_detect_run_mode` and `Environment.__init__`.

| How | `repo_dir` | `run_mode` | `mode_label` | update |
|---|---|---|---|---|
| `git clone` + `./install.sh` | the clone path | `repo` | Local Path | `git pull` |
| `curl \| bash` | `~/.cache/<PROJECT_NAME>` | `standalone` | Remote Cache | `git pull` |
| packaged (`/usr/share/<project>`) | that path | `system` | System Package | package manager |

## Detection order

```python
if (root_dir / ".system-install").is_file():              → system
elif root_dir.resolve() == cache_dir.resolve():           → standalone
elif (root_dir / "configs") and (root_dir / "assets"):    → repo
else:                                                      → standalone
```

The `.system-install` marker is checked first: a package that also ships
`configs/` + `assets/` would otherwise be misread as `repo`. A package build
creates the marker.

## Update handoff (re-exec first)

After a successful `git pull`, the current process does **not** deploy. It
re-execs itself with `PENDING_UPGRADE_ENV` set (and `PENDING_UPGRADE_MENU_ENV`
when the update came from the interactive panel) so the deploy runs on the
freshly pulled engine code. Reason: the pull rewrote the engine files on disk
while the running process still holds the old modules; a lazy import after the
pull would fail with `ModuleNotFoundError`.

`zekniri/__main__._run()` catches `zekniri.*` `ModuleNotFoundError` (a mixed or
interrupted tree) and prints one actionable line instead of a traceback.

## CLI link

`~/.local/bin/<CLI_CMD>` is a symlink to the `install.sh` of whichever tree you
ran. In `system` mode this is a no-op: the package owns the entry point. A stale
user link that shadows a system package is warned about by
`check_path_occlusion()` at the top of `update` and `doctor`.
