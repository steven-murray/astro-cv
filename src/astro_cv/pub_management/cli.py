"""CLI commands for publication management."""

import time
import tomllib

import cyclopts
from ads.exceptions import APIResponseError
from ads.libraries import Library
from rich.console import Console

from termgraph import Data, Args, BarChart, Colors

from astro_cv.pub_management.nasa_ads import (
    add_new_papers_to_library,
    build_query,
    compare_query_to_library,
    obtain_library_papers,
    obtain_query_papers,
    remove_excess_papers_from_library,
    obtain_library_papers_not_in_orcid,
    write_library_cache,
    read_library_cache,
)
from .datatypes import PubList
from .stats import (
    compute_h_index,
    compute_i10_index,
    citation_distribution,
    average_citations,
    median_citations,
    total_citations,
    average_citations_per_year,
    top_cited_papers,
)

console = Console()

app = cyclopts.App(name="ads", help="Manage NASA ADS publication libraries.")


def retry_on_timeout(func, *args, max_retries=3, **kwargs):
    """Retry a function if it times out.

    Args:
        func: Function to call
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        console: Rich console for status messages
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        APIResponseError: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except APIResponseError as e:
            if "504" in str(e) or "Gateway Time-out" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff: 5s, 10s, 15s
                    if console:
                        console.print(
                            f"[yellow]API timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})[/yellow]"
                        )
                    time.sleep(wait_time)
                    continue
            raise


def _draw_bar_chart(title: str, data: dict[str, int], color=Colors.Green) -> None:
    chart_data = Data(data=list(data.values()), labels=[str(k) for k in data.keys()])

    args = Args(
        width=console.width - 10,
        title=title,
        colors=[color],
    )

    chart = BarChart(chart_data, args)
    chart.draw()


@app.command
def report(
    repo: cyclopts.types.ExistingDirectory, refereed: bool = False, min_year: int = 0
):
    """Report summary of publication library and cache.

    Args:
        repo: Path to your CV configuration repository.
        refereed: Whether to include only refereed publications.
    """
    cache = repo / "ads" / "library-cache.toml"
    if not cache.exists():
        console.print(
            f"[bold red]No library cache found at {cache}. Run [bold]astro-cv ads refresh-cache[/bold] to create one.[/bold red]"
        )
        return

    papers = PubList.read_toml(cache)
    if min_year > 0:
        papers = papers.select(year_min=min_year)

    if refereed:
        papers = papers.select(refereed=True)

    console.print("[bold]Library Report[/bold]")
    console.print(f"Total papers in library: [bold green]{len(papers)}[/bold green]")
    total_cites = total_citations(papers)
    console.print(f"Total citations in library: [bold green]{total_cites}[/bold green]")

    console.print(
        f"h-index of library: [bold green]{compute_h_index(papers)}[/bold green]"
    )

    recent_papers = papers.select(year_min=(time.localtime().tm_year - 5))
    h5_index = compute_h_index(recent_papers)
    console.print(f"h5-index of library: [bold green]{h5_index}[/bold green]")
    console.print(
        f"i10-index of library: [bold green]{compute_i10_index(papers)}[/bold green]"
    )

    console.print(
        f"Median citations per paper: [bold green]{median_citations(papers):.2f}[/bold green]"
    )
    console.print(
        f"Average citations per paper: [bold green]{average_citations(papers):.2f}[/bold green]"
    )
    console.print(
        f"Total citations: [bold green]{total_citations(papers)}[/bold green]"
    )

    # Simple bar chart
    cite_dist = citation_distribution(papers)
    _draw_bar_chart(
        title="Citation Distribution",
        data=cite_dist,
    )
    # Distribution of papers per year
    papers_per_year = {}
    for p in papers:
        year = p.year
        papers_per_year[year] = papers_per_year.get(year, 0) + 1

    _draw_bar_chart(
        title="Papers per Year",
        data=papers_per_year,
    )

    # Distribution of papers per journal
    papers_per_journal = {}
    for p in papers:
        journal = p.pub if p.pub else "Unknown"
        papers_per_journal[journal] = papers_per_journal.get(journal, 0) + 1
    # Sort the journals by number of papers and take top 10
    papers_per_journal = dict(
        sorted(papers_per_journal.items(), key=lambda item: item[1], reverse=True)[:10]
    )

    _draw_bar_chart(
        title="Papers per Journal",
        data=papers_per_journal,
    )

    # Distributions of citations per year
    citations_per_year = {}
    for p in papers:
        year = p.year
        citations_per_year[year] = citations_per_year.get(year, 0) + p.citation_count

    _draw_bar_chart(
        title="Citations per Year",
        data=citations_per_year,
    )

    # Top cited papers
    top_papers = top_cited_papers(papers, n=5)
    console.print("\n[bold]Top 5 Cited Papers:[/bold]")
    for p in top_papers:
        console.print(
            f"  [[bold]{p.citation_count} citations[/bold]] {p.title[0]} [cyan]({p.year})[/cyan]"
        )

    # Top cited papers per year
    top_papers_per_year = top_cited_papers(papers, n=5, per_year=True)
    console.print("\n[bold]Top 5 Cited Papers Per Year:[/bold]")
    for p in top_papers_per_year:
        console.print(
            f"  [[bold]{p.citations_per_year:.1f}[/bold]] {p.title[0]} [cyan]({p.year})[/cyan]"
        )

    # Average citations per year
    avg_cites_per_year = average_citations_per_year(papers)
    console.print(
        f"\n[bold]Average Citations Per Year:[/bold] [bold green]{avg_cites_per_year:.2f}[/bold green]"
    )


@app.command
def refresh_cache(repo: cyclopts.types.ExistingDirectory):
    """Refresh the local cache of the ADS library.

    This does not update your ADS library, it only fetches the current state of the
    library and saves it to a local cache file for reporting and comparison purposes.

    Running `astro-cv ads manage` will automatically refresh the cache after making any
    changes to the library, so you don't need to run this command manually unless you
    want to update the cache without making changes to the library.
    """
    # Write the library to cache
    cache = repo / "ads" / "library-cache.toml"
    config = repo / "ads" / "config.toml"

    with open(config, "rb") as fl:
        cfg = tomllib.load(fl)

    library = Library(cfg["library"])

    cached_library = read_library_cache(cache)
    papers = obtain_library_papers(library, extra_fields=("citation_count",))

    if cached_library:
        cachepubs = cached_library["publications"]

        new_citations = {}
        for p in papers:
            cached_paper = cachepubs.get(p.bibcode)
            oldcount = cached_paper.get("citation_count", 0) if cached_paper else 0
            if cached_paper and p.citation_count != oldcount:
                new_citations[p.bibcode] = (
                    oldcount,
                    p.citation_count,
                    p.citation_count - oldcount,
                )

        console.print(
            f"[bold]Comparing to previous snapshot at '{cached_library['date_compiled']}'[/bold]"
        )
        console.print(
            f"[bold green]Total citation count changes:[/bold green] {sum(x[2] for x in new_citations.values())}"
        )
        console.print(
            f"[bold green]Total papers with citation count changes:[/bold green] {len(new_citations)}"
        )
        if new_citations:
            console.print("[bold green]Top 5 citation count increases:[/bold green]")
            top_increases = sorted(
                new_citations.items(), key=lambda x: x[1][2], reverse=True
            )[:5]
            for bibcode, (old_count, new_count, diff) in top_increases:
                console.print(
                    f"  - [dim]{bibcode}:[/dim] {old_count} -> {new_count} ([green]+{diff}[/green])"
                )

        new_papers = [p for p in papers if p.bibcode not in cachepubs]
        if new_papers:
            console.print(
                "[bold green]New Papers added since last snapshot:[/bold green]"
            )
            for p in new_papers:
                console.print(
                    f"  - [dim]{p.bibcode}:[/dim] {p.title[0]} [cyan]({p.year})[/cyan]"
                )

    write_library_cache(papers, cache)
    console.print(f"[bold green]Library cache refreshed at {cache}[/bold green]")


@app.command
def manage(
    repo: cyclopts.types.ExistingDirectory,
):
    """Manage publications using NASA ADS.

    Args:
        repo: Path to your CV configuration repository.
    """
    config = repo / "ads" / "config.toml"

    if not config.exists():
        console.print(f"[bold red]Configuration file not found at {config}[/bold red]")
        return

    with open(config, "rb") as fl:
        cfg = tomllib.load(fl)

    library = Library(cfg["library"])

    false_lib = Library(cfg["false_lib"])

    # Build and execute query
    query = build_query(
        name=cfg["name"],
        affiliations=cfg["affiliations"],
        orcid=cfg["orcid"],
        started_year=cfg["started"],
        false_lib_id=false_lib.id,
    )

    console.print("[bold cyan]Performing following query:[/bold cyan]")
    console.print(f"  > [dim]{query}[/dim]")

    with console.status("[bold cyan]Querying ADS API...[/bold cyan]"):
        papers, indices, author_aff, orcids = retry_on_timeout(
            obtain_query_papers,
            query=query,
            name=cfg["name"],
            affiliations=cfg["affiliations"],
            orcid=cfg["orcid"],
            false_lib=false_lib,
        )

    # Get library papers and compare
    with console.status("[bold cyan]Fetching library papers...[/bold cyan]"):
        known_papers = retry_on_timeout(
            obtain_library_papers,
            library,
        )

    already_in, new_papers, excess_papers, new_indices, new_author_aff, new_orcids = (
        compare_query_to_library(papers, known_papers, indices, author_aff, orcids)
    )

    console.print(
        f"[bold green]Found {len(papers)} papers in the search.[/bold green] {len(already_in)} were already in your library. [bold yellow]{len(new_papers)} are new.[/bold yellow]"
    )

    # Update library interactively
    papers_to_print = remove_excess_papers_from_library(excess_papers, library)
    if papers_to_print:
        for p in papers_to_print:
            console.print(
                f"  [dim]{','.join(p.author)}:[/dim] {p.title[0]} [cyan]({p.year})[/cyan] / {p.aff} {p.orcid_pub}"
            )

    if new_papers:
        console.print(
            f"[bold yellow]Found {len(new_papers)} new papers, please select whether each one should be in your library:[/bold yellow]"
        )

    add_new_papers_to_library(
        new_papers, new_orcids, new_author_aff, new_indices, library, false_lib
    )

    # Check for papers not associated with ORCID
    with console.status("[bold cyan]Checking ORCID associations...[/bold cyan]"):
        orcid_papers = retry_on_timeout(
            obtain_library_papers_not_in_orcid,
            library,
            orcid=cfg["orcid"],
            unclaimable_bibcodes=cfg.get("orcid_not_claimable", []),
        )

    if orcid_papers:
        console.print(
            "[bold magenta]The following papers were in your library but are not associated with your ORCID on ADS:[/bold magenta]"
        )
        for p in orcid_papers:
            console.print(
                f"  - [dim]{p.author[0]}:[/dim] {p.title[0]} [cyan]({p.year})[/cyan]"
            )
        console.print("[bold]Follow this link to associate them:[/bold]")
        console.print(
            f"  [link=https://ui.adsabs.harvard.edu/search/q=docs(library%2F{library.id})%20NOT%20orcid%3A{cfg['orcid']}]https://ui.adsabs.harvard.edu/search/q=docs(library%2F{library.id})%20NOT%20orcid%3A{cfg['orcid']}[/link]"
        )

    # Refresh cache
    refresh_cache(repo)
