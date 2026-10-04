"""Network operations — git pull with timeouts and graceful degradation.

Every network call must carry a connect timeout and degrade instead of
crashing. A failed update is a message, not a traceback.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from zekniri.core import get_env, log_msg, timed_run
from zekniri.i18n import msg

_GIT_CONFIG = [
    "-c", "http.lowSpeedTime=15",
    "-c", "http.lowSpeedLimit=1000",
    "-c", "http.connectTimeout=10",
    "-c", "http.timeout=30",
]


def _build_pull_cmd(repo_dir: Path, quiet: bool) -> list:
    cmd = ["git", *_GIT_CONFIG, "-C", str(repo_dir), "pull", "--ff-only"]
    if quiet:
        cmd.append("--quiet")
    return cmd


def _run_git_pull(repo_dir: Path, quiet: bool) -> Optional[int]:
    """Construct and run the pull command. Returns the exit code or None."""
    cmd = _build_pull_cmd(repo_dir, quiet)
    log_msg("INFO", f"git pull: {' '.join(cmd)}")
    devnull = subprocess.DEVNULL if quiet else None
    res = timed_run(cmd, timeout=120, stdout=devnull, stderr=devnull, check=False)
    if res is None:
        return None
    return res.returncode


def safe_git_pull(repo_dir: Path) -> Optional[bool]:
    """Pull the repo. Returns True (ok), False (failed) or None (not applicable).

    System-package installs are refused: pacman owns their update path.
    """
    env = get_env()
    if env.run_mode == "system":
        print(msg("update_use_pacman"))
        return None

    if not (repo_dir / ".git").is_dir():
        print(msg("update_no_git"))
        return False

    quiet = not sys.stdout.isatty()
    code = _run_git_pull(repo_dir, quiet=quiet)
    if code is None:
        print(msg("update_timeout"), file=sys.stderr)
        return False
    return code == 0
