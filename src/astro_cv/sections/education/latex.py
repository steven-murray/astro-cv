"""LaTeX generation for education section."""

from astro_cv.formats.latex import myformat

from .datatype import Education, Institution, Degree, Supervisor

BLANK = "\n\n" + r"\blankline" + "\n\n"


def _format_location(inst: Institution) -> str:
    parts = [inst.city, inst.state, inst.country]
    parts = [p for p in parts if p]
    return ", ".join(parts)


def _format_subject(deg: Degree) -> str:
    if deg.subject_url and deg.subject:
        return myformat(
            r"\href{<% url %>}{<% subject %>}", url=deg.subject_url, subject=deg.subject
        )
    if deg.subject:
        return deg.subject
    return ""


def _format_supervisors(supervisors: list[Supervisor]) -> str:
    formatted = []
    for sup in supervisors:
        if sup.url:
            formatted.append(
                myformat(r"\href{<% url %>}{<% name %>}", url=sup.url, name=sup.name)
            )
        else:
            formatted.append(sup.name)
    return ", ".join(formatted)


def _include_degree(config: Education, degree: Degree) -> bool:
    if degree.level == "undergrad" and not config.keep_undergrad:
        return False
    if degree.level == "secondary" and not config.keep_secondary:
        return False
    return True


def _include_undergrad_courses(config: Education, degree: Degree) -> bool:
    if degree.level != "undergrad":
        return True
    return config.keep_undergrad_courses


def create(config: Education) -> str:
    """Generate LaTeX for education section."""
    out = []

    for inst in config.institutions:
        degrees = [d for d in inst.degrees if _include_degree(config, d)]
        if not degrees:
            continue

        location = _format_location(inst)
        if location:
            header = myformat(
                r"\href{<% url %>}{\textbf{<% name %>}}, <% location %>",
                url=inst.url,
                name=inst.name,
                location=location,
            )
        else:
            header = myformat(
                r"\href{<% url %>}{\textbf{<% name %>}}",
                url=inst.url,
                name=inst.name,
            )

        out.append(header)
        out.append(r"\begin{outerlist}")

        for degree in degrees:
            subject = _format_subject(degree)
            if subject:
                line = myformat(
                    r"\item[] <% title %>, <% subject %> (<% years %>)",
                    title=degree.title,
                    subject=subject,
                    years=degree.years,
                )
            else:
                line = myformat(
                    r"\item[] <% title %> (<% years %>)",
                    title=degree.title,
                    years=degree.years,
                )

            out.append(line)

            details = []
            if degree.thesis_title:
                details.append(
                    myformat(
                        r"\item Thesis Title: <% title %>", title=degree.thesis_title
                    )
                )
            if degree.thesis_topic:
                details.append(
                    myformat(
                        r"\item Thesis Topic: <% topic %>", topic=degree.thesis_topic
                    )
                )
            if degree.supervisors:
                details.append(
                    myformat(
                        r"\item Supervisors: <% supervisors %>",
                        supervisors=_format_supervisors(degree.supervisors),
                    )
                )
            if degree.area_of_study:
                details.append(
                    myformat(
                        r"\item Area of Study: <% area %>", area=degree.area_of_study
                    )
                )
            if degree.graduation:
                details.append(
                    myformat(r"\item Graduated: <% grad %>", grad=degree.graduation)
                )
            if degree.courses and _include_undergrad_courses(config, degree):
                details.append(r"\item Courses Taken:")
                details.append(r"\begin{itemize}")
                for course in degree.courses:
                    details.append(myformat(r"\item <% course %>", course=course))
                details.append(r"\end{itemize}")
            if degree.subjects:
                details.append(
                    myformat(
                        r"\item Subjects Taken (Marks scale E1-A10): <% subjects %>",
                        subjects=", ".join(degree.subjects),
                    )
                )

            if details:
                out.append(r"\begin{innerlist}")
                out.extend(details)
                out.append(r"\end{innerlist}")

        out.append(r"\end{outerlist}")
        out.append(r"\blankline")

    return "\n".join(out)
