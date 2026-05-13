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
    \begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}X@{\hspace{1.25em}}>{\raggedleft\arraybackslash}p{0.40\textwidth}@{}}
    \href{<% institution_url %>}{<% department_name %>} & \href{mailto:<% email %>}{<% email %>}~\faEnvelope\\
    <% institution_name %> & <% website_1 %>\\
    <% institution_street %> & <% website_2 %>\\
    <% institution_location %>, <% institution_country %> & <% website_3 %>\\
    \end{tabularx}
    \vspace{2mm}
    """

    wb = {}
    for i, website in enumerate(config.websites):
        kind = website.kind
        webid = website.id

        if kind.lower() == "linkedin":
            icon = website.icon or r"\faLinkedinSquare"
            url = website.url or f"https://www.linkedin.com/in/{webid}"
        elif kind.lower() == "github":
            icon = website.icon or r"\faGithub"
            url = website.url or f"https://github.com/{webid}/"
        elif kind.lower() == "orcid":
            icon = website.icon or r"\faOrcid"
            url = website.url or f"https://orcid.org/{webid}"
        elif kind.lower() == "web":
            icon = website.icon or r"\faLaptop"
            url = website.url
        elif kind:
            icon = website.icon or r"\faLaptop %s: " % kind
            url = website.url
        else:
            icon = website.icon or r"\faLaptop: "
            url = website.url

        if kind.lower() == "web":
            label = webid or "Personal Website"
        else:
            label = webid or url

        wb[kind] = r"\href{%s}{%s}\hspace{0.35em}%s" % (url, label, icon)

    website_values = [wb[w.kind] for w in config.websites]
    while len(website_values) < 3:
        website_values.append("")

    out = myformat(
        contact_information,
        escape_amp=False,
        institution_url=config.institution.url,
        department_name=config.institution.department_name,
        institution_name=config.institution.name,
        institution_street=config.institution.street,
        institution_location=config.institution.location,
        institution_country=config.institution.country,
        email=config.personal.email,
        website_1=website_values[0],
        website_2=website_values[1],
        website_3=website_values[2],
    )

    out = myformat(out, **wb)

    return out
