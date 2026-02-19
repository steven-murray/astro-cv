"""Data types for contact information section."""

from pathlib import Path
from typing import Optional

import attrs
import tomllib


@attrs.define
class Website:
    """A website/online profile."""

    url: str
    kind: str
    id: str
    icon: Optional[str] = None


@attrs.define
class Institution:
    """Institution information."""

    url: str
    department_name: str
    name: str
    street: str
    location: str
    country: str


@attrs.define
class Personal:
    """Personal information."""

    firstname: str
    surname: str
    phone_number: str
    email: str
    citizenship: list[str]


@attrs.define
class Online:
    """Online identifiers."""

    orcid: str


@attrs.define
class ContactInformation:
    """Configuration for contact information section."""

    institution: Institution
    personal: Personal
    online: Online
    websites: list[Website]

    @classmethod
    def read_toml(cls, path: Path) -> "ContactInformation":
        """Read contact information from TOML file.

        Args:
            path: Path to the TOML configuration file

        Returns:
            ContactInformation instance
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            institution=Institution(**data["institution"]),
            personal=Personal(**data["personal"]),
            online=Online(**data["online"]),
            websites=[Website(**w) for w in data["websites"]],
        )
