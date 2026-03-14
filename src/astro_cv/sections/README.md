# Sections Package

This package contains modular CV sections with TOML-based configuration.

## Structure

Each section is a subpackage with the following structure:

```
sections/
├── section_name/
│   ├── __init__.py          # Exports main classes and functions
│   ├── datatype.py          # attrs-based configuration dataclass with .read_toml()
│   └── latex.py             # LaTeX generation logic
```

## Adding a New Section

To add a new section:

1. **Create TOML configuration** in the config repo (e.g., `my-cv-info/section-name.toml`)

2. **Create section subpackage**: `sections/section_name/`

3. **Define data types** in `datatype.py`:
   ```python
   import attrs
   import tomllib
   from pathlib import Path

   @attrs.define
   class SectionName:
       """Configuration for section."""

       field1: str
       field2: list[str]

       @classmethod
       def read_toml(cls, path: Path) -> "SectionName":
           """Read configuration from TOML file."""
           with open(path, 'rb') as f:
               data = tomllib.load(f)
           return cls(**data)
   ```

4. **Implement LaTeX generation** in `latex.py`:
   ```python
   from astro_cv.formats.latex import myformat
   from .datatype import SectionName

   def create_section_name(config: SectionName) -> str:
       """Generate LaTeX for section."""
       # Your LaTeX generation logic here
       return latex_string
   ```

5. **Export in `__init__.py`**:
   ```python
   from .latexmport SectionName
   from .processing import create_section_name

   __all__ = ["SectionName", "create_section_name"]
   ```

6. **Update `sections/__init__.py`** to include the new section

## Example Sections

### Contact Information

**Config**: `my-cv-info/contact-information.toml`

```toml
[institution]
url = "https://example.edu"
name = "University Name"
# ...

[personal]
firstname = "John"
surname = "Doe"
email = "john@example.edu"

[[websites]]
url = "https://github.com/username"
kind = "github"
id = "username"
```

**Usage**:
```python
from astro_cv.sections.contact_information import ContactInformation, create_contact_information

config = ContactInformation.read_toml(Path("my-cv-info/contact-information.toml"))
latex = create_contact_information(config)
```

### Academic References

**Config**: `my-cv-info/academic-references.toml`

```toml
[[references]]
name = "Prof. Jane Smith"
email = "jane@example.edu"
address = "123 University Ave"
phone = "+1 234 567 8900"

[settings]
maxref = 4
```

**Usage**:
```python
from astro_cv.sections.academic_references import AcademicReferences, create_academic_references

config = AcademicReferences.read_toml(Path("my-cv-info/academic-references.toml"))
latex = create_academic_references(config)
```

## Testing

Run the example script to test the current sections:

```bash
uv run python example_sections.py
```
