"""Generate LaTeX for press releases section."""

import datetime
from astro_cv.formats.latex import myformat
from .datatype import PressReleases, PressReleaseEntry


def create(data: PressReleases) -> str:
    """Generate LaTeX for press releases section.

    Parameters
    ----------
    data : PressReleases
        Press releases data.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    if not data.articles and not data.events:
        return ""

    out = []

    BLANK = "\n\n" + r"\blankline" + "\n\n"
    HLINE = "\n\n" + r"\hline" + "\n\n"

    def format_entry(entry: PressReleaseEntry) -> str:
        """Format a single press release entry."""
        # Parse date
        if entry.Date:
            date = datetime.datetime.strptime(entry.Date, "%d/%m/%Y")
            date_str = date.strftime("%b %Y")

        # Format title with optional link
        if entry.Link:
            title = myformat(
                r"\href{<% Link %>}{<% Title %>}", Link=entry.Link, Title=entry.Title
            )
        else:
            title = entry.Title

        # Format authors
        authors_list = entry.get_authors_list()
        if authors_list:
            authors_str = ", ".join(authors_list)
        else:
            authors_str = ""

        # Build the entry
        result = myformat(r"\item ``<% title %>''", title=title)

        if authors_str:
            result += myformat(r" by <% authors %>", authors=authors_str)

        if entry.MediaOffice:
            result += myformat(r", <% MediaOffice %>", MediaOffice=entry.MediaOffice)

        if entry.Location:
            result += myformat(r", <% Location %>", Location=entry.Location)

        result += myformat(r" (<% date %>)", date=date_str)

        return result

    # Articles
    if data.articles:
        out.append(r"\textbf{Articles}")
        out.append(HLINE)
        out.append(r"\begin{enumerate}")

        for article in sorted(data.articles, key=lambda x: x.Date, reverse=True):
            out.append(format_entry(article))

        out.append(r"\end{enumerate}")
        out.append(BLANK)

    # Events
    if data.events:
        out.append(r"\textbf{Events}")
        out.append(HLINE)
        out.append(r"\begin{enumerate}")

        for event in sorted(data.events, key=lambda x: x.Date, reverse=True):
            out.append(format_entry(event))

        out.append(r"\end{enumerate}")
        out.append(BLANK)

    return "\n".join(out)
