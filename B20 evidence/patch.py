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
        # add a base directory to restrict and isolate directory
        base_dir = Path("/safe/base").resolve()
        path = Path(explicit).expanduser().resolve()

        if not path.is_relative_to(base_dir):
            raise ValueError("Invalid path") # reject not allowed directory
        return path
    
    return (Path.home() / WORKSPACE_DIRNAME).resolve()
