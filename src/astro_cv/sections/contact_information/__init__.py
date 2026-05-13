"""Contact information section."""

from .datatype import ContactInformation
from .latex import create

# Show the margin heading for contact information.
SECTION_TITLE = True

__all__ = ["ContactInformation", "create"]
