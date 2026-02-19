"""Generate LaTeX for professional experience section."""

from astro_cv.formats.latex import myformat
from .datatype import ProfessionalExperience
import attrs


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

    for job in jobs:
        # Format years
        if job.end_year == 0:
            year_str = myformat(r"<% start %> -- present", start=str(job.start_year))
        elif job.start_year == job.end_year:
            year_str = str(job.start_year)
        else:
            year_str = myformat(
                r"<% start %> -- <% end %>",
                start=str(job.start_year),
                end=str(job.end_year),
            )

        preformat = r"""%
        \textbf{<% organisation %>}, <% city %>, <% state %>

        <% title %>, (<% dates_ %>)

        \blankline

        """
        out.append(myformat(preformat, dates_=year_str, **attrs.asdict(job)))

    return "\n".join(out)
