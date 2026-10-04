"""Static asset deployment.

Assets are repo-shipped static files (wallpapers, icons, whatever an app's
config points at). They are synced to ``~/.local/share/<PROJECT_NAME>`` with
no-clobber semantics: a file already present is left alone, so the user's own
files survive updates.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path

from zekniri.constants import PROJECT_NAME
from zekniri.core import get_env, log_msg


@dataclass
class AssetDeployResult:
    copied: int = 0
    skipped: int = 0
    destination: str = ""


def assets_present() -> bool:
    """True when the repo ships a non-empty assets tree (hidden files ignored)."""
    env = get_env()
    return env.assets_src.is_dir() and any(
        p for p in env.assets_src.iterdir() if not p.name.startswith(".")
    )


def _asset_destination() -> Path:
    env = get_env()
    return env.home / ".local/share" / PROJECT_NAME


def deploy_assets() -> AssetDeployResult:
    """No-clobber sync of ``assets/`` into ``~/.local/share/<PROJECT_NAME>``."""
    env = get_env()
    result = AssetDeployResult(destination=str(_asset_destination()))
    if not assets_present():
        log_msg("INFO", "No assets shipped; skipping asset deployment")
        return result

    dest_root = _asset_destination()
    dest_root.mkdir(parents=True, exist_ok=True)

    for src in env.assets_src.rglob("*"):
        if src.is_dir() or src.name.startswith("."):
            continue
        rel = src.relative_to(env.assets_src)
        target = dest_root / rel
        if target.exists():
            result.skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        result.copied += 1

    log_msg("INFO", f"Assets deployed: {result.copied} copied, {result.skipped} kept")
    return result
