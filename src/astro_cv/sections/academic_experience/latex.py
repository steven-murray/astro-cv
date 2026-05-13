"""Generate LaTeX for academic experience section."""

from astro_cv.formats.latex import myformat, format_year_range
from .datatype import AcademicExperience, AcademicExperienceEntry
import attrs
from collections.abc import Sequence


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

    def _date_range(entry: AcademicExperienceEntry) -> str:
        return format_year_range(entry.start_year, entry.end_year)

    def _row(main: str, date: str) -> str:
        template = r"""
\noindent\begin{tabularx}{\linewidth}{@{}X r@{}}
<% main %> & \textbf{<% date %>} \\
\end{tabularx}
"""
        return myformat(template, main=main, date=date)

    def _double_row(
        main_top: str, main_bottom: str, date: str, value: str, bold_value: bool = True
    ) -> str:
        value_fmt = rf"\textbf{{{value}}}" if bold_value else value
        template = r"""
\noindent\begin{tabularx}{\linewidth}{@{}X r@{}}
<% main_top %> & \textbf{<% date %>} \\
<% main_bottom %> & <% value %> \\
\end{tabularx}
"""
        return myformat(
            template,
            main_top=main_top,
            main_bottom=main_bottom,
            date=date,
            value=value_fmt,
        )

    def _href(url: str, text: str) -> str:
        url = url.replace("&", r"\&").replace("%", r"\%")
        text = text.replace("&", r"\&").replace("%", r"\%")
        return rf"\href{{{url}}}{{{text}}}"

    out = []

    def create_subcategory(
        entries: Sequence[AcademicExperienceEntry],
        cat: str,
        label=None,
        item_spacing: str = r"\vspace{0.55em}",
        current_text: str = r"\phantom{0000}",
        value_bold: bool = True,
        **extra_format_kwargs,
    ):
        if len(entries) == 0:
            return ""

        backslash = "\\"
        linebreak = backslash * 2
        header = "\n".join(
            [
                f"{backslash}noindent{backslash}begin{{tabularx}}{{{backslash}linewidth}}{{@{{}}X r@{{}}}}",
                f"{backslash}textbf{{<% cat %>}} & {backslash}textbf{{<% date %> -- <% current_text %>}} {linebreak}",
                f"{backslash}end{{tabularx}}",
            ]
        )
        out = myformat(
            header,
            cat=label or cat,
            date=min(x.start_year for x in entries),
            current_text=current_text,
        )
        out += "\n"

        for x in sorted(entries, key=lambda x: x.start_year, reverse=True):
            date = _date_range(x)
            kw = attrs.asdict(x)
            kw["end_year"] = x.end_year if x.end_year not in (None, 0) else "present"
            for k, fnc in extra_format_kwargs.items():
                kw[k] = fnc(x)

            main = kw.pop("main")
            value = kw.pop("value", "")
            if value:
                top_line, bottom_line = (
                    main.split("\\newline ", 1) if "\\newline " in main else (main, "")
                )
                if bottom_line:
                    out += _double_row(
                        main_top=top_line,
                        main_bottom=bottom_line,
                        date=date,
                        value=value,
                        bold_value=value_bold,
                    )
                else:
                    out += _double_row(
                        main_top=main,
                        main_bottom="",
                        date=date,
                        value=value,
                        bold_value=value_bold,
                    )
            else:
                out += _row(main=main, date=date)
            out += "\n"
            out += item_spacing
            out += "\n"

        out += r"\blankline"
        out += "\n\n"

        return out

    # Add each category if not omitted
    if not data.omit_grants:
        out.append(
            create_subcategory(
                data.grants,
                "Grants",
                item_spacing=r"\vspace{0.85em}",
                main=lambda x: rf"{x.grant}\newline \textit{{{x.title}}}, {x.authors}",
                value=lambda x: x.amount.replace("$", r"\$") if x.amount else "",
                value_bold=False,
            )
        )

    if not data.omit_collaborations:
        out.append(
            create_subcategory(
                data.collaborations,
                "Collaborations",
                main=lambda x: f"{x.group} [CI {x.principal_investigator}]",
            )
        )

    if not data.omit_committees:
        out.append(
            create_subcategory(
                data.committees,
                "Memberships and Committees",
                main=lambda x: f"{x.committee} [{x.role}]",
            )
        )

    if not data.omit_referees:
        out.append(
            create_subcategory(
                data.referees,
                "Journal Referee",
                main=lambda x: f"Referee for {x.journal}",
            )
        )

    if not data.omit_lecturing:
        out.append(
            create_subcategory(
                data.lecturing,
                "Lecturing",
                main=lambda x: (
                    f"{x.course_code} Lecture {x.course_name} {x.institution}"
                ),
            )
        )

    if not data.omit_supervision:
        out.append(
            create_subcategory(
                data.supervision,
                "Supervision",
                label=r"Supervision ($\dagger$ indicates primary supervisor)",
                main=lambda x: (
                    f"{'$\\dagger$ ' if not x.co_supervised else ''}"
                    f"{x.level}: {x.student_name}"
                ),
            )
        )

    if not data.omit_teaching:
        out.append(
            create_subcategory(
                data.teaching,
                "Teaching",
                main=lambda x: (
                    f"{x.level} `{x.course_name}`: \\textit{{{x.role}}} ({x.institution})"
                ),
            )
        )

    if not data.omit_outreach:
        out.append(
            create_subcategory(
                data.outreach,
                "Outreach",
                main=lambda x: (
                    f"{_href(x.url, x.activity) if x.url else x.activity}, {x.location}"
                ),
            )
        )

    if not data.omit_industry:
        out.append(
            create_subcategory(
                data.industry,
                "Industry and Inter-disciplinary Engagement",
                main=lambda x: (
                    f"\\textbf{{{x.company}:}} {x.project}. \\textit{{{x.description}}}"
                ),
            )
        )

    if not data.omit_prof_training:
        out.append(
            create_subcategory(
                data.prof_training,
                "Professional Training",
                main=lambda x: f"{x.name}, {x.place}",
            )
        )

    if not data.omit_personal_training:
        out.append(
            create_subcategory(
                data.personal_training,
                "Personal Training",
                main=lambda x: x.name,
            )
        )

    return "\n".join([s for s in out if s])
