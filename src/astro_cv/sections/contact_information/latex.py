"""LaTeX generation logic for contact information section."""

from astro_cv.formats.latex import myformat

from .datatype import ContactInformation


def create(config: ContactInformation) -> str:
    """Generate LaTeX for contact information section.

    Args:
        config: ContactInformation configuration object

    Returns:
        LaTeX string for the contact information section
    """
    contact_information = r"""%
    \newlength{\rcollength}\setlength{\rcollength}{3.5in}%
    %
    \href{<% institution_url %>}{<% department_name %>}

    \begin{tabular}[t]{@{}p{\textwidth-\rcollength -0.2in}p{\rcollength}}
     <% institution_name %>,     &  \hfill <% phone_number %>~\faPhone \\
     <% institution_street %>,	 &  \hfill \href{mailto:<% email %>}{<% email %>}~\faEnvelopeO \\
     <% institution_location %>, <% institution_country %> &
    \end{tabular}

    \vspace{5mm}

    \noindent\begin{tabularx}{\textwidth}{<% ncols %>}
        <% websites %>
    \end{tabularx}
    \vspace{2mm}
    """

    wb = {}
    for i, website in enumerate(config.websites):
        kind = website.kind
        webid = website.id

        if kind.lower() == "linkedin":
            icon = website.icon or r"\faLinkedinSquare~"
            url = website.url or f"https://www.linkedin.com/in/{webid}"
        elif kind.lower() == "github":
            icon = website.icon or r"\faGithub~"
            url = website.url or f"https://github.com/{webid}/"
        elif kind.lower() == "orcid":
            icon = website.icon or r"\faOrcid~"
            url = website.url or f"https://orcid.org/{webid}"
        elif kind.lower() == "web":
            icon = website.icon or r"\faLaptop~"
            url = website.url
        elif kind:
            icon = website.icon or r"\faLaptop~%s: " % kind
            url = website.url
        else:
            icon = website.icon or r"\faLaptop~: "
            url = website.url

        wb[kind] = r"\href{%s}{%s\verb|%s|}" % (url, icon, webid or url)

    ncols = max(len(config.websites), 3)
    websites = " \\".join(
        " & ".join(f"<% {w.kind} %>" for w in ws[:ncols])
        for ws in [
            config.websites[i : i + ncols]
            for i in range(0, len(config.websites), ncols)
        ]
    )

    out = myformat(
        contact_information,
        escape_amp=False,
        institution_url=config.institution.url,
        department_name=config.institution.department_name,
        institution_name=config.institution.name,
        institution_street=config.institution.street,
        institution_location=config.institution.location,
        institution_country=config.institution.country,
        phone_number=config.personal.phone_number,
        email=config.personal.email,
        ncols="Y" * ncols,
        websites=websites,
    )

    out = myformat(out, **wb)

    return out
