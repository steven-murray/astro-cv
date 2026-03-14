"""Generate LaTeX for research interests section."""

from astro_cv.formats.latex import myformat
from .datatype import ResearchInterests


def create(data: ResearchInterests) -> str:
    """Generate LaTeX for research interests section.

    Parameters
    ----------
    data : ResearchInterests
        Research interests data loaded from TOML.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    out = []

    for category, topics in data.interests.items():
        topics_str = ", ".join(topics)
        out.append(
            myformat(
                r"\textbf{<% category %>}: <% topics %>\\",
                category=category,
                topics=topics_str,
            )
        )

    return "\n".join(out)
