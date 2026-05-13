"""Generate LaTeX for professional experience section."""

from astro_cv.formats.latex import myformat, format_year_range
from .datatype import ProfessionalExperience
import attrs


def _location(job) -> str:
    parts = [job.organisation, job.city, job.state]
    parts = [part for part in parts if part]
    return ", ".join(parts)


def create(data: ProfessionalExperience) -> str:
    """Generate LaTeX for professional experience section.

    Parameters
    ----------
    data : ProfessionalExperience
        Professional experience data loaded from TOML.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    jobs = data.filtered_jobs()
    out = []
    backslash = "\\"
    linebreak = backslash * 2

    for job in jobs:
        # Format years
        year_str = format_year_range(job.start_year, job.end_year)

        preformat = "\n".join(
            [
                "%",
                f"        {backslash}begin{{tabularx}}{{{backslash}linewidth}}{{@{{}}X r@{{}}}}",
                f"        {backslash}textbf{{<% title %>}} & {backslash}textbf{{<% dates_ %>}} {linebreak}",
                f"        <% location %> & {linebreak}",
                f"        {backslash}end{{tabularx}}",
                "",
                f"        {backslash}blankline",
                "",
                "        ",
            ]
        )
        out.append(
            myformat(
                preformat,
                dates_=year_str,
                location=_location(job),
                **attrs.asdict(job),
            )
        )

    return "\n".join(out)
