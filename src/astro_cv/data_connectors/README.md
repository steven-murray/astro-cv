# Integrations

This package provides connectors to external data sources for CV generation.

## Architecture

The integrations package follows a **decoupled architecture**:

- **Data Classes**: Live in their respective section packages (e.g., `astro_cv.sections.awards_and_scholarships.AwardsAndScholarships`)
- **Connectors**: Fetch data from sources and populate the dataclasses (e.g., `GSheetsDataConnector`)
- **Flexibility**: Different connectors can exist (Google Sheets, JSON, API, etc.) all returning the same dataclass instances

This allows:
- Sections to own their data structures
- Multiple data sources to feed the same section
- Easy addition of new connectors without changing section code

## Google Sheets Integration (`gsheet.py`)

The `GSheetsDataConnector` class handles authentication with Google Sheets and provides methods to retrieve normalized data for different CV sections.

### Authentication

The connector uses service account authentication:

```python
from astro_cv.integrations import GSheetsDataConnector

# Authenticate and connect
connector = GSheetsDataConnector(
    sheet_name="Activity Tracker",
)

# By default, credentials are loaded from
# ~/.config/astro-cv/authorization_key.json (Linux)
# via appdirs.

# Retrieve data
awards = connector.get_awards_and_scholarships(min_year=2007, min_rating=2)

# Optional: override the auth key path explicitly
custom = GSheetsDataConnector(auth_file="/path/to/authorization_key.json")
```

### Available Methods

#### `get_awards_and_scholarships(min_year: int, min_rating: int) -> AwardsAndScholarships`

Retrieves awards and scholarships from the "Awards" worksheet and returns an `astro_cv.sections.awards_and_scholarships.AwardsAndScholarships` instance.

```python
from astro_cv.integrations import GSheetsDataConnector
from astro_cv.sections.awards_and_scholarships import create_awards_and_scholarships

connector = GSheetsDataConnector()
awards = connector.get_awards_and_scholarships(min_year=2007, min_rating=2)
filtered = awards.filtered_awards()  # Apply filters
latex_content = create_awards_and_scholarships(awards)
```

#### `get_technical_skills() -> TechnicalSkill`

Retrieves technical skills from the "Technical" worksheet (first row) and returns a `astro_cv.sections.technical_skills.TechnicalSkill` instance.

```python
from astro_cv.integrations import GSheetsDataConnector
from astro_cv.sections.technical_skills import create_technical_skills

connector = GSheetsDataConnector()
skills = connector.get_technical_skills()
latex_content = create_technical_skills(skills)
```

#### `get_presentations(write_posters: bool, write_local_talks: bool) -> Presentation`

Retrieves presentations from "Conferences", "Seminars", and optionally "Other Presentations" worksheets and returns an `astro_cv.sections.presentations.Presentation` instance organized by type.

```python
from astro_cv.integrations import GSheetsDataConnector
from astro_cv.sections.presentations import create_presentations

connector = GSheetsDataConnector()
presentations = connector.get_presentations(write_posters=False, write_local_talks=False)
latex_content = create_presentations(presentations)
```

#### `get_academic_experience(...) -> AcademicExperience`

Retrieves academic experience from multiple worksheets with optional filtering and returns an `astro_cv.sections.academic_experience.AcademicExperience` instance.

```python
from astro_cv.integrations import GSheetsDataConnector
from astro_cv.sections.academic_experience import create_academic_experience

connector = GSheetsDataConnector()
experience = connector.get_academic_experience(
    omit_grants=False,
    omit_collaborations=False,
    # ... other options
)
latex_content = create_academic_experience(experience)
```

#### `get_press_releases() -> PressReleases`

Retrieves press releases from the "Press Releases" worksheet and returns an `astro_cv.sections.press_releases.PressReleases` instance organized by type (Article/Event).

```python
from astro_cv.integrations import GSheetsDataConnector
from astro_cv.sections.press_releases import create_press_releases

connector = GSheetsDataConnector()
press_releases = connector.get_press_releases()
latex_content = create_press_releases(press_releases)
```

**Worksheet fields:**
- Date (e.g., "15/01/2025")
- Type ("Article" or "Event")
- Location
- Title of Press Release
- Names of Authors (semicolon-separated)
- Media Office
- Link (URL)

## Data Classes

All dataclasses belong to their respective sections and are imported from there:

- `astro_cv.sections.awards_and_scholarships.AwardsAndScholarships` + `AwardsEntry`
- `astro_cv.sections.technical_skills.TechnicalSkill`
- `astro_cv.sections.presentations.Presentation` + `PresentationEntry`
- `astro_cv.sections.academic_experience.AcademicExperience` + `AcademicExperienceEntry`
- `astro_cv.sections.press_releases.PressReleases` + `PressReleaseEntry`

## Helper Functions

### `lol_to_lod(lol: list[list]) -> list[dict]`

Converts a list-of-lists (from gspread) to a list-of-dicts using the first row as headers. Available from integrations:

```python
from astro_cv.integrations import lol_to_lod

raw_data = [
    ["Name", "Age"],
    ["Alice", 30],
    ["Bob", 25],
]
normalized = lol_to_lod(raw_data)
# [{"Name": "Alice", "Age": 30}, {"Name": "Bob", "Age": 25}]
```

## Future Connectors

To add a new connector (e.g., JSON files, SQL, etc.):

1. Create a new file in `integrations/` (e.g., `json_connector.py`)
2. Implement retrieval methods that return the same dataclass instances
3. Export from `integrations/__init__.py`
4. No changes needed to section code - it always accepts the same dataclass types
