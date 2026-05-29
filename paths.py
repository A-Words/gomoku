"""Runtime path helpers for development and PyInstaller builds."""

from pathlib import Path
import sys


def project_root() -> Path:
    """Return the source directory during development."""
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    """Return a read-only bundled resource path."""
    base = Path(getattr(sys, "_MEIPASS", project_root()))
    return base.joinpath(*parts)


def user_data_path(*parts: str) -> Path:
    """Return a writable app-adjacent data path."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = project_root()
    return base.joinpath(*parts)
