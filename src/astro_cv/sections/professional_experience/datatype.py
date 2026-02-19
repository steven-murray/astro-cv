"""Professional Experience section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class Job:
    """A single job/position."""

    organisation: str
    city: str
    state: str
    title: str
    start_year: int
    end_year: int  # 0 means current
    rating: int


@attrs.define
class ProfessionalExperience:
    """Professional experience with job listings and filter settings."""

    jobs: list[Job]
    min_rating: int
    min_date: int

    @classmethod
    def read_toml(cls, path: Path | str) -> "ProfessionalExperience":
        """Read professional experience from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        jobs = [Job(**job_data) for job_data in data["jobs"]]
        settings = data.get("settings", {})

        return cls(
            jobs=jobs,
            min_rating=settings.get("min_rating", 0),
            min_date=settings.get("min_date", 0),
        )

    def filtered_jobs(self) -> list[Job]:
        """Get jobs filtered by rating and date."""
        return [
            job
            for job in self.jobs
            if job.rating >= self.min_rating and job.start_year >= self.min_date
        ]
