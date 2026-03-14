"""Academic Experience section datatype."""

import tomllib
from pathlib import Path
import attrs
from typing import Literal, Self
from abc import ABC


@attrs.define(kw_only=True)
class AcademicExperienceEntry(ABC):
    """Generic academic experience entry (grants, committees, etc.)."""

    start_year: int
    start_month: int | None = None
    start_day: int | None = None

    end_year: int | None = None
    end_month: int | None = None
    end_day: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create from dictionary, handling optional fields."""

        # Deal with dates consistently.
        if "year" in data:
            data["start_year"] = data.pop("year")
        if "startdate" in data:
            start_date = data.pop("startdate")
            parts = start_date.split("/")
            data["start_year"] = int(parts[-1])
            if len(parts) > 1:
                data["start_month"] = int(parts[-2])
            if len(parts) > 2:
                data["start_day"] = int(parts[-3])
        if "enddate" in data:
            end_date = data.pop("enddate")
            if end_date:
                parts = end_date.split("/")
                data["end_year"] = int(parts[-1])
                if len(parts) > 1:
                    data["end_month"] = int(parts[-2])
                if len(parts) > 2:
                    data["end_day"] = int(parts[-3])
        if "date" in data:
            date = data.pop("date")
            parts = date.split("/")
            data["start_year"] = int(parts[-1])
            if len(parts) > 1:
                data["start_month"] = int(parts[-2])
            if len(parts) > 2:
                data["start_day"] = int(parts[-3])

        return cls(**data)


@attrs.define(kw_only=True)
class GrantEntry(AcademicExperienceEntry):
    """Grant entry with specific fields."""

    grant: str
    title: str
    authors: str
    amount: str
    role: Literal["PI", "Co-PI", "Collaborator"]


@attrs.define(kw_only=True)
class CollaborationEntry(AcademicExperienceEntry):
    """Collaboration entry with specific fields."""

    group: str
    principal_investigator: str


@attrs.define(kw_only=True)
class CommitteeEntry(AcademicExperienceEntry):
    """Committee entry with specific fields."""

    committee: str
    role: str


@attrs.define(kw_only=True)
class RefereeEntry(AcademicExperienceEntry):
    """Referee entry with specific fields."""

    journal: str


@attrs.define(kw_only=True)
class LecturingEntry(AcademicExperienceEntry):
    """Lecturing entry with specific fields."""

    course_code: str
    institution: str
    course_name: str


@attrs.define(kw_only=True)
class SupervisionEntry(AcademicExperienceEntry):
    student_name: str
    #    project_title: str
    institution: str
    level: Literal["Undergraduate", "Masters", "Honours", "PhD"]
    co_supervised: bool


@attrs.define(kw_only=True)
class TeachingEntry(AcademicExperienceEntry):
    course_name: str
    duration: str
    level: str
    institution: str
    role: str


@attrs.define(kw_only=True)
class OutreachEntry(AcademicExperienceEntry):
    activity: str
    nature_of_activity: Literal[
        "Public Talk", "Media Appearance", "School Visit", "Education/Training"
    ]
    location: str
    country: str
    url: str | None = None
    other_url: str | None = None


@attrs.define(kw_only=True)
class IndustryEntry(AcademicExperienceEntry):
    project: str
    company: str
    description: str


@attrs.define(kw_only=True)
class ProfessionalTrainingEntry(AcademicExperienceEntry):
    name: str
    place: str


@attrs.define(kw_only=True)
class PersonalTrainingEntry(AcademicExperienceEntry):
    name: str


@attrs.define(kw_only=True)
class AcademicExperience:
    """Academic experience data with multiple categories."""

    grants: list[GrantEntry] = attrs.Factory(list)
    collaborations: list[CollaborationEntry] = attrs.Factory(list)
    committees: list[CommitteeEntry] = attrs.Factory(list)
    referees: list[RefereeEntry] = attrs.Factory(list)
    lecturing: list[LecturingEntry] = attrs.Factory(list)
    supervision: list[SupervisionEntry] = attrs.Factory(list)
    teaching: list[TeachingEntry] = attrs.Factory(list)
    outreach: list[OutreachEntry] = attrs.Factory(list)
    industry: list[IndustryEntry] = attrs.Factory(list)
    prof_training: list[ProfessionalTrainingEntry] = attrs.Factory(list)
    personal_training: list[PersonalTrainingEntry] = attrs.Factory(list)

    # Settings for which categories to omit
    omit_grants: bool = False
    omit_collaborations: bool = False
    omit_committees: bool = False
    omit_referees: bool = False
    omit_lecturing: bool = False
    omit_supervision: bool = False
    omit_teaching: bool = False
    omit_outreach: bool = False
    omit_prof_training: bool = False
    omit_personal_training: bool = False
    omit_industry: bool = False

    @classmethod
    def read_toml(cls, path: Path | str) -> "AcademicExperience":
        """Read academic experience settings from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(**settings)
