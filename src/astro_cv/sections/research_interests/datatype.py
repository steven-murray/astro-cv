"""Research Interests section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class ResearchInterests:
    """Research interests with categories and sub-topics."""

    interests: dict[str, list[str]]

    @classmethod
    def read_toml(cls, path: Path | str) -> "ResearchInterests":
        """Read research interests from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            interests=data["interests"],
        )
