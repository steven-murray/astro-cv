"""Google Sheets data connector for CV sections."""

import tomllib
from pathlib import Path
from typing import Any
import gspread
import logging

# Import dataclasses from their respective sections
from astro_cv.sections.awards_and_scholarships import AwardsAndScholarships, AwardsEntry
from astro_cv.sections.technical_skills import TechnicalSkill
from astro_cv.sections.presentations import Presentation, PresentationEntry
from astro_cv.sections.academic_experience import (
    AcademicExperience,
    CollaborationEntry,
    SupervisionEntry,
)
from astro_cv.sections.press_releases import PressReleases, PressReleaseEntry

logger = logging.getLogger(__name__)


def lol_to_lod(lol: list[list]) -> list[dict]:
    """Convert list-of-lists from gspread to list-of-dicts.

    Assumes first row is a header.
    """
    if len(lol) < 2:
        return []
    return [{lol[0][i]: val for i, val in enumerate(lst)} for lst in lol[1:]]


class DataConnector:
    """Connect to Google Sheets and retrieve normalized data for CV sections."""

    def __init__(
        self,
        auth_file: Path | str = "authorization_key.json",
        sheet_name: str = "Activity Tracker",
    ):
        """Initialize Google Sheets connector and authenticate.

        Parameters
        ----------
        auth_file : Path or str
            Path to the service account JSON file for authentication.
        sheet_name : str
            Name of the Google Sheet to open.
        verbose : bool
            Print authentication status messages.
        """
        self.auth_file = Path(auth_file)
        self.sheet_name = sheet_name
        self.data = None

        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API."""
        try:
            logger.info(f"Authenticating with Google Sheets using {self.auth_file}...")

            self.gc = gspread.service_account(filename=str(self.auth_file))

            logger.info(f"Opening '{self.sheet_name}' from Google Sheets...")

            self.data = self.gc.open(self.sheet_name)

            logger.info("Successfully authenticated with Google Sheets")

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Error: Authentication file not found at {self.auth_file}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error authenticating with Google Sheets: {e}") from e

    def _get_worksheet_data(self, worksheet_name: str) -> list[dict]:
        """Get data from a worksheet as list of dicts.

        Parameters
        ----------
        worksheet_name : str
            Name of the worksheet to retrieve.

        Returns
        -------
        list[dict]
            List of dictionaries, one per row.
        """
        try:
            worksheet = self.data.worksheet(worksheet_name)
            rows = worksheet.get_all_values()
            return lol_to_lod(rows)
        except Exception as e:
            logger.error(f"Error reading worksheet '{worksheet_name}': {e}")
            return []

    def get_awards_and_scholarships(
        self,
        min_year: int = 0,
        min_rating: int = 0,
    ) -> AwardsAndScholarships:
        """Get awards and scholarships data.

        Parameters
        ----------
        min_year : int
            Minimum year to include awards.
        min_rating : int
            Minimum rating to include awards.

        Returns
        -------
        AwardsAndScholarships
            Normalized awards data.
        """
        data = self._get_worksheet_data("Awards")
        awards = [
            AwardsEntry(
                Name=row.get("Name", ""),
                DateReceived=row.get("DateReceived", ""),
                Duration=row.get("Duration", ""),
                Institution=row.get("Institution", ""),
                Rating=row.get("Rating", "0"),
            )
            for row in data
        ]

        return AwardsAndScholarships(
            awards=awards,
            min_year=min_year,
            min_rating=min_rating,
        )

    def get_technical_skills(self) -> TechnicalSkill:
        """Get technical skills data.

        Returns
        -------
        TechnicalSkill
            Technical skills data (first entry from worksheet).
        """
        data = self._get_worksheet_data("Technical")

        if not data:
            return TechnicalSkill()

        first_row = data[0]
        return TechnicalSkill(
            OSProficient=first_row.get("OSProficient", ""),
            OSUsed=first_row.get("OSUsed", ""),
            LanguageProficient=first_row.get("LanguageProficient", ""),
            LanguageUsed=first_row.get("LanguageUsed", ""),
            SoftwareProficient=first_row.get("SoftwareProficient", ""),
            SoftwareUsed=first_row.get("SoftwareUsed", ""),
        )

    def get_presentations(
        self,
        write_posters: bool = False,
        write_local_talks: bool = False,
    ) -> Presentation:
        """Get presentations data from multiple worksheets.

        Parameters
        ----------
        write_posters : bool
            Include posters in output.
        write_local_talks : bool
            Include local talks in output.

        Returns
        -------
        Presentation
            Normalized presentations data.
        """
        # Get conference presentations
        conference_data = self._get_worksheet_data("Conferences")
        invited_talks = []
        contributed_talks = []
        posters = []

        for row in conference_data:
            if "Name" not in row:
                # Skip rows without a Name (could be empty rows or malformed data)
                continue
            entry = PresentationEntry(
                Title=row["Title"],
                Name=row["Name"],
                City=row["City"],
                Country=row["Country"],
                StartDate=row["StartDate"],
                URL=row["URL"],
                Awards=row["Awards"],
                Type=row["Type of contribution"],
                InvitedSpeaker=row.get("Invited Speaker?", "No"),
            )
            if row.get("Invited Speaker?") == "Yes":
                invited_talks.append(entry)
            elif row.get("Type of contribution") == "Talk":
                contributed_talks.append(entry)
            elif row.get("Type of contribution") == "Poster":
                posters.append(entry)

        # Get seminars
        seminars_data = self._get_worksheet_data("Seminars")
        seminars = [
            PresentationEntry(
                Title=row["TalkTitle"],
                Name=row["Name"],
                City=row["Location"],
                Country="",
                StartDate=row["Date"],
                URL=row["TalkURL"],
            )
            for row in seminars_data
            if "Name" in row
        ]

        # Get local talks if requested
        local_talks = []
        if write_local_talks:
            local_data = self._get_worksheet_data("Other Presentations")
            local_talks = [
                PresentationEntry(
                    Title=row["Title"],
                    Name=row["Name"],
                    City=row["Location"],
                    Country="",
                    StartDate=row["Date"],
                    URL=row["TalkURL"],
                )
                for row in local_data
            ]

        return Presentation(
            invited_talks=invited_talks,
            contributed_talks=contributed_talks,
            seminars=seminars,
            posters=posters,
            local_talks=local_talks,
            write_posters=write_posters,
            write_local_talks=write_local_talks,
        )

    def get_academic_experience(
        self,
        omit_grants: bool = False,
        omit_collaborations: bool = False,
        omit_committees: bool = False,
        omit_referees: bool = False,
        omit_lecturing: bool = False,
        omit_supervision: bool = False,
        omit_teaching: bool = False,
        omit_outreach: bool = False,
        omit_prof_training: bool = False,
        omit_personal_training: bool = False,
        omit_industry: bool = False,
    ) -> AcademicExperience:
        """Get academic experience data from multiple worksheets.

        Parameters
        ----------
        omit_* : bool
            Whether to omit each category from the results.

        Returns
        -------
        AcademicExperience
            Normalized academic experience data.
        """
        # Map omit flags to worksheet names and result attributes
        worksheets = {
            "Grants": ("grants", "GrantEntry", omit_grants),
            "Collaborations": (
                "collaborations",
                "CollaborationEntry",
                omit_collaborations,
            ),
            "Memberships and Committees": (
                "committees",
                "CommitteeEntry",
                omit_committees,
            ),
            "Journal Referee": ("referees", "RefereeEntry", omit_referees),
            "Lecturing": ("lecturing", "LecturingEntry", omit_lecturing),
            "Supervision": ("supervision", "SupervisionEntry", omit_supervision),
            "Teaching": ("teaching", "TeachingEntry", omit_teaching),
            "Outreach": ("outreach", "OutreachEntry", omit_outreach),
            "IndustryEngagement": ("industry", "IndustryEntry", omit_industry),
            "Professional Training": (
                "prof_training",
                "ProfessionalTrainingEntry",
                omit_prof_training,
            ),
            "Personal Training": (
                "personal_training",
                "PersonalTrainingEntry",
                omit_personal_training,
            ),
        }

        all_entries = {}
        for worksheet_name, (attr_name, entry_type, omit) in worksheets.items():
            if not omit:
                data = self._get_worksheet_data(worksheet_name)
                entries = []
                for row in data:
                    row = {
                        k.lower().replace(" ", "_").replace("-", "_"): v
                        for k, v in row.items()
                    }  # Normalize keys

                    if hasattr(self, f"get_{attr_name}"):
                        # If there's a specific method for this category, use it
                        method = getattr(self, f"get_{attr_name}")
                        entries.append(method(row))
                    else:
                        entries.append(globals()[entry_type].from_dict(row))

                all_entries[attr_name] = entries

        return AcademicExperience(**all_entries)

    def get_collaborations(self, row: dict) -> CollaborationEntry:
        """Get collaborations data from the 'Collaborations' worksheet."""
        if "ci" in row:
            row["principal_investigator"] = row.pop("ci")
        return CollaborationEntry.from_dict(row)

    def get_supervision(self, row: dict) -> SupervisionEntry:
        """Get supervision data from the 'Supervision' worksheet."""
        row["co_supervised"] = (
            True if row.get("co_supervised", "No").lower() == "yes" else False
        )
        return SupervisionEntry.from_dict(row)

    def get_press_releases(self) -> PressReleases:
        """Get press releases data from Google Sheets.

        Returns
        -------
        PressReleases
            Normalized press releases data organized by type.
        """
        data = self._get_worksheet_data("Press Releases")

        articles = []
        events = []

        for row in data:
            entry = PressReleaseEntry(
                Date=row["Date"],
                Type=row["Type"],
                Location=row["Location"],
                Title=row["Title of Press Release"],
                Authors=row["Names of Authors"],
                MediaOffice=row["Media Office"],
                Link=row["Link"],
            )

            if entry.Type.lower() == "article":
                articles.append(entry)
            elif entry.Type.lower() == "event":
                events.append(entry)
            else:
                # Default to article if type is unclear
                articles.append(entry)

        return PressReleases(
            articles=articles,
            events=events,
        )

    def get(self, section_name: str, config_path: Path | str) -> Any:
        """Generic method to get section data from Google Sheets.

        Delegates to the appropriate section-specific method based on section_name.
        Loads settings from the TOML config file.

        Parameters
        ----------
        section_name : str
            Name of the section (e.g., 'academic_experience', 'awards_and_scholarships').
        config_path : Path or str
            Path to the section's TOML configuration file.

        Returns
        -------
        Any
            The data object for the section.

        Raises
        ------
        ValueError
            If the section_name is not supported by this connector.
        """
        config_path = Path(config_path)
        section_key = section_name.replace("-", "_")

        # Load settings from TOML file
        with open(config_path, "rb") as f:
            settings = tomllib.load(f)

        kwargs = settings.get("settings", {})

        try:
            return getattr(self, f"get_{section_key}")(**kwargs)
        except AttributeError:
            raise ValueError(
                f"DataConnector (gsheet) does not support '{section_name}'. "
                f"Supported sections: awards_and_scholarships, technical_skills, "
                f"presentations, academic_experience, press_releases"
            )
