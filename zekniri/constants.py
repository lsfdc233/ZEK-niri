"""Global constants, paths, and the ANSI palette.

Identity lives here and only here. To rename the tool, change PROJECT_NAME and
CLI_CMD, then rename the package directory and adjust install.sh's
``engine_is_complete`` / launcher string. Nothing else hardcodes the name.
"""

import os
from pathlib import Path

# --- Project identity ---
PROJECT_NAME = "ZEKniri"
# Command installed as ~/.local/bin/<CLI_CMD>; what the user types.
CLI_CMD = "ZEK-niri"
# Python package directory; used for ``python3 -m <PACKAGE_NAME>`` re-exec.
PACKAGE_NAME = "zekniri"

# --- Directory conventions ---
CONFIG_DIR_NAME = "configs"
ASSETS_DIR_NAME = "assets"

# --- Repository / network ---
REPO_URL = os.environ.get("ZEKNIRI_REPO", "https://github.com/sky1234762/ZEK-niri.git")

# Base system packages no app manifest declares. Empty by default: a generic
# installer assumes nothing about the host.
CORE_DEPS: list[str] = []

# Snapshots kept before the oldest is pruned.
MAX_SNAPSHOTS = 30

# Flag carried across an update re-exec so the deploy runs on the freshly
# pulled engine code instead of modules already loaded in the old process.
PENDING_UPGRADE_ENV = "ZEKNIRI_PENDING_UPGRADE"
PENDING_UPGRADE_MENU_ENV = "ZEKNIRI_PENDING_UPGRADE_MENU"


class Colors:
    """ANSI palette. TUI output stays inside this scale."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    DARK_GRAY = "\033[90m"

    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_PURPLE = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"

    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"
    CLEAR_SCREEN = "\033[H\033[J"
    CLEAR_LINE = "\033[2K\r"


def nyx_home_name() -> str:
    """Name of the tool's own data directory under ~/.config."""
    return PROJECT_NAME


def default_repo_dir() -> Path:
    return Path.home() / ".cache" / PROJECT_NAME
