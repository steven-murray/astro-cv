"""LaTeX generation logic for academic references section."""

from astro_cv.formats.latex import myformat

from .datatype import AcademicReferences


def create(config: AcademicReferences) -> str:
    """Generate LaTeX for academic references section.

    Args:
        config: AcademicReferences configuration object

    Returns:
        LaTeX string for the academic references section
    """
    maxref = config.maxref if config.maxref is not None else len(config.references)

    out = r"\begin{tabular}{ l r }" + "\n"
    out += " \\\\ \n".join(
        myformat(
            r"\textbf{<% name %>} & \href{mailto:<% email %>}{<% email %>}",
            name=ref.name,
            email=ref.email,
        )
        for ref in config.references[:maxref]
    )

    out += "\n"
    out += r"\end{tabular}"
    return out
