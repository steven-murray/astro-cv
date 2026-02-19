"""Generate LaTeX for academic experience section."""

from astro_cv.formats.latex import myformat
from .datatype import AcademicExperience, AcademicExperienceEntry
import attrs


def create(data: AcademicExperience) -> str:
    """Generate LaTeX for academic experience section.

    Parameters
    ----------
    data : AcademicExperience
        Academic experience data.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    BLANK = "\n\n" + r"\blankline" + "\n\n"
    HLINE = "\n\n" + r"\hline" + "\n\n"

    out = []

    def create_subcategory(
        entries: list[AcademicExperienceEntry],
        cat: str,
        fmt_string: str,
        label=None,
        **extra_format_kwargs,
    ):
        if len(entries) > 0:
            # Get the type of date defining this subcategory
            out = myformat(
                r"\textbf{<% cat %>} \hfill \textbf{<% date %> -- Present}",
                cat=label or cat,
                date=min(x.start_year for x in entries),
            )

            out += "\n"
            out += r"\begin{innerlist}"
            out += "\n"

            for x in sorted(entries, key=lambda x: x.start_year, reverse=True):
                kw = attrs.asdict(x)
                for k, fnc in extra_format_kwargs.items():
                    kw[k] = fnc(x)

                out += myformat(fmt_string, **kw)
                out += "\n\n"

            out += r"\end{innerlist}"
            out += "\n\n"
            out += r"\blankline"
            out += "\n\n"

            return out
        else:
            return ""

    def format_category(entries: list[AcademicExperienceEntry], label: str) -> str:
        """Format a category of academic experience."""
        if not entries:
            return ""

        result = myformat(r"\textbf{<% label %>}", label=label)
        result += HLINE
        result += r"\begin{innerlist}"

        for entry in entries:
            result += myformat(
                r"\item <% Name %>",
                Name=entry.Name,
            )
            result += "\n"

        result += r"\end{innerlist}"
        result += BLANK

        return result

    # Add each category if not omitted
    if not data.omit_grants:
        out.append(
            create_subcategory(
                data.grants,
                "Grants",
                r"\item <% authors %>\hfill<% start_year %>\\ \textit{<% title %>}, <% grant %>\hfill<% award_amount %>",
                award_amount=lambda x: (r"\textbf{%s}" % x.amount).replace("$", "\$")
                if x.amount
                else "",
            )
        )

    if not data.omit_collaborations:
        out.append(
            create_subcategory(
                data.collaborations,
                "Collaborations",
                r"\item <% group %> [CI <% principal_investigator %>], (<% start_year %>~--~<% end_year %>)",
            )
        )

    if not data.omit_committees:
        out.append(
            create_subcategory(
                data.committees,
                "Memberships and Committees",
                r"\item <% committee %> [<% role %>], (<% start_year %>~--~<% end_year %>)",
            )
        )

    if not data.omit_referees:
        out.append(
            create_subcategory(
                data.referees,
                "Journal Referee",
                r"\item Referee for <% journal %> (<% start_year %>~--~<% end_year %>)",
            )
        )

    if not data.omit_lecturing:
        out.append(
            create_subcategory(
                data.lecturing,
                "Lecturing",
                r"\item <% course_code %> Lecture<% course_name %> <% institution %> (<% start_year %>~--~<% end_year %>)",
            )
        )

    if not data.omit_supervision:
        out.append(
            create_subcategory(
                data.supervision,
                "Supervision",
                r"\item <% cosup %> <% level %> <% student %>: <% student_name %> (<% start_year %>~--~<% end_year %>)",
                cosup=lambda x: "Co-supervised" if x.co_supervised else "Supervised",
                student=lambda x: "student"
                if x.level in ["PhD", "Masters", "Honours"]
                else "",
            )
        )

    if not data.omit_teaching:
        out.append(
            create_subcategory(
                data.teaching,
                "Teaching",
                r"\item <% level %> `<% course_name %>': \textit{<% role %>} (<% institution %>, <% start_year %>~--~<% end_year %>)",
            )
        )

    if not data.omit_outreach:
        out.append(
            create_subcategory(
                data.outreach,
                "Outreach",
                r"\item <% activity %> (<% location %>, <% start_year %>/<% start_month %>/<% start_day %>",
                activity=lambda x: myformat(
                    r"\href{<% url %>}{<% activity %>}", url=x.url, activity=x.activity
                )
                if x.url
                else x.activity,
            )
        )

    if not data.omit_industry:
        out.append(
            create_subcategory(
                data.industry,
                "Industry and Inter-disciplinary Engagement",
                r"\item \textbf{<% company %>:} <% project %> (<% start_year %>~--~<% end_year %>). \textit{<% description %>}",
            )
        )

    if not data.omit_prof_training:
        out.append(
            create_subcategory(
                data.prof_training,
                "Professional Training",
                r"\item <% name %> (<% start_year %>/<% start_month %>/<% start_day %>)",
            )
        )

    if not data.omit_personal_training:
        out.append(
            create_subcategory(
                data.personal_training,
                "Personal Training",
                r"\item <% name %> (<% start_year %>/<% start_month %>/<% start_day %>)",
            )
        )

    return "\n".join([s for s in out if s])
