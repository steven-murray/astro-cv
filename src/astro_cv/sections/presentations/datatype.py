"""Presentations section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class PresentationEntry:
    """Presentation entry."""

    Title: str
    Name: str
    City: str
    Country: str
    StartDate: str
    URL: str = ""
    Awards: str = ""
    Type: str = "Talk"
    InvitedSpeaker: str = "No"


@attrs.define
class Presentation:
    """Presentations data."""

    invited_talks: list[PresentationEntry] = attrs.Factory(list)
    contributed_talks: list[PresentationEntry] = attrs.Factory(list)
    seminars: list[PresentationEntry] = attrs.Factory(list)
    posters: list[PresentationEntry] = attrs.Factory(list)
    local_talks: list[PresentationEntry] = attrs.Factory(list)
    write_posters: bool = False
    write_local_talks: bool = False

    @classmethod
    def read_toml(cls, path: Path | str) -> "Presentation":
        """Read presentations settings from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(
            write_posters=settings.get("write_posters", False),
            write_local_talks=settings.get("write_local_talks", False),
        )
