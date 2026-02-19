"""Press Releases section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class PressReleaseEntry:
    """Single press release entry."""

    Date: str
    Type: str  # "Article" or "Event"
    Location: str
    Title: str = ""
    Authors: str = ""  # Semicolon-separated list
    MediaOffice: str = ""
    Link: str = ""

    def get_authors_list(self) -> list[str]:
        """Parse semicolon-separated authors into list."""
        if not self.Authors:
            return []
        return [author.strip() for author in self.Authors.split(";")]


@attrs.define
class PressReleases:
    """Press releases data."""

    articles: list[PressReleaseEntry] = attrs.Factory(list)
    events: list[PressReleaseEntry] = attrs.Factory(list)

    @classmethod
    def read_toml(cls, path: Path | str) -> "PressReleases":
        """Read press releases settings from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            tomllib.load(f)  # Load but don't need settings yet

        return cls()

    def all_releases(self) -> list[PressReleaseEntry]:
        """Get all press releases sorted by date (most recent first)."""
        return sorted(self.articles + self.events, key=lambda x: x.Date, reverse=True)
