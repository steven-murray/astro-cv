import contextlib
import datetime
from operator import itemgetter
from collections import defaultdict
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from cache_to_disk import cache_to_disk

import ads
from github import Github

import config as c

now = datetime.datetime.now()

import gspread

# Authorize access to the Google Sheet.
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

try:
    #credentials = ServiceAccountCredentials.from_json_keyfile_name("authorization_key.json", scope)
    gc = gspread.service_account(filename='authorization_key.json') 
    #gspread.authorize(credentials)

    print("Opening Activity Information from Google Sheets...")
    data = gc.open(c.GOOGLE_SHEET)
except Exception as e:
    print(e)
    HAVE_GOOGLE = False
    
BLANK = "\n\n" + r"\blankline" + "\n\n"
HLINE = "\n\n" + r"\hline" + "\n\n"

def section(func):
    section_title = func.__name__.replace("create_", "").replace("_", " ").title()

    def wrapper(*args, **kwargs):
        out = r"\section{%s}%%" % section_title
        out += '\n\t'
        print(f"Writing {section_title}...")
        _out = func(*args, **kwargs)
        _out = "\n\t".join(_out.split("\n"))
        out += _out
        out += '\n\n'
        return out

    return wrapper


def lol_to_lod(lol):
    """Converts a list-of-lists from gspread worksheet to a list of dictionaries.
    Assumes top row is a header"""
    return [{lol[0][i]: val for i, val in enumerate(lst)} for lst in lol[1:]]


def custom_format(string, brackets, *args, **kwargs):
    """
    Format strings like str.format(*args, **kwargs), except with brackets intead of {}.

    Copied from https://stackoverflow.com/a/40877821/1467820.
    """
    if len(brackets) != 2:
        raise ValueError(f'Expected two brackets. Got {len(brackets)}.')
    padded = string.replace('{', '{{').replace('}', '}}')
    substituted = padded.replace(brackets[0], '{').replace(brackets[1], '}')
    return substituted.format(*args, **kwargs)


def myformat(string, *args, escape_amp=True, **kwargs):
    # Any substitution should be text, and so "&" symbols must be escaped.
    if escape_amp:
        for i in range(len(args)):
            with contextlib.suppress(AttributeError):
                args[i] = args[i].replace("&", r"\&")
        for k in kwargs:
            with contextlib.suppress(AttributeError):
                kwargs[k] = kwargs[k].replace("&", r'\&')
    return custom_format(string, ["<% ", " %>"], *args, **kwargs)


@section
def create_contact_information(institution_url, department_name, institution_name,
                               institution_street, institution_location, institution_country,
                               phone_number, email, websites):
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
    for i, website in enumerate(websites):
        kind = website.get("kind", "")
        webid = website.get("id", "")

        if kind.lower() == "linkedin":
            icon = website.get("icon", r"\faLinkedinSquare~")
            url = website.get("url", f"https://www.linkedin.com/in/{webid}")
        elif kind.lower() == "github":
            icon = website.get("icon", r"\faGithub~")
            url = website.get("url", f"https://github.com/{webid}/")
        elif kind.lower() == "orcid":
            icon = website.get("icon", r"\faOrcid~")
            url = website.get("url", f"https://orcid.org/{webid}")
        elif kind.lower() == 'web':
            icon = website.get("icon", r"\faLaptop~")
            url = website.get('url')
        elif kind:
            icon = website.get("icon", r"\faLaptop~%s: "%kind)
            url = website.get("url")
        else:
            icon = website.get("icon", r"\faLaptop~: ")
            url = website.get("url")

        wb[kind] = r"\href{%s}{%s\verb|%s|}" % (url, icon, webid or url)

    ncols = max(len(websites), 3)
    websites=" \\".join(" & ".join(f"<% {k['kind']} %>" for k in ws[:ncols]) for ws in [websites[i:i+ncols] for i in range(0, len(websites), ncols)])
    
    out = myformat(
        contact_information,
        escape_amp=False,
        institution_url=institution_url,
        department_name=department_name,
        institution_name=institution_name,
        institution_street=institution_street,
        institution_location=institution_location,
        institution_country=institution_country,
        phone_number=phone_number,
        email=email,
        ncols="Y" * ncols,
        websites=websites,
    )


    out = myformat(
        out,
        **wb
    )

    return out

@section
def create_academic_references(references, maxref=None):
    # out = r"\begin{innerlist}"

    if maxref is None:
        maxref = len(references)

    out = r"\begin{tabular}{ l r }" + "\n"
    out += " \\\\ \n".join(
        myformat(
            r"\textbf{<% name %>} & \href{mailto:<% email %>}{<% email %>}",
            **entry
        )
        for entry in references[:maxref]
    )

    out += '\n'
    out += r"\end{tabular}"
    return out


@section
def create_research_interests(interests):
    out = ''

    for interest, sub_interests in interests.items():
        out += myformat(r"\textbf{<% interest %>}: <% sub %>.", interest=interest, sub = ", ".join(sub_interests))
        out += "\n\n"
    return out


@section
def create_education(keep_undergrad=True, keep_secondary=False, keep_undergrad_courses=False):
    out = r"""%
\href{http://www.uwa.edu.au}{\textbf{University of Western Australia}}, 
Perth, Western Australia
\begin{outerlist}

\item[] PhD, 
        \href{http://www.icrar.org}
             {Physics} 
        (2012--2015)
        \begin{innerlist}
        \item Thesis Title: Next-generation tools for next-generation surveys
        \item Supervisors: 
              \href{https://uwa.academia.edu/ChrisPower}
                   {Prof. Chris Power},
              \href{https://uwa.academia.edu/AaronRobotham}
                   {Dr. Aaron Robotham}
        \item Area of Study: Cosmology/Structure formation
        \item Courses Taken:
        \begin{itemize}
            \item General Relativity (HD)
            \item Computer Intensive Methods in Statistics (D) 
            \item Bayesian Astronomy in R
        \end{itemize}
        \end{innerlist}

\item[] Honours, 
        \href{http://www.physics.uwa.edu.au/}
             {Physics} (2011)
        \begin{innerlist}
        \item Graduated: First Class
        \item Thesis Topic: Large-Scale Structure in the SDSS and GAMA surveys
        \item Supervisor: Prof. John Hartnett
        \item Courses Taken:
        \begin{itemize}
            \item Differential Geometry (HD)
            \item Mathematical Methods (HD)
            \item Computational Quantum Mechanics (D)
            \item Astrophysics (D)
        \end{itemize}
        \end{innerlist}

\end{outerlist}

\blankline
"""

    if keep_undergrad:
        out += r"""
\href{http://uq.edu.au}{\textbf{University of Queensland}},
Brisbane, Queensland, Australia
\begin{outerlist}
\item[] Bachelor of Science in Mathematics (2007-2009)
        \begin{innerlist}
        \item Graduated: GPA of 6.583/7<% courses %>
    \end{innerlist}
\end{outerlist}

\blankline
"""
        courses = '\n' + r"\item Third-Year and Higher Courses Taken: Set Theory and Logic (D), " \
                         r"Bifurcation and Chaos (HD), Optimization Theory (HD), Complex Analysis " \
                         r"" \
                         r"(HD), Algebraic Methods of Methematical Physics (HD), Quantum Physics " \
                         r"(D), Astrophysics and Cosmology (HD), Statistical Mechanics (D)."
        out = myformat(out, courses=courses if keep_undergrad_courses else "")
    if keep_secondary:
        out += r"""
\href{http://www.mfac.edu.au/}{\textbf{Matthew Flinders Anglican College}}, 
Sunshine Coast, QLD, Australia
\begin{outerlist}

\item[] Secondary School (2002-2006)
    \begin{innerlist}
    \item Graduated with OP 1
    \item Subjects Taken (Marks scale E1-A10): Extension Mathematics C (A10), Mathematics B (
    A10), Chemistry (A8), Music (A8), Extension Music (A6), English (A4), Physics (A4).
    \end{innerlist}
\end{outerlist}
"""

    return out


@section
def create_professional_experience(jobs, min_rating, min_date):
    out = ""

    for job in jobs:
        if job['rating'] < min_rating:
            continue

        if job['dates'][-1] is not None and job['dates'][-1] < min_date:
            continue

        preformat = r"""%
        \textbf{<% organisation %>}, <% city %>, <% state %>

        <% title %>, (<% dates_ %>)
        
        \blankline
        
        """
        if len(job['dates']) == 2:
            dates_ = f"""{job['dates'][0]} -- {job['dates'][1] or ""}"""
        else:
            dates_ = str(job['dates'][0])
        out += myformat(preformat, dates_=dates_, **job)

    return out

@section
def create_academic_experience(omit_grants, omit_collaborations, omit_committees, omit_referees,
                               omit_lecturing,
                               omit_supervision, omit_teaching, omit_outreach, omit_prof_training,
                               omit_personal_training, omit_industry):
    def create_subcategory(cat, fmt_string, label=None, **extra_format_kwargs):
        X = lol_to_lod(data.worksheet(cat).get_all_values())

        if len(X) > 0:
            # Get the type of date defining this subcategory
            for date_id in ['Date', 'StartDate', "Year"]:
                if date_id in X[0]:
                    break

            out = myformat(r"\textbf{<% cat %>} \hfill \textbf{<% date %> -- Present}", cat=label or cat, date=min(x[date_id].split("/")[-1] for x in X))

            out += '\n'
            out += r"\begin{innerlist}"
            out += '\n'
            for x in sorted(X, key=lambda x: int(x[date_id].split("/")[-1]), reverse=True):

                for k, fnc in extra_format_kwargs.items():
                    x[k] = fnc(x)

                out += myformat(fmt_string, **x)
                out += '\n\n'

            out += r"\end{innerlist}"
            out += '\n\n'
            out += r"\blankline"
            out += '\n\n'

            return out
        else:
            return ""

    out = ""

    if not omit_grants:
        out += create_subcategory(
            "Grants",
            r"\item <% Authors %>\hfill<% Year %>\\ \textit{<% Title %>}, <% Grant %>\hfill<% award_amount %>",
            award_amount=lambda x: r"\textbf{\$%s}"%x['Amount'] if x['Amount'] else "" 
        )

    if not omit_collaborations:
        out += create_subcategory(
            "Collaborations",
            r"\item <% Group %> [CI <% CI %>], (<% StartDate %>~--~<% EndDate %>)")

    if not omit_committees:
        out += create_subcategory(
            "Memberships and Committees",
            r"\item <% Committee %> [<% Role %>], (<% start %>~--~<% end %>)",
            start=lambda x: x['StartDate'].split("/")[-1],
            end=lambda x: x['EndDate'].split("/")[-1])

    if not omit_referees:
        out += create_subcategory(
            "Journal Referee",
            r"\item Referee for <% Journal %> (<% StartDate %>~--~<% EndDate %>)")

    if not omit_lecturing:
        out += create_subcategory(
            "Lecturing",
            r"\item <% Number %> Lecture<% course %> <% Title %> (<% StartDate %>~--~<% EndDate "
            r"%>, <% University %>)",
            course=lambda x: ":" if x["Number"] == 1 else "Course:")

    if not omit_supervision:
        out += create_subcategory(
            "Supervision",
            r"\item <% cosup %> <% Level %> <% student %>: <% Name %> (<% StartDate %>~--~<% "
            r"EndDate %>)",
            cosup=lambda x: "Co-supervised" if x['Co-Supervised'] == "Yes" else "Supervised",
            student=lambda x: "student" if x['Level'] in ['PhD', "Masters", "Honours"] else "")

    if not omit_teaching:
        out += create_subcategory(
            "Teaching",
            r"\item <% Level %> `<% Name %>': \textit{<% Role %>} (<% University %>, <% StartDate "
            r"%>~--~<% EndDate %>)")

    if not omit_outreach:
        out += create_subcategory(
            "Outreach",
            r"\item <% activity %> (<% Location %>, <% date %>)",
            activity=lambda x: myformat(r"\href{<% URL %>}{<% Activity %>}", **x) if x['URL'] else
            x['Activity'],
            date=lambda x: x['Date'].split("/")[-1])

    if not omit_industry:
        out += create_subcategory(
            "IndustryEngagement",
            r"\item \textbf{<% Company %>:} <% Project %> (<% StartDate %>~--~<% EndDate %>). \textit{<% Description %>}",
            label="Industry and Inter-disciplinary Engagement",
        )

    if not omit_prof_training:
        out += create_subcategory(
            "Professional Training",
            r"\item <% Name %> (<% date %>)",
            date=lambda x: datetime.datetime.strptime(x['StartDate'], "%d/%m/%Y").strftime("%b %Y"))

    if not omit_personal_training:
        out += create_subcategory(
            "Personal Training",
            r"\item <% Name %> (<% date %>)",
            date=lambda x: datetime.datetime.strptime(x['Date'], "%d/%m/%Y").strftime("%b %Y"))

    return out


@section
def create_awards_and_scholarships(min_year, min_rating):
    awards = lol_to_lod(data.worksheet("Awards").get_all_values())

    if min_year:
        awards = [a for a in awards if int(a['DateReceived']) >= min_year]

    if min_rating:
        awards = [a for a in awards if int(a['Rating']) >= min_rating]

    # Try to segregate awards by institution.
    seg_awards = {}
    for a in awards:
        if a['Institution'] in seg_awards:
            seg_awards[a['Institution']].append(a)
        else:
            seg_awards[a['Institution']] = [a]

    seg_year = {
        k: max(a['DateReceived'] for a in v) for k, v in seg_awards.items()
    }

    sorted_segyear = sorted(seg_year.items(), key=itemgetter(1), reverse=True)

    out = ""
    for inst, year in sorted_segyear:
        out += myformat(r"\textbf{<% inst %>}", inst=inst)
        out += '\n\n'
        out += r"\begin{innerlist}"
        for award in seg_awards[inst]:
            out += myformat(r"\item <% Name %> (<% DateReceived %><% duration %>)", duration=f", for {award['Duration']}" if award['Duration'] else "", **award)

            out += '\n'
        out += r"\end{innerlist}"
        out += '\n\n'
        out += r'\blankline'
        out += '\n\n'
    return out


@section
def create_technical_skills():
    technical = lol_to_lod(data.worksheet("Technical").get_all_values())[0]
    out = ""

    def colonlist_to_sentence(str):
        return " and".join(str.replace(";", ',').rsplit(',', 1))

    if technical['OSProficient']:
        out += "Proficiency with %s operating systems." % colonlist_to_sentence(
            technical['OSProficient'])
        out += '\n'
        if not technical['OSUsed']:
            out += '\n\n'
            out += r'\blankline'
            out += '\n\n'

    if technical['OSUsed']:
        oses = colonlist_to_sentence(technical['OSUsed'])
        out += f"Working knowledge of {oses} operating systems"

        out += '\n\n'
        out += r'\blankline'
        out += '\n\n'

    if technical['LanguageProficient']:
        lanugages = colonlist_to_sentence(technical['LanguageProficient'])
        out += f"Intimate knowledge of a variety of programming languages, in particular {lanugages}"


        if technical["LanguageUsed"]:
            out += f", and to varying extents {colonlist_to_sentence(technical['LanguageUsed'])}."

            out += '\n\n'
            out += r'\blankline'
            out += '\n\n'
        else:
            out += "."

    elif technical['LanguageUsed']:
        out += "Basic knowledge of %s programming languages." % colonlist_to_sentence(
            technical['LanguageUsed'])
        out += '\n\n'
        out += r'\blankline'
        out += '\n\n'

    if technical['SoftwareProficient']:
        out += f"In-depth experience with {colonlist_to_sentence(technical['SoftwareProficient'])} programs and frameworks"


        if technical["SoftwareUsed"]:
            out += f", and to varying extents {colonlist_to_sentence(technical['SoftwareUsed'])}."

        else:
            out += "."
    elif technical['SoftwareUsed']:
        out += "Experience with %s programs and frameworks." % colonlist_to_sentence(
            technical['SoftwareUsed'])
    return out

@section
def create_software(max_repos, blacklist):
    # Authorize to access github repos
    print("    Collecting Software from Github...")
    gh = Github(c.GITHUB_PWD)

    transport = RequestsHTTPTransport(url='https://api.github.com/graphql', headers={'Authorization': f"token {c.GITHUB_PWD}"})

    client = Client(transport=transport)

    def get_contributions(org_id):
        query = gql(
            """
            query getContributions($org_id: ID!, $from: DateTime!){
                viewer{
                    contributionsCollection(from: $from, organizationID: $org_id) {
                        totalCommitContributions
                        totalIssueContributions
                        totalPullRequestContributions
                        totalPullRequestReviewContributions
                    }
                }
            }
            """
        )
        one_year_ago = now - datetime.timedelta(days=365)

        out = client.execute(query, variable_values={'org_id': org_id, "from": f'{one_year_ago.isoformat()}Z'})



        return out['viewer']['contributionsCollection']

    def get_orgs():
        query = gql(
            """
            {
              viewer{
                organizations(first: 20) {
                  nodes {
                    login
                    id
                    description
                  }
                }
              }
            }
            """
        )

        this = client.execute(query)
        return {
            node['login']: (node['id'], node['description'])
            for node in this['viewer']['organizations']['nodes'] if node['login'] not in c.BLACKLIST_ORGS
        }

    def get_repos(gh):
        return [gh.get_repo(name) for name in c.ORIGINAL_CODES]


    my_orgs = get_orgs()
    my_contributions = {}
    for org, (org_id, _) in my_orgs.items():
        if org in c.BLACKLIST_ORGS:
            continue
        my_contributions[org] = get_contributions(org_id)

    print(my_contributions)

    print(f"    Collected {len(my_orgs)} orgs.")

    org_totes = [(name, sum(o.values())) for name, o in my_contributions.items()]
    org_totes = [(name, tote) for name, tote in org_totes if tote >= c.MIN_CONTRIBUTIONS]
    org_totes = sorted(org_totes, key = lambda x: x[1], reverse=True)

    repos = get_repos(gh)

    print(f"    Collected {len(repos)} Repositories")

    def get_contributions(repo):
        rank = 0
        total_contributions = 0
        for i, user in enumerate(repo.get_contributors()):
            if user.login== c.GITHUB_USER:
                rank = i + 1
                contrib = user.contributions
            total_contributions +=user.contributions

        return rank, contrib, total_contributions

    repos = sorted(repos, key=lambda r: r.stargazers_count, reverse=True)
    contributions = [get_contributions(repo) for repo in repos]


    out = ''
    out += r"Complete information at \href{https://github.com/%s?tab=repositories}{github.com/%s}. " % (
        c.GITHUB_USER, c.GITHUB_USER)

    out += BLANK

    out += r"\textbf{Organizations}"
    out += BLANK
    out += r"""
    Most of my software development occurs within teams, which are listed here (only organizations in which I’ve                                 
    been active in the last year and are a ​member are listed). Each column gives the total                                       
    number of my contributions made to the organization, and then shows the relative contribution (percentage)                                 
    of the contributions in the form of \textbf{C}ommits​, \textbf{​P}Rs, \textbf{I}ssues​ and​ \textbf{R}eviews​.
    """
    out += BLANK

    out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z r} 
            \hline
            \textbf{Github Org} & \textbf{Description} & \textbf{Contr.} [C|P|I|R] \\
            \hline
    """

    for org, tote in org_totes:
        out += myformat(
            r"\href{https://github.com/<% org %>}{<% org %>} & <% descr %> & \texttt{<% tote %> [<% totalCommitContributions:03d %>|<% totalIssueContributions:02d %>|<% totalPullRequestContributions:02d %>|<% totalPullRequestReviewContributions:02d %>]} \\",
            org = org, tote=tote, descr=my_orgs[org][1], **my_contributions[org]
        )

    out += r"""
        \hline
        \end{tabularx}
        \end{table}
    """

    out += "\n\n"
    out += r'\textbf{Original Codes}'
    out += BLANK
    out += r"""
    Here I list notable codes that I originally authored and maintain. Much of my 
    current development work occurs in collaborative software, which is listed below.
    
    \textbf{Key}: \faStar\ GH Stars | \faCodeBranch\ Forks
    """

    out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z c c} 
            \hline
            \textbf{Repo} & \textbf{Description} &  \faStar\ & \faCodeBranch\ \\
            \hline
    """

    for i, repo in enumerate(repos[:max_repos]):
        out += myformat(
            r"\href{<% url %>}{\bf <% name %>} & <% descr %>  & <% stargazers %> & <% nforks %> \\ ",
            url=repo.html_url, name='/'.join(repo.html_url.split('/')[-2:]), 
            descr=repo.description, nforks=f"{repo.forks_count:02d}",
            stargazers=f"{repo.stargazers_count:02d}",
        )

    out += r"""
        \hline
        \end{tabularx}
        \end{table}
    """




    repos = get_all_my_repos()

    out += '\n'
    out += r'\textbf{Collaborative Codes}'
    out += BLANK
    out += r"""
    Here I list notable codes that I contribute to collaboratively. They are listed in
    descending order of my total number of contributions.
    
    \textbf{Key}:  \faStar\ GH Stars | \faCodeBranch\ Forks | \faList\ My Rank as Contributor | \faPlusCircle\ My Contributions
    """

    out += r"""
        \begin{table}[H]
        \small
            \begin{tabularx}{\textwidth}{l Z c c c c} 
            \hline
            \textbf{Repo} & \textbf{Description} &  \faStar\ & \faCodeBranch\ & \faPlusCircle\ & \faList\ \\
            \hline
    """

    for name, data in repos[:c.MAX_REPOS_COLLAB]:
        repo = data['repo']
        out += myformat(
            r"\href{<% url %>}{\bf <% name %>} & <% descr %>  & <% stargazers %> & <% nforks %> & <% contribs %> (<% contribs_percent:d %>\%) & <% rank %>/<% ncontribs %>\\ ",
            url=repo.html_url,# name=('/'.join(repo.html_url.split('/')[-2:])).replace('_', r'\_'),
            name=repo.name.replace('_', r'\_'),
            descr=repo.description, nforks=repo.forks_count,
            stargazers=repo.stargazers_count,
            contribs=data['contributions'],
            contribs_percent=int(data['contrib_percent']),
            rank=data['rank'],
            ncontribs = data['ncontribs']
        )

    out += r"""
        \hline
        \end{tabularx}
        \end{table}
    """



    return out


@cache_to_disk(3)
def get_all_my_repos():
    gh = Github(c.GITHUB_PWD)
    all_repos = gh.get_user().get_repos()
    out_repos = {}
    for repo in all_repos:
        if any(repo.name in name for name in c.ORIGINAL_CODES):
            continue

        contribs = list(repo.get_contributors())
        total_contribs = 0
        for i, contrib in enumerate(contribs):
            if contrib.login == c.GITHUB_USER:
                out_repos[repo.html_url] = {'contributions': contrib.contributions, 'rank':i+1, 'repo': repo}
            total_contribs += contrib.contributions

        if repo.html_url not in out_repos:
            continue

        out_repos[repo.html_url]['contrib_percent'] = 100*(out_repos[repo.html_url]['contributions'] / total_contribs)
        out_repos[repo.html_url]['ncontribs'] = len(contribs)

    return sorted(out_repos.items(), key= lambda x: x[1]['contributions'], reverse=True)
    
@section
def create_publications(library, surname, students):
    url = fr"https://ui.adsabs.harvard.edu/public-libraries/{library}"

    out = ""
    if c.USE_LINKS:
        out += myformat(
            r"To see a configurable list of all my publications, see \href{<% url %>}{my ADS list}. "
            r"Information correct as of <% today %>. Any arxiv e-prints displayed have been accepted. "
            r"Papers in each category listed in reverse chronological order. Papers with more than <% cites %>"
            r" citations per year highlighted in {\color{Orange} orange}.",
            url=url, today=now.strftime("%d %b %Y"), cites=c.HIGHLIGHT_CITE_PER_YEAR
        )
    else:
        out += myformat(
            r"To see a configurable list of all my publications, see my ADS list\footnote{\url{<% url %>}}. "
            r"Information correct as of <% today %>. Any arxiv e-prints displayed have been accepted."
            r"Papers in each category listed in reverse chronological order. Papers with more than <% cites %>"
            r" citations per year highlighted in {\color{Orange} orange}.",
            url=url, today=now.strftime("%d %b %Y"), cites=c.HIGHLIGHT_CITE_PER_YEAR
        )
    out += BLANK

    # Get all my papers
    print("    Collecting Publications from ADS...")
    fields = ['bibcode', 'doctype', 'citation_count', 'title', 'author', 'year', 'pub', 'volume',
              'page', 'read_count', "doi"]
    papers = list(ads.SearchQuery(q=f"docs(library/{library})", fl=fields, max_pages=100))
    print(f"    Collected {len(papers)} papers")

    # Separate out proposals/conference proceedings
    confproc = [p for p in papers if p.doctype == "inproceedings"]
#    papers = [p for p in papers if p.doctype == 'article' or (p.doctype == 'eprint' and p.bibcode in c.ACCEPTED)]

    # Weed out duplicates
    papers_ = []
    for p in papers:
        if p in papers_:
            print(f"    Duplicate: {p.title[0]} [{p.bibcode}]")
            continue
        if p.doctype != 'article':
            if p.doctype == 'eprint' and p.bibcode not in c.ACCEPTED:
                print(f"    Not Accepted:  {p.title[0]} [{p.bibcode}]")
                continue
            elif p.doctype != 'eprint':
                print(f"    Not An Article: {p.title[0]} [{p.bibcode}]")
                continue

        papers_.append(p)

    papers = papers_

    print(
        f"    Pruned to {len(papers)} papers after de-duplication and removal of "
        f"conference proceedings/proposals (n={len(confproc)})"
    )

    mq = ads.MetricsQuery(bibcodes=[p.bibcode for p in papers])
    metrics = mq.execute()

    # Get total metrics
    citation_counts = [p.citation_count for p in papers]
    ordered_cites = sorted(citation_counts, reverse=True)

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
        tot_cite=metrics['citation stats']['total number of citations'], 
        norm_papers = metrics['basic stats']['normalized paper count'],
        tot_norm_cite=metrics['citation stats']['normalized number of citations'], 
        h_index=metrics['indicators']['h'], 
        m_index=metrics['indicators']['m'],
        g_index=metrics['indicators']['g'],
        tori_index=metrics['indicators']['tori'],
        i10_index=metrics['indicators']['i10'],
        i100_index=metrics['indicators']['i100']
    )
    out += BLANK

    # Sort papers in descending "importance"
    papers = sorted(papers,
                    key=lambda p: p.year,
                    # lambda p: (p.citation_count +0.05*p.read_count)/ (0.01 + float(now.year) -
                    # float(p.year))/(1 +author_number(p)),
                    reverse=True)

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
        auth = paper.author
        for i, a in enumerate(auth):
            if surname in a:
                auth[i] = r'\textbf{' + a + "}"

        if len(paper.author) > 4:
            authors = ", ".join(auth[:3]) + " et. al."
        else:
            authors = ", ".join(auth)

        journal = journal_abbrev.get(paper.pub, paper.pub)
        if journal:
            journal += ","

        out = myformat(r"\item <% authors %> (<% year %>), \textit{<% title %>}, \href{<% url %>}{\color{" r"lightblue}{<% journal %> <% volume %> <% page %>}} \hfill ", title=paper.title[0], authors=authors, year=paper.year, journal=journal, volume=f"{paper.volume}," if paper.volume is not None else "", page=paper.page[0] if paper.page else '', url=paper.doi)


        if paper.citation_count / max(now.year - int(paper.year) , 1) >= c.HIGHLIGHT_CITE_PER_YEAR:
            rest = r"{\color{Orange} \faPen~<% citation_count %>~~\faEye~<% read_count %>}"
        else:   
            rest = r"\faPen~<% citation_count %>~~\faEye~<% read_count %>"

        rest = myformat(rest, citation_count=f'{paper.citation_count:>3}', read_count=f'{paper.read_count:>3}',)
        return out + rest

    # First do first-author papers
    def write_subset(papers, label, condition, resume=True):
        these, indx = zip(*[(p, i) for i, p in enumerate(papers) if condition(p)])
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
                label=label, cites=cite_count, reads=read_count, npapers=len(these)
            )
            out += r"\begin{enumerate}[itemsep=1pt%s]"%(',resume' if resume else '')

            for paper in these:
                out += write_paper(paper)

#            out += r"\setcounter{itemc}{\value{enumi}}"
            out += r"\end{enumerate}"

        print(f"\t{label}:\n\t\t", end='')
        print("\n\t\t".join([p.title[0] for p in these]))
        return out, papers

    # First author
    _out, papers = write_subset(
        papers, "First author papers", lambda p: surname in p.author[0], resume=False
    )
    out += _out

    def author_number(p):
        for i, auth in enumerate(p.author):
            if auth.startswith(surname):
                break
        return i + 1

    def is_important_author(surname, paper, verbose=False):
        """
        Check if this paper is one that you're an important author of, other than first author.
        """
        if verbose:
            print(f"      {paper.title[0]}")

        # Can't be first author
        if paper.author[0].startswith(surname):
            if verbose: print("       is a first author")
            return False

        # If you're top-4 you're always important
        if author_number(paper) <= c.TOP_N:
            if verbose: print(f"       is a top-{c.TOP_N} author paper")
            return True

        # If there's less than 12 authors, and you're not top 4, you're not important.
        if len(paper.author) < c.ALPHABET_N:
            if verbose: print(
                f"       is a small-group paper where you're not in the top {c.TOP_N}")
            return False

        # Otherwise, you're important if it's got an alphabetical order list and you're before it.
        for i in range(1, len(paper.author) - 1):
            if paper.author[-(i + 1)].split(",")[0].split(" ")[-1] > \
                    paper.author[-i].split(",")[0].split(" ")[-1]:
                break

        if i < c.ALPHABET_N:
            # Not an alphabetical list at the end
            if verbose: print(
                "       is a large-collab paper with no alphabetical listing, where you're not "
                "top 4")
            return False
        if author_number(paper) > len(paper.author) - i:
            # My name is part of the alphabetical list
            if verbose: print(
                "       is a large-collab paper where you're in the alphabetical section of "
                "authors")
            return False

        if verbose: print("       is a large-collab paper where you are before the alphabetical ")
        return True

    # Student's papers
    _out, papers = write_subset(papers, "Supervised papers by my students", lambda p: any(pp in p.author[0] for pp in students))
    out += _out
    
    # "Important" author
    _out, papers = write_subset(papers, "Papers with significant contribution to analysis",
                                lambda p: is_important_author(surname, p))
    out += _out

    # All other papers
    _out, papers = write_subset(papers, "Collaboration papers (contr. to analysis and/or writing)", lambda p: True)
    out += _out

    if confproc:
        out += write_subset(confproc, "Conference proceedings", lambda p: True)[0]

    return out


@section
def create_press_releases():
    return ""


@section
def create_presentations(write_posters, write_local_talks):
    presentations = lol_to_lod(data.worksheet("Conferences").get_all_values())
    out = ""

    def write_talks(talk_list):
        out = r"\begin{enumerate}"
        for talk in sorted(talk_list, key=lambda x: int(x['StartDate'].strip("/")[-1]),
                           reverse=True):
            date = datetime.datetime.strptime(talk['StartDate'], "%d/%m/%Y")
            out += myformat(
                r"\item ``<% title %>'' at <% Name %>, <% City %>, <% Country %> (<% date %>) <% "
                r"prize %>",
                date=date.strftime("%b %Y"),
                title=myformat(r"\href{<% URL %>}{<% Title %>}", **talk) if talk['URL'] else talk[
                    'Title'],
                prize=r"[\textbf{Prize for %s}]" % (talk['Awards'].replace(";", " and")) if talk[
                    'Awards'] else "",
                **talk)
            out += '\n'
        out += r"\end{enumerate}"
        out += BLANK
        return out

    # Get Invited Talks
    invited = [p for p in presentations if p['Invited Speaker?'] == "Yes"]
    if invited:
        out += r"\textbf{Invited Talks}"
        out += HLINE
        out += write_talks(invited)

    seminars = lol_to_lod(data.worksheet("Seminars").get_all_values())
    out += r"\textbf{Seminars}"
    out += HLINE
    out += r"\begin{enumerate}"
    for talk in sorted(seminars, key=lambda x: int(x['Date'].strip("/")[-1]), reverse=True):
        date = datetime.datetime.strptime(talk['Date'], "%d/%m/%Y")
        out += myformat(
            r"\item ``<% title %>'', <% Location %> (<% Date %>) ",
            date=date.strftime("%b %Y"),
            title=myformat(r"\href{<% TalkURL %>}{<% TalkTitle %>}", **talk) if talk['TalkURL'] else talk['TalkTitle'],
            **talk)
        out += '\n'
    out += r"\end{enumerate}"
    out += BLANK

    # Get Contributed Talks
    contributed = [p for p in presentations if
                   p['Invited Speaker?'] == "No" and p["Type of contribution"] == "Talk"]
    if contributed:
        out += r"\textbf{Contributed Talks}"
        out += HLINE
        out += write_talks(contributed)

    # Get posters
    if write_posters:
        posters = [p for p in presentations if p['Type of contribution'] == "Poster"]
        if posters:
            out += r"\textbf{Posters}"
            out += write_talks(posters)

    # Do local presentations
    if write_local_talks:
        local_talks = lol_to_lod(data.worksheet("Other Presentations").get_all_values())

        def write_local(local_talks, kind):
            out = r"\noindent\textbf{%s %ss}"%("Local" if kind!="Tutorial" else "", kind)
            out += HLINE
            out += r"\begin{enumerate}"
            for talk in local_talks:
                url = talk['VideoURL']
                if not url:
                    url = talk['TalkURL']

                if talk['TalkURL'] or talk['VideoURL']:
                    out += myformat(
                        r"\item ``\href{<% url %>}{<% Title %>}'' at <% Name %>, <% Location %> (<% "
                        r"Date %>)",
                        url=url,
                        **talk
                    )
                else:
                    out += myformat(r"\item ``<% Title %>'' at <% Name %>, <% Location %> (<% Date %>)",
                                    **talk)
                out += '\n'
            out += r"\end{enumerate}"
            out += BLANK

            return out

        kinds = {talk['Kind'] for talk in local_talks}
        for kind in kinds:
            out += write_local([talk for talk in local_talks if talk['Kind'] == kind], kind)

    return out
