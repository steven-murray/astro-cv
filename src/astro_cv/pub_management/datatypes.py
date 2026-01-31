"""Module for publication statistics calculations."""

from pathlib import Path
from functools import cached_property
import attrs
from typing import Generator, Self
import tomllib
import tomli_w


@attrs.define(frozen=True)
class Publication:
    """Class to hold a paper."""

    title: str
    authors: list[str]
    year: int
    bibcode: str
    refereed: bool
    citation_count: int = 0
    orcid_pub: bool = False
    aff: list[str] = attrs.field(factory=list)
    pub: str = ""

    @property
    def citations_per_year(self) -> float:
        """Citations per year."""
        from datetime import datetime

        current_year = datetime.now().year
        years_since_pub = max(1, current_year - self.year)
        return self.citation_count / years_since_pub


def _to_tuple_of_pubs(pubs: list[dict]) -> tuple[Publication, ...]:
    """Convert a list of publication dicts to a tuple of Publication objects."""
    return tuple(
        Publication(
            title=p.get("title", ""),
            authors=p.get("author", []),
            year=int(p.get("year", 0)),
            bibcode=p.get("bibcode", ""),
            citation_count=p.get("citation_count", 0),
            orcid_pub=p.get("orcid_pub", False),
            aff=p.get("aff", []),
            pub=p.get("pub", ""),
            refereed=p.get("refereed", False),
        )
        if isinstance(p, dict)
        else p
        for p in pubs
    )


@attrs.define(frozen=True)
class PubList:
    """Class to hold a list of publications."""

    publications: tuple[Publication, ...] = attrs.field(
        factory=tuple, converter=_to_tuple_of_pubs
    )

    def __len__(self) -> int:
        return len(self.publications)

    def __iter__(self) -> Generator[Publication, None, None]:
        return (p for p in self.publications)

    @cached_property
    def _dictform(self) -> dict[str, Publication]:
        return {p.bibcode: p for p in self.publications}

    def __getitem__(self, bibcode: str | int) -> Publication:
        if isinstance(bibcode, int):
            return self.publications[bibcode]
        else:
            return self._dictform[bibcode]

    def __contains__(self, bibcode: str) -> bool:
        return bibcode in self._dictform

    def keys(self) -> Generator:
        return self._dictform.keys()

    def values(self) -> Generator:
        return self._dictform.values()

    def items(self) -> Generator:
        return self._dictform.items()

    @classmethod
    def from_dict(cls, data: dict[str, dict]) -> Self:
        """Create a PubList from a dict of publication dicts."""
        pubs = tuple(data.values())
        return cls(publications=pubs)

    @classmethod
    def read_toml(cls, path: Path) -> Self:
        """Read a PubList from a TOML file."""

        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls.from_dict(data.get("publications", {}))

    def write_toml(self, path: Path) -> None:
        """Write the PubList to a TOML file."""
        data = {"publications": [attrs.asdict(p) for p in self.publications]}
        with path.open("wb") as f:
            tomli_w.dump(data, f)

    def select(
        self,
        year_min: int | None = None,
        year_max: int | None = None,
        min_citations: int | None = None,
        max_citations: int | None = None,
        refereed: bool | None = None,
    ) -> Self:
        """Select a subset of publications based on criteria."""
        selected_pubs = []
        for p in self.publications:
            if year_min is not None and p.year < year_min:
                continue
            if year_max is not None and p.year > year_max:
                continue
            if min_citations is not None and p.citation_count < min_citations:
                continue
            if max_citations is not None and p.citation_count > max_citations:
                continue
            if refereed is not None:
                if refereed and not p.refereed:
                    continue
                if not refereed and p.refereed:
                    continue
            selected_pubs.append(p)

        return PubList(publications=tuple(selected_pubs))
