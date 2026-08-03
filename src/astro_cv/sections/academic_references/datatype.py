"""Data types for academic references section."""

import tomllib
from pathlib import Path

import attrs


@attrs.define
class Reference:
    """A single academic reference."""

    name: str
    email: str
    address: str
    phone: str = ""


@attrs.define
class AcademicReferences:
    """Configuration for academic references section."""

    references: list[Reference]
    maxref: int | None = None

    @classmethod
    def read_toml(cls, path: Path) -> "AcademicReferences":
        """Read academic references from TOML file.

        Args:
            path: Path to the TOML configuration file

        Returns:
            AcademicReferences instance
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(
            references=[Reference(**ref) for ref in data.get("references", [])],
            maxref=settings.get("maxref"),
        )
