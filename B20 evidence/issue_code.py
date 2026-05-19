# the following code is original from https://github.com/HKUDS/OpenHarness/blob/main/ohmo/workspace.py

import os
from pathlib import Path

WORKSPACE_DIRNAME = ".ohmo"


def get_workspace_root(workspace: str | Path | None = None) -> Path:
    """Return the ohmo workspace root.

    Resolution order:
    1. Explicit ``workspace`` argument
    2. ``OHMO_WORKSPACE`` environment variable
    3. ``~/.ohmo``
    """
    explicit = workspace or os.environ.get("OHMO_WORKSPACE")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        
        # this is the issue line, it return the same path no matter the path name is .ohm or not
        return path if path.name == WORKSPACE_DIRNAME else path 
    return (Path.home() / WORKSPACE_DIRNAME).resolve()
