"""Software section datatype."""

import tomllib
from pathlib import Path
from typing import Self

import attrs
import tomli_w


@attrs.define(frozen=True)
class Organization:
    """Organization with contribution information."""

    login: str
    description: str = ""
    total_commits: int = 0
    total_issues: int = 0
    total_prs: int = 0
    total_reviews: int = 0

    @property
    def total_contributions(self) -> int:
        """Total contributions to organization."""
        return (
            self.total_commits + self.total_issues + self.total_prs + self.total_reviews
        )


@attrs.define(frozen=True)
class Repository:
    """Repository with contributor information."""

    name: str
    url: str
    description: str = ""
    stargazers: int = 0
    forks: int = 0
    user_contributions: int = 0
    user_rank: int = 0  # Rank among all contributors (1 = top)
    total_contributors: int = 0

    @property
    def contribution_percent(self) -> float:
        """Percentage of total contributions by user."""
        if self.total_contributors == 0:
            return 0.0
        # Rough estimate: user_contributions / (avg contribs per person)
        return 100 * (self.user_contributions / max(1, self.total_contributors * 5))


@attrs.define(frozen=True)
class SoftwareList:
    """Software section data."""

    organizations: list[Organization] = attrs.field(factory=list)
    original_repos: list[Repository] = attrs.field(factory=list)
    collaborative_repos: list[Repository] = attrs.field(factory=list)

    # Settings from TOML
    github_user: str = ""
    max_repos: int = 10
    max_repos_collab: int = 10
    blacklist_orgs: list[str] = attrs.field(factory=list)
    blacklist_repos: list[str] = attrs.field(factory=list)
    original_codes: list[str] = attrs.field(factory=list)
    min_contributions: int = 1

    @classmethod
    def read_toml(cls, path: Path | str) -> Self:
        """Read SoftwareList settings from TOML file.

        Note: This reads settings only. Repositories are populated via connector.
        """
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(
            github_user=settings.get("github_user", ""),
            max_repos=settings.get("max_repos", 10),
            max_repos_collab=settings.get("max_repos_collab", 10),
            blacklist_orgs=settings.get("blacklist_orgs", []),
            blacklist_repos=settings.get("blacklist_repos", []),
            original_codes=settings.get("original_codes", []),
            min_contributions=settings.get("min_contributions", 1),
        )

    def write_toml(self, path: Path | str) -> None:
        """Write the SoftwareList to a TOML file."""
        path = Path(path)
        data = {
            "settings": {
                "github_user": self.github_user,
                "max_repos": self.max_repos,
                "max_repos_collab": self.max_repos_collab,
                "blacklist_orgs": self.blacklist_orgs,
                "blacklist_repos": self.blacklist_repos,
                "original_codes": self.original_codes,
                "min_contributions": self.min_contributions,
            }
        }
        with path.open("wb") as f:
            tomli_w.dump(data, f)
