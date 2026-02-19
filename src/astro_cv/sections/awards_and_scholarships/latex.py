"""Generate LaTeX for awards and scholarships section."""

from astro_cv.formats.latex import myformat
from .datatype import AwardsAndScholarships


def create(data: AwardsAndScholarships) -> str:
    """Generate LaTeX for awards and scholarships section.

    Parameters
    ----------
    data : AwardsAndScholarships
        Awards and scholarships data.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    from operator import itemgetter

    awards = data.filtered_awards()

    # Segregate awards by institution
    seg_awards = {}
    for a in awards:
        if a.Institution in seg_awards:
            seg_awards[a.Institution].append(a)
        else:
            seg_awards[a.Institution] = [a]

    seg_year = {k: max(int(a.DateReceived) for a in v) for k, v in seg_awards.items()}
    sorted_segyear = sorted(seg_year.items(), key=itemgetter(1), reverse=True)

    out = []
    for inst, year in sorted_segyear:
        out.append(myformat(r"\textbf{<% inst %>}", inst=inst))
        out.append(r"\begin{innerlist}")

        for award in seg_awards[inst]:
            duration_str = f", for {award.Duration}" if award.Duration else ""
            out.append(
                myformat(
                    r"\item <% Name %> (<% DateReceived %><% duration %>)",
                    duration=duration_str,
                    Name=award.Name,
                    DateReceived=award.DateReceived,
                )
            )

        out.append(r"\end{innerlist}")
        out.append(r"\blankline")

    return "\n\n".join(out)
