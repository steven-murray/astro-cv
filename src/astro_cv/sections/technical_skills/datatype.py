"""Technical Skills section datatype."""

import tomllib
from pathlib import Path
import attrs


@attrs.define
class TechnicalSkill:
    """Technical skills entry."""

    OSProficient: str = ""
    OSUsed: str = ""
    LanguageProficient: str = ""
    LanguageUsed: str = ""
    SoftwareProficient: str = ""
    SoftwareUsed: str = ""

    @classmethod
    def read_toml(cls, path: Path | str) -> "TechnicalSkill":
        """Read technical skills settings from TOML file."""
        path = Path(path)
        with open(path, "rb") as f:
            tomllib.load(f)  # Load but don't need settings yet

        return cls()
