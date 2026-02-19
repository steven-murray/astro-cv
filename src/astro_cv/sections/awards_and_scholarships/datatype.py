"""Awards and Scholarships section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class AwardsEntry:
    """Single award entry."""

    Name: str
    DateReceived: str
    Duration: str = ""
    Institution: str = ""
    Rating: str = "0"


@attrs.define
class AwardsAndScholarships:
    """Awards and scholarships data."""

    awards: list[AwardsEntry]
    min_year: int = 0
    min_rating: int = 0

    def filtered_awards(self) -> list[AwardsEntry]:
        """Get awards filtered by year and rating."""
        return [
            award
            for award in self.awards
            if int(award.DateReceived) >= self.min_year
            and int(award.Rating) >= self.min_rating
        ]

    @classmethod
    def read_toml(cls, path: Path | str) -> "AwardsAndScholarships":
        """Read awards settings from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(
            awards=[],  # Will be populated by connector
            min_year=settings.get("min_year", 0),
            min_rating=settings.get("min_rating", 0),
        )
