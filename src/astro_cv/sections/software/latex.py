"""LaTeX generation for software section."""

from astro_cv.formats.latex import myformat
from .datatype import SoftwareList

BLANK = "\n\n"


def create(software_list: SoftwareList) -> str:
    """Generate LaTeX for software section."""
    out = ""

    # Organizations section
    if software_list.organizations:
        orgs_by_contributions = sorted(
            software_list.organizations,
            key=lambda o: o.total_contributions,
            reverse=True,
        )

        out += r"\textbf{Organizations}"
        out += BLANK
        out += r"""Most of my software development occurs within teams, which are listed here (only organizations in which I've been active are listed). Each column gives the total number of my contributions made to the organization, and then shows the relative contribution in the form of \textbf{C}ommits, \textbf{P}Rs, \textbf{I}ssues and \textbf{R}eviews."""
        out += BLANK

        out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z r}
            \hline
            \textbf{Github Org} & \textbf{Description} & \textbf{Contr.} [C|P|I|R] \\
            \hline
        """

        for org in orgs_by_contributions:
            total = org.total_contributions
            out += myformat(
                r"\href{https://github.com/<% login %>}{<% login %>} & <% desc %> & \texttt{<% total %> [<% commits %>|<% issues %>|<% prs %>|<% reviews %>]} \\",
                login=org.login,
                desc=org.description[:50] if org.description else "",
                total=total,
                commits=f"{org.total_commits:03d}",
                issues=f"{org.total_issues:02d}",
                prs=f"{org.total_prs:02d}",
                reviews=f"{org.total_reviews:02d}",
            )

        out += r"""
        \hline
        \end{tabularx}
        \end{table}
        """
        out += BLANK

    # Original Codes section
    if software_list.original_repos:
        out += r"\textbf{Original Codes}"
        out += BLANK
        out += r"""Here I list notable codes that I originally authored and maintain."""
        out += BLANK
        out += r"\textbf{Key}: \faStar\ GitHub Stars | \faCodeBranch\ Forks"
        out += BLANK

        out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z c c}
            \hline
            \textbf{Repo} & \textbf{Description} &  \faStar\ & \faCodeBranch\ \\
            \hline
        """

        for repo in software_list.original_repos[: software_list.max_repos]:
            repo_name = repo.url.split("/")[-1]
            out += myformat(
                r"\href{<% url %>}{\bf <% name %>} & <% desc %> & <% stars %> & <% forks %> \\",
                url=repo.url,
                name=repo_name.replace("_", r"\_"),
                desc=repo.description[:60] if repo.description else "",
                stars=f"{repo.stargazers:02d}",
                forks=f"{repo.forks:02d}",
            )

        out += r"""
        \hline
        \end{tabularx}
        \end{table}
        """
        out += BLANK

    # Collaborative Codes section
    if software_list.collaborative_repos:
        out += r"\textbf{Collaborative Codes}"
        out += BLANK
        out += r"""Here I list notable codes that I contribute to collaboratively. They are listed in descending order of my contributions."""
        out += BLANK
        out += r"\textbf{Key}: \faStar\ Stars | \faCodeBranch\ Forks | \faList\ My Rank | \faPlusCircle\ My Contrs."
        out += BLANK

        out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z c c c c}
            \hline
            \textbf{Repo} & \textbf{Description} &  \faStar\ & \faCodeBranch\ & \faPlusCircle\ & \faList\ \\
            \hline
        """

        for repo in software_list.collaborative_repos[: software_list.max_repos_collab]:
            out += myformat(
                r"\href{<% url %>}{\bf <% name %>} & <% desc %> & <% stars %> & <% forks %> & <% contribs %> & <% rank %>/<% total %> \\",
                url=repo.url,
                name=repo.name.replace("_", r"\_"),
                desc=repo.description[:50] if repo.description else "",
                stars=f"{repo.stargazers:02d}",
                forks=f"{repo.forks:02d}",
                contribs=f"{repo.user_contributions:03d}",
                rank=f"{repo.user_rank:02d}",
                total=f"{repo.total_contributors:02d}",
            )

        out += r"""
        \hline
        \end{tabularx}
        \end{table}
        """
        out += BLANK

    return out
