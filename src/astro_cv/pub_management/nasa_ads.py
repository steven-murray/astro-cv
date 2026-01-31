"""
Manage publications using NASA ADS (Astrophysics Data System).

To setup for calling the script, you must install the ads package from the following fork:
`pip install git+git://github.com/steven-murray/ads` and
the `questionary` and `pyyaml` packages (`pip install questionary pyyaml`).
You also must create an ADS API key (go to your settings page on ADS) and save it in
`~/.ads/dev_key`.

What happens under the hood is that it will perform an automatic search based on
members' names and affiliation, then it will compare that list to a library we maintain.
Anything new, and you will be prompted to add them to the library. Anything you decide NOT
to add to the library will be flagged as a false positive and added to a library of such, so
as never to come up again.
In the end, it will only print out docs in the library itself.
"""

# TODO: ability to add orcid

import ads
from datetime import datetime
from pathlib import Path

import questionary as qs
import tomli_w
import tomllib
from ads.libraries import Library

now = datetime.now()


def get_author_index(authors: list[str], name: str) -> list[int]:
    """Get the index of the author in the author list.

    Args:
        authors: List of author names from a paper
        name: Name to search for (can be "Last, First" or "First Last" format)

    Returns:
        List of indices where the author appears in the author list
    """
    if "," in name:
        first = name.split(",")[1].strip()
        last = name.split(",")[0].strip()
    else:
        first = name.split(" ")[0].strip()
        last = name.split(" ")[1:].strip()

    # Reduce by last name first.
    bools = [last in a for a in authors]

    if sum(bools) == 1:
        return [bools.index(True)]
    elif sum(bools) == 0:
        return []

    # Otherwise, there are multiple authors with the author's last name. Try matching first.
    bools = [
        b and a.split(",")[1].strip().startswith(first[0])
        for a, b in zip(authors, bools)
    ]

    if sum(bools) == 1:
        return [bools.index(True)]
    elif sum(bools) == 0:
        return []

    return [idx for idx, b in enumerate(bools) if b]


def build_query(
    name: str, affiliations: list[str], orcid: str, started_year: int, false_lib_id: str
) -> str:
    """Build an ADS query string based on author info.

    Args:
        name: Author name
        affiliations: List of affiliations to search for
        orcid: Author's ORCID ID
        started_year: Starting year for the search
        false_lib_id: ID of the false positive library to exclude

    Returns:
        ADS query string
    """
    quoted_affiliations = ['"' + aff + '"' for aff in affiliations]
    affiliation_q = " OR ".join(quoted_affiliations)
    year = f"year:{started_year}-{now.year}"

    query = f'(author:"{name}" aff:({affiliation_q}) {year}) OR orcid:{orcid} NOT docs(library/{false_lib_id})'
    return query


def obtain_query_papers(
    query: str, name: str, affiliations: list[str], orcid: str, false_lib: Library
):
    """Execute ADS query and filter papers by author affiliation and ORCID.

    Args:
        query: ADS query string
        name: Author name for filtering
        affiliations: List of affiliations for filtering
        orcid: Author's ORCID for filtering
        false_lib: Library of false positives

    Returns:
        Tuple of (papers, indices, author_affiliations, orcids)
    """
    papers = list(
        ads.SearchQuery(
            q=query,
            sort="date desc",
            max_pages=20,  # Reduced from 100 to prevent API timeouts
            fl=[
                "author",
                "title",
                "bibcode",
                "pub",
                "volume",
                "issue",
                "page",
                "year",
                "orcid_pub",
                "aff",
            ],
        )
    )

    # This shouldn't need to be done, but just in case...
    falsebibs = [
        p.bibcode
        for p in ads.SearchQuery(
            q=f"docs(library/{false_lib.id})",
            sort="date desc",
            max_pages=20,  # Reduced from 100 to prevent API timeouts
            fl=["bibcode"],
        )
    ]

    papers = [p for p in papers if p.bibcode not in falsebibs]

    # Get author indices and metadata
    indices = [get_author_index(p.author, name) for p in papers]
    author_aff = [[p.aff[idx] for idx in idxs] for p, idxs in zip(papers, indices)]
    orcids = [
        [p.orcid_pub[idx] if p.orcid_pub else "-" for idx in idxs]
        for p, idxs in zip(papers, indices)
    ]

    # Filter papers by ORCID match
    mask = [(orcid in orc or "-" in orc or not orc) for orc in orcids]
    papers = [p for m, p in zip(mask, papers) if m]
    indices = [p for m, p in zip(mask, indices) if m]
    author_aff = [p for m, p in zip(mask, author_aff) if m]
    orcids = [p for m, p in zip(mask, orcids) if m]

    # Filter papers by affiliation match
    mask = [
        not affs or any(any(a in aff for a in affiliations) for aff in affs)
        for affs in author_aff
    ]
    papers = [p for m, p in zip(mask, papers) if m]
    indices = [p for m, p in zip(mask, indices) if m]
    author_aff = [p for m, p in zip(mask, author_aff) if m]
    orcids = [p for m, p in zip(mask, orcids) if m]

    return papers, indices, author_aff, orcids


def obtain_library_papers(
    library: Library, exclude_orcid: str = "", extra_fields: tuple[str] | None = None
):
    """Get all papers currently in the library.

    Args:
        library: ADS Library instance
        exclude_orcid: Optional ORCID to exclude from results

    Returns:
        List of papers in the library
    """
    query = f"docs(library/{library.id})"
    if exclude_orcid:
        query += f" NOT orcid:{exclude_orcid}"

    fields = ["author", "title", "year", "bibcode", "aff", "orcid_pub"]
    if extra_fields:
        fields.extend(extra_fields)

    known_papers = list(
        ads.SearchQuery(
            q=query,
            fl=fields,
            sort="date desc",
            max_pages=20,  # Reduced from 100 to prevent API timeouts
        )
    )
    return known_papers


def compare_query_to_library(papers, known_papers, indices, author_aff, orcids):
    """Compare query results to library papers and categorize them.

    Args:
        papers: Papers from the query
        known_papers: Papers already in the library
        indices: Author indices for each paper
        author_aff: Author affiliations for each paper
        orcids: ORCIDs for each paper

    Returns:
        Tuple of (already_in, new_papers, excess_papers, new_indices, new_author_aff, new_orcids)
    """
    already_in = [p for p in papers if p in known_papers]
    new_papers = [p for p in papers if p not in known_papers]
    excess_papers = [p for p in known_papers if p not in papers]

    new_indices = [a for a, p in zip(indices, papers) if p not in known_papers]
    new_author_aff = [a for a, p in zip(author_aff, papers) if p not in known_papers]
    new_orcids = [a for a, p in zip(orcids, papers) if p not in known_papers]

    return (
        already_in,
        new_papers,
        excess_papers,
        new_indices,
        new_author_aff,
        new_orcids,
    )


def remove_excess_papers_from_library(excess_papers, library: Library):
    """Interactively remove excess papers from the library.

    Args:
        excess_papers: Papers in library but not in query results
        library: ADS Library instance

    Returns:
        List of papers to print if 'just print' option was selected
    """
    if not excess_papers:
        return []

    res = qs.select(
        f"WARNING: {len(excess_papers)} papers are in the library, but not in your search. Select whether to REMOVE them:",
        choices=["yes to all", "no to all", "choose each", "just print"],
    ).ask()

    papers_to_print = []
    if res == "yes to all":
        remove = [p.bibcode for p in excess_papers]
    elif res == "no to all":
        remove = []
    elif res == "just print":
        papers_to_print = excess_papers
        remove = []
    else:
        remove = []
        for p in excess_papers:
            res = qs.select(
                f"{','.join(p.author)}: {p.title[0]} ({p.year})",
                choices=["yes", "no"],
                default="yes",
            ).ask()
            if res == "yes":
                remove.append(p.bibcode)

    if remove:
        library.remove_documents(remove)

    return papers_to_print


def add_new_papers_to_library(
    new_papers,
    new_orcids,
    new_author_aff,
    new_indices,
    library: Library,
    false_lib: Library,
):
    """Interactively add new papers to the library.

    Args:
        new_papers: Papers found in query but not in library
        new_orcids: ORCID data for new papers
        new_author_aff: Affiliation data for new papers
        new_indices: Author indices for new papers
        library: Main ADS Library instance
        false_lib: False positive library instance
    """
    if not new_papers:
        return

    keep = []
    no_keep = []

    for p, orc, aff, idx in zip(new_papers, new_orcids, new_author_aff, new_indices):
        res = qs.select(
            f"{p.author[0]}: {p.title[0]} ({p.year}) orcid:{orc} aff:{aff} authnames: {[p.author[i] for i in idx]}",
            choices=["yes", "no", "not sure", "quit"],
            default="yes",
        ).ask()

        if res == "yes":
            keep.append(p.bibcode)
        elif res == "no":
            no_keep.append(p.bibcode)
        elif res == "quit":
            break

    if keep:
        library.add_documents(keep)
    if no_keep:
        false_lib.add_documents(no_keep)


def obtain_library_papers_not_in_orcid(
    library: Library,
    orcid: str,
    unclaimable_bibcodes: tuple[str] | None = None,
):
    """Get all papers currently in the library that are not associated with the given ORCID.

    Args:
        library: ADS Library instance
        exclude_orcid: ORCID to exclude from results

    Returns:
        List of papers in the library not associated with the given ORCID
    """
    papers = obtain_library_papers(library, exclude_orcid=orcid)

    # Further filter out unclaimable bibcodes if provided
    if unclaimable_bibcodes:
        papers = [p for p in papers if p.bibcode not in unclaimable_bibcodes]

    return papers


def write_library_cache(
    papers: list, cache_path: Path, has_citation_counts: bool = False
):
    """Write library papers to a TOML cache file.

    Args:
        papers: List of ADS Article objects to cache
        cache_path: Path to the cache file (e.g., 'my-cv-info/ads/library-cache.toml')
    """
    # Ensure the directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Get citation counts for all papers
    if not has_citation_counts:
        bibcodes = [p.bibcode for p in papers]
        citation_counts = {}
        pubs = {}
        properties = {}

        if bibcodes:
            # Query for citation counts in batches to avoid overwhelming the API
            cited_papers = list(
                ads.SearchQuery(
                    q=f"bibcode:({' OR '.join(bibcodes)})",
                    fl=["bibcode", "citation_count", "pub", "property"],
                    rows=min(len(bibcodes), 2000),
                    max_pages=1,
                )
            )
            citation_counts = {p.bibcode: p.citation_count or 0 for p in cited_papers}
            pubs = {p.bibcode: p.pub for p in cited_papers}
            properties = {p.bibcode: p.property for p in cited_papers}
    else:
        citation_counts = {p.bibcode: p.citation_count or 0 for p in papers}
        pubs = {p.bibcode: p.pub for p in papers}
        properties = {p.bibcode: p.property for p in papers}

    # Build the cache structure
    cache_data = {"date_compiled": datetime.now().isoformat(), "publications": {}}

    for paper in papers:
        cache_data["publications"][paper.bibcode] = this = {
            "author": paper.author,
            "title": paper.title,
            "year": paper.year,
            "bibcode": paper.bibcode,
            "aff": paper.aff,
            "orcid_pub": paper.orcid_pub or "",
            "pub": pubs.get(paper.bibcode, ""),
            "citation_count": citation_counts.get(paper.bibcode, 0),
            "refereed": "REFEREED" in properties.get(paper.bibcode, []),
        }

        if any(val is None for key, val in this.items()):
            raise ValueError(
                f"Warning: Paper {paper.bibcode} has missing fields.\n{this}"
            )

    # Write to TOML file
    with open(cache_path, "wb") as f:
        tomli_w.dump(cache_data, f)


def read_library_cache(cache_path: Path) -> dict:
    """Read library papers from a TOML cache file.

    Args:
        cache_path: Path to the cache file (e.g., 'my-cv-info/ads/library-cache.toml')

    Returns:
        Dictionary with 'date_compiled' and 'publications' keys
        Returns empty dict if file doesn't exist
    """
    if not cache_path.exists():
        return {}

    with open(cache_path, "rb") as f:
        return tomllib.load(f)
