"""Generate LaTeX for presentations section."""

import re

from astro_cv.formats.latex import myformat
from .datatype import Presentation, PresentationEntry


def _href(url: str, text: str) -> str:
    """Build a URL-safe hyperlink for presentation titles."""
    url = url.replace("&", r"\&").replace("%", r"\%")
    text = text.replace("&", r"\&").replace("%", r"\%")
    return rf"\href{{{url}}}{{{text}}}"


def _normalize_title(talk: PresentationEntry) -> str:
    """Normalize talk titles and embedded links into safe LaTeX."""
    if talk.URL:
        return _href(talk.URL, talk.Title)

    href_match = re.fullmatch(r"\\href\{([^}]*)\}\{(.+)\}", talk.Title)
    if href_match:
        return _href(href_match.group(1), href_match.group(2))

    return talk.Title


def create(data: Presentation) -> str:
    """Generate LaTeX for presentations section.

    Parameters
    ----------
    data : Presentation
        Presentations data.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    out = []

    BLANK = "\n\n" + r"\blankline" + "\n\n"
    HLINE = "\n\n" + r"\hline" + "\n\n"

    def write_talks(talk_list: list[PresentationEntry]) -> str:
        """Format a list of talks."""
        result = r"\begin{enumerate}"

        for talk in sorted(
            talk_list,
            key=lambda x: x.StartDate,
            reverse=True,
        ):
            date = talk.StartDate

            # Format title with optional URL
            title = _normalize_title(talk)

            # Format awards if present
            prize = ""
            if talk.Awards:
                prize = r"[\textbf{Prize for %s}]" % (talk.Awards.replace(";", " and"))

            result += myformat(
                r"\item ``<% title %>'' at <% Name %>, <% City %>, <% Country %> (<% date %>) <% prize %>",
                title=title,
                Name=talk.Name,
                City=talk.City,
                Country=talk.Country,
                date=date.strftime("%b %Y"),
                prize=prize,
            )
            result += "\n"

        result += r"\end{enumerate}"
        return result

    # Invited talks
    if data.invited_talks:
        out.append(r"\textbf{Invited Talks}")
        out.append(HLINE)
        out.append(write_talks(data.invited_talks))
        out.append(BLANK)

    # Seminars
    if data.seminars:
        out.append(r"\textbf{Seminars}")
        out.append(HLINE)
        out.append(r"\begin{enumerate}")

        for talk in sorted(
            data.seminars,
            key=lambda x: x.StartDate,
            reverse=True,
        ):
            date = talk.StartDate

            title = _normalize_title(talk)

            out.append(
                myformat(
                    r"\item ``<% title %>'', <% Location %> (<% date %>)",
                    title=title,
                    Location=talk.City,
                    date=date.strftime("%b %Y"),
                )
            )

        out.append(r"\end{enumerate}")
        out.append(BLANK)

    # Contributed talks
    if data.contributed_talks:
        out.append(r"\textbf{Contributed Talks}")
        out.append(HLINE)
        out.append(write_talks(data.contributed_talks))
        out.append(BLANK)

    # Posters
    if data.write_posters and data.posters:
        out.append(r"\textbf{Posters}")
        out.append(HLINE)
        out.append(write_talks(data.posters))
        out.append(BLANK)

    # Local talks
    if data.write_local_talks and data.local_talks:
        out.append(r"\textbf{Local Talks}")
        out.append(HLINE)
        out.append(r"\begin{enumerate}")

        for talk in data.local_talks:
            date_str = talk.StartDate

            if date_str:
                date = talk.StartDate
                date_str = date.strftime("%b %Y")

            title = _normalize_title(talk)

            out.append(
                myformat(
                    r"\item ``<% title %>'' at <% Name %>, <% Location %> (<% date %>)",
                    title=title,
                    Name=talk.Name,
                    Location=talk.City,
                    date=date_str,
                )
            )

        out.append(r"\end{enumerate}")
        out.append(BLANK)

    return "\n".join(out)
