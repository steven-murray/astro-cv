"""Generate LaTeX for summary profile section."""

from astro_cv.formats.latex import myformat
from .datatype import SummaryProfile


def create(data: SummaryProfile) -> str:
    """Generate LaTeX for summary profile section.

    Renders the profile text inside a tcolorbox that spans the full text
    column, using the lightblue accent colour defined in the document setup.

    Parameters
    ----------
    data : SummaryProfile
        Summary profile data loaded from TOML.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    template = (
        r"\vspace{2mm}%"
        "\n"
        r"\noindent"
        "\n"
        r"\hspace*{-\marginparsep minus \marginparwidth}%"
        "\n"
        r"\begin{minipage}[t]{\textwidth+\marginparsep+\marginparwidth}%"
        "\n"
        r"\begin{tcolorbox}["
        r"enhanced, width=\columnwidth, colback=lightblue!5, colframe=lightblue!60!black, "
        r"boxrule=0pt, borderline west={2pt}{0pt}{lightblue!80!black}, "
        r"sharp corners, left=8pt, right=8pt, top=6pt, bottom=6pt, "
        r"before skip=0pt, after skip=3mm"
        r"]"
        "\n"
        r"<% text %>"
        "\n"
        r"\end{tcolorbox}%"
        "\n"
        r"\end{minipage}%"
    )
    return myformat(template, text=data.text)
