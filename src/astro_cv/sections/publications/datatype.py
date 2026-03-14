"""Publications section datatype."""

import tomllib
from pathlib import Path
from functools import cached_property
from typing import Self, Union
import attrs
import tomli_w


@attrs.define(frozen=True)
class Publication:
    """Class to hold a paper."""

    title: str
    authors: list[str]
    year: int
    bibcode: str
    refereed: bool
    doi: str
    volume: int | None = None
    page: int | None = None

    citation_count: int = 0
    read_count: int = 0
    orcid_pub: bool = False
    aff: list[str] = attrs.field(factory=list)
    pub: str = ""
    doctype: str = ""

    @property
    def citations_per_year(self) -> float:
        """Citations per year."""
        from datetime import datetime

        current_year = datetime.now().year
        years_since_pub = max(1, current_year - self.year)
        return self.citation_count / years_since_pub


def _to_tuple_of_pubs(pubs: list | tuple | None) -> tuple[Publication, ...]:
    """Convert a list of publication dicts to a tuple of Publication objects."""
    if pubs is None or (isinstance(pubs, (list, tuple)) and len(pubs) == 0):
        return tuple()

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


@attrs.define(frozen=True, kw_only=True)
class PublicationList:
    """Class to hold a list of publications."""

    # Settings from TOML
    library: str
    surname: str

    publications: Union[tuple[Publication, ...], list, tuple] = attrs.field(
        factory=tuple, converter=_to_tuple_of_pubs
    )

    students: list[str] = attrs.field(factory=list)
    do_proceedings: bool = False
    top_n: int = 4
    alphabet_n: int = 12
    highlight_cite_per_year: int = 5
    other_bibcodes: list[str] = attrs.field(factory=list)
    accepted: list[str] = attrs.field(factory=list)

    def __len__(self) -> int:
        return len(self.publications)

    def __iter__(self):
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

    def keys(self):
        return self._dictform.keys()

    def values(self):
        return self._dictform.values()

    def items(self):
        return self._dictform.items()

    @classmethod
    def from_dict(cls, data: dict[str, dict], **kwargs) -> Self:
        """Create a PublicationList from a dict of publication dicts."""
        pubs = tuple(data.values())
        return cls(publications=pubs, **kwargs)

    @classmethod
    def read_toml(cls, path: Path | str) -> Self:
        """Read a PublicationList settings from TOML file.

        Note: This reads settings only. Publications are loaded via connector.
        """
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)

        settings = data.get("settings", {})

        return cls(
            publications=tuple(),  # Will be populated by connector
            library=settings.get("library", ""),
            surname=settings.get("surname", ""),
            students=settings.get("students", []),
            do_proceedings=settings.get("do_proceedings", False),
            top_n=settings.get("top_n", 4),
            alphabet_n=settings.get("alphabet_n", 12),
            highlight_cite_per_year=settings.get("highlight_cite_per_year", 5),
            other_bibcodes=settings.get("other_bibcodes", []),
            accepted=settings.get("accepted", []),
        )

    def write_toml(self, path: Path) -> None:
        """Write the PublicationList to a TOML file."""
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

        return attrs.evolve(self, publications=tuple(selected_pubs))
