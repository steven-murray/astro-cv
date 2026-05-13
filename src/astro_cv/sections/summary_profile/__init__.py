"""Summary profile section."""

from .datatype import SummaryProfile
from .latex import create

# No margin heading for this section — the styled box is self-explanatory.
SECTION_TITLE = False

__all__ = ["SummaryProfile", "create"]
