"""Summary profile section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class SummaryProfile:
    """A short summary / profile statement to appear near the top of the CV."""

    text: str

    @classmethod
    def read_toml(cls, path: Path | str) -> "SummaryProfile":
        """Read summary profile from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(text=data["text"])
