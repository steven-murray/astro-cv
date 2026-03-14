"""Education section datatype."""

from pathlib import Path
from typing import Self

import attrs
import tomllib
import tomli_w


@attrs.define(frozen=True)
class Supervisor:
    """Supervisor details."""

    name: str
    url: str = ""


@attrs.define(frozen=True)
class Degree:
    """Degree details."""

    level: str
    title: str
    years: str
    subject: str = ""
    subject_url: str = ""
    thesis_title: str = ""
    thesis_topic: str = ""
    supervisors: list[Supervisor] = attrs.field(factory=list)
    area_of_study: str = ""
    graduation: str = ""
    courses: list[str] = attrs.field(factory=list)
    subjects: list[str] = attrs.field(factory=list)


@attrs.define(frozen=True)
class Institution:
    """Institution details."""

    name: str
    url: str
    city: str
    state: str
    country: str = ""
    degrees: list[Degree] = attrs.field(factory=list)


@attrs.define(frozen=True)
class Education:
    """Education section data and settings."""

    institutions: list[Institution]

    # Settings from TOML
    keep_undergrad: bool = True
    keep_secondary: bool = False
    keep_undergrad_courses: bool = False

    @classmethod
    def read_toml(cls, path: Path | str) -> Self:
        """Read education data from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})
        institutions = []
        for inst in data.get("institutions", []):
            degrees = []
            for deg in inst.get("degrees", []):
                supervisors = [Supervisor(**s) for s in deg.get("supervisors", [])]
                degrees.append(
                    Degree(
                        level=deg.get("level", ""),
                        title=deg.get("title", ""),
                        years=deg.get("years", ""),
                        subject=deg.get("subject", ""),
                        subject_url=deg.get("subject_url", ""),
                        thesis_title=deg.get("thesis_title", ""),
                        thesis_topic=deg.get("thesis_topic", ""),
                        supervisors=supervisors,
                        area_of_study=deg.get("area_of_study", ""),
                        graduation=deg.get("graduation", ""),
                        courses=deg.get("courses", []),
                        subjects=deg.get("subjects", []),
                    )
                )

            institutions.append(
                Institution(
                    name=inst.get("name", ""),
                    url=inst.get("url", ""),
                    city=inst.get("city", ""),
                    state=inst.get("state", ""),
                    country=inst.get("country", ""),
                    degrees=degrees,
                )
            )

        return cls(
            institutions=institutions,
            keep_undergrad=settings.get("keep_undergrad", True),
            keep_secondary=settings.get("keep_secondary", False),
            keep_undergrad_courses=settings.get("keep_undergrad_courses", False),
        )

    def write_toml(self, path: Path | str) -> None:
        """Write education data to TOML file."""
        path = Path(path)

        data = {
            "settings": {
                "keep_undergrad": self.keep_undergrad,
                "keep_secondary": self.keep_secondary,
                "keep_undergrad_courses": self.keep_undergrad_courses,
            },
            "institutions": [
                {
                    "name": inst.name,
                    "url": inst.url,
                    "city": inst.city,
                    "state": inst.state,
                    "country": inst.country,
                    "degrees": [
                        {
                            "level": deg.level,
                            "title": deg.title,
                            "years": deg.years,
                            "subject": deg.subject,
                            "subject_url": deg.subject_url,
                            "thesis_title": deg.thesis_title,
                            "thesis_topic": deg.thesis_topic,
                            "supervisors": [
                                {"name": s.name, "url": s.url} for s in deg.supervisors
                            ],
                            "area_of_study": deg.area_of_study,
                            "graduation": deg.graduation,
                            "courses": deg.courses,
                            "subjects": deg.subjects,
                        }
                        for deg in inst.degrees
                    ],
                }
                for inst in self.institutions
            ],
        }

        with path.open("wb") as f:
            tomli_w.dump(data, f)
