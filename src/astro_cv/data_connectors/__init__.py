"""Data source integrations for CV generation."""

# Import DataConnector from each integration module
from . import gsheet, ads, github, toml

__all__ = [
    "gsheet",
    "ads",
    "github",
    "toml",
]

# Also provide backward compatibility imports (deprecated)
from .gsheet import lol_to_lod

__all__ += ["lol_to_lod"]
