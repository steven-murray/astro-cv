"""Data source integrations for CV generation."""

# Import DataConnector from each integration module
from . import ads, github, gsheet, toml

__all__ = [
    "ads",
    "github",
    "gsheet",
    "toml",
]

# Also provide backward compatibility imports (deprecated)
from .gsheet import lol_to_lod

__all__ += ["lol_to_lod"]
