"""ZEKniri title art.

The canonical source is ``logo/title`` at the repository root. The TUI reads it
at runtime, so editing that file changes the title without touching code. The
copy below is only a fallback for a tree where the file is missing.
"""

from pathlib import Path

from zekniri.core import get_env

TITLE_REL = "logo/title"

FALLBACK_ART = r'''███████╗███████╗██╗  ██╗    ███╗   ██╗██╗██████╗ ██╗
╚══███╔╝██╔════╝██║ ██╔╝    ████╗  ██║██║██╔══██╗██║
  ███╔╝ █████╗  █████╔╝     ██╔██╗ ██║██║██████╔╝██║
 ███╔╝  ██╔══╝  ██╔═██╗     ██║╚██╗██║██║██╔══██╗██║
███████╗███████╗██║  ██╗    ██║ ╚████║██║██║  ██║██║
╚══════╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝'''

FALLBACK_WIDTH = 52


def load_title():
    """Return ``(art, width)``: prefer ``<repo>/logo/title``, else the fallback."""
    try:
        path = Path(get_env().repo_dir) / TITLE_REL
        if path.is_file():
            text = path.read_text(encoding="utf-8").rstrip("\n")
            lines = text.splitlines()
            if lines:
                return text, max(len(line) for line in lines)
    except OSError:
        pass
    return FALLBACK_ART, FALLBACK_WIDTH
