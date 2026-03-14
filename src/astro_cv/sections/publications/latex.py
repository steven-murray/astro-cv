"""LaTeX generation for publications section."""

from datetime import datetime

import ads

from astro_cv.formats.latex import myformat

now = datetime.now()
BLANK = "\n\n"


def create(pub_list):
    """Generate LaTeX for publications section using PublicationList data."""
    url = rf"https://ui.adsabs.harvard.edu/public-libraries/{pub_list.library}"

    out = ""
    out += myformat(
        r"To see a configurable list of all my publications, see \href{<% url %>}{my ADS list}. "
        r"Information correct as of <% today %>. Any arxiv e-prints displayed have been accepted. "
        r"Papers in each category listed in reverse chronological order. Papers with more than <% cites %>"
        r" citations per year highlighted in {\color{Orange} orange}.",
        url=url,
        today=now.strftime("%d %b %Y"),
        cites=pub_list.highlight_cite_per_year,
    )
    out += BLANK

    # Filter papers by doctype
    papers = []
    confproc = []
    for p in pub_list.publications:
        if p.doctype == "inproceedings":
            confproc.append(p)
        elif p.doctype == "article" or (
            p.doctype == "eprint" and p.bibcode in pub_list.accepted
        ):
            papers.append(p)

    # Get metrics from ADS
    if papers:
        mq = ads.MetricsQuery(bibcodes=[p.bibcode for p in papers])
        metrics = mq.execute()

        out += r"\textbf{At a Glance}"
        out += BLANK
        out += myformat(
            r"""
        \begin{table}[h!]
            \begin{tabular}{l l l l}
            \hline
            \textbf{Total Papers} & <% tot_papers %> & \textbf{M-index} & <% m_index:.1f %> \\
            \textbf{Normalized Papers} & <% norm_papers:.1f %> & \textbf{G-index} & <% g_index %> \\
            \textbf{Total Citations} & <% tot_cite %> & \textbf{I10-index} & <% i10_index %> \\
            \textbf{Total Norm. Citations} & <% tot_norm_cite:.1f %> & \textbf{I100-index} & <% i100_index %> \\
            \textbf{H-index} &  <% h_index %> & \textbf{Tori-index} & <% tori_index:.1f %>\\
            \hline
        \end{tabular}
        \end{table}
        """,
            tot_papers=len(papers),
            tot_cite=metrics["citation stats"]["total number of citations"],
            norm_papers=metrics["basic stats"]["normalized paper count"],
            tot_norm_cite=metrics["citation stats"]["normalized number of citations"],
            h_index=metrics["indicators"]["h"],
            m_index=metrics["indicators"]["m"],
            g_index=metrics["indicators"]["g"],
            tori_index=metrics["indicators"]["tori"],
            i10_index=metrics["indicators"]["i10"],
            i100_index=metrics["indicators"]["i100"],
        )
        out += BLANK

    # Sort papers by year (reverse chronological)
    papers = sorted(papers, key=lambda p: p.year, reverse=True)

    journal_abbrev = {
        "Monthly Notices of the Royal Astronomical Society": "MNRAS",
        "Monthly Notices of the Royal Astronomical Society Letters": "MNRASL",
        "The Astrophysical Journal": "ApJ",
        "The Astrophysical Journal Letters": "ApJL",
        "Publications of the Astronomical Society of Australia": "PASA",
        "Astronomy and Computing": r"A&C",
        "ArXiv e-prints": "",
        "The Journal of Open Source Software": "JOSS",
    }

    out += r"Key: \faFile*~\ Papers, \faPen\ Citations, \faEye\ Reads (on NASA ADS)"
    out += BLANK

    def write_paper(paper):
        """Format a single paper entry."""
        auth = list(paper.authors)
        for i, a in enumerate(auth):
            if pub_list.surname in a:
                auth[i] = r"\textbf{" + a + "}"

        if len(paper.authors) > 4:
            authors = ", ".join(auth[:3]) + " et. al."
        else:
            authors = ", ".join(auth)

        journal = journal_abbrev.get(paper.pub, paper.pub)
        if journal:
            journal += ","

        out = myformat(
            r"\item <% authors %> (<% year %>), \textit{<% title %>}, \href{<% url %>}{\color{"
            r"lightblue}{<% journal %> <% volume %> <% page %>}} \hfill ",
            title=paper.title[0]
            if isinstance(paper.title, (list, tuple))
            else paper.title,
            authors=authors,
            year=paper.year,
            journal=journal,
            volume=f"{paper.volume}," if paper.volume is not None else "",
            page=paper.page[0]
            if isinstance(paper.page, (list, tuple)) and paper.page
            else (paper.page if paper.page else ""),
            url=paper.doi,
        )

        if paper.citations_per_year >= pub_list.highlight_cite_per_year:
            rest = (
                r"{\color{Orange} \faPen~<% citation_count %>~~\faEye~<% read_count %>}"
            )
        else:
            rest = r"\faPen~<% citation_count %>~~\faEye~<% read_count %>"

        rest = myformat(
            rest,
            citation_count=f"{paper.citation_count:>3}",
            read_count=f"{paper.read_count:>3}",
        )
        return out + rest

    def author_number(p):
        """Get the author number (1-indexed position) of surname in paper."""
        for i, auth in enumerate(p.authors):
            if auth.startswith(pub_list.surname):
                break
        return i + 1

    def is_important_author(paper):
        """
        Check if this paper is one that you're an important author of, other than first author.
        """
        # Can't be first author
        if paper.authors[0].startswith(pub_list.surname):
            return False

        # If you're top-N you're always important
        if author_number(paper) <= pub_list.top_n:
            return True

        # If there's less than alphabet_n authors, and you're not top N, you're not important.
        if len(paper.authors) < pub_list.alphabet_n:
            return False

        # Otherwise, you're important if it's got an alphabetical order list and you're before it.
        for i in range(1, len(paper.authors) - 1):
            if (
                paper.authors[-(i + 1)].split(",")[0].split(" ")[-1]
                > paper.authors[-i].split(",")[0].split(" ")[-1]
            ):
                break

        if i < pub_list.alphabet_n:
            # Not an alphabetical list at the end
            return False
        if author_number(paper) > len(paper.authors) - i:
            # My name is part of the alphabetical list
            return False

        return True

    def write_subset(papers, label, condition, resume=True):
        """Write a subset of papers matching a condition."""
        these = [p for p in papers if condition(p)]
        papers = [p for p in papers if not condition(p)]

        out = BLANK if resume else ""
        if these:
            cite_count = sum(p.citation_count for p in these)
            read_count = sum(p.read_count for p in these)

            out += myformat(
                r"""
                \textbf{<% label %>} \hfill \faFile*~<% npapers %>\ \ \faPen~<% cites %>\ \ \faEye~<% reads %>
                \hline
                """,
                label=label,
                cites=cite_count,
                reads=read_count,
                npapers=len(these),
            )
            out += r"\begin{enumerate}[itemsep=1pt%s]" % (",resume" if resume else "")

            for paper in these:
                out += write_paper(paper)

            out += r"\end{enumerate}"

        return out, papers

    # First author
    _out, papers = write_subset(
        papers,
        "First author papers",
        lambda p: pub_list.surname in p.authors[0],
        resume=False,
    )
    out += _out

    # Student's papers
    _out, papers = write_subset(
        papers,
        "Supervised papers by my students",
        lambda p: any(pp in p.authors[0] for pp in pub_list.students),
    )
    out += _out

    # "Important" author
    _out, papers = write_subset(
        papers,
        "Papers with significant contribution to analysis",
        is_important_author,
    )
    out += _out

    # All other papers
    _out, papers = write_subset(
        papers,
        "Collaboration papers (contr. to analysis and/or writing)",
        lambda p: True,
    )
    out += _out

    # Conference proceedings if enabled
    if pub_list.do_proceedings and confproc:
        _out, _ = write_subset(confproc, "Conference proceedings", lambda p: True)
        out += _out

    return out
