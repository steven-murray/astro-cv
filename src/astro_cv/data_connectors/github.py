"""GitHub API data connector for software section."""

from datetime import datetime, timedelta
from typing import Optional, Any
from pathlib import Path
from rich.progress import Progress

import attrs
from github import Github
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import logging
from cache_to_disk import cache_to_disk
from astro_cv.sections.software import SoftwareList
from astro_cv.sections.software.datatype import Organization, Repository


logger = logging.getLogger(__name__)


@cache_to_disk(n_days_to_cache=3)
def _filter_repos(
    user, blacklist, min_contributions, github_user
) -> list[tuple[str, dict]]:
    all_repos = sorted(user.get_repos(visibility="public"), key=lambda r: r.full_name)

    out_repos = {}
    with Progress() as progress:
        task = progress.add_task("Processing repositories...", total=len(all_repos))

        for repo in all_repos:
            progress.update(
                task, advance=1, description=f"Processing {repo.full_name}..."
            )

            # Skip original codes
            if any(repo.name in name for name in blacklist):
                continue

            try:
                contribs = list(repo.get_contributors())
                total_contribs = 0
                user_rank = None
                user_contribs = None

                for i, contrib in enumerate(contribs):
                    if contrib.login == github_user:
                        user_rank = i + 1
                        user_contribs = contrib.contributions
                    total_contribs += contrib.contributions

                # Only include if user is a contributor with minimum contributions
                if user_rank is None or user_contribs is None:
                    continue

                if user_contribs < min_contributions:
                    continue

                out_repos[repo.html_url] = {
                    "repo": repo,
                    "contributions": user_contribs,
                    "rank": user_rank,
                    "ncontribs": len(contribs),
                    "contrib_percent": 100 * (user_contribs / total_contribs)
                    if total_contribs > 0
                    else 0,
                }
            except Exception as e:
                logger.warning(f"Could not process {repo.name}: {e}")

    # Sort by contributions descending
    sorted_repos = sorted(
        out_repos.items(), key=lambda x: x[1]["contributions"], reverse=True
    )

    return sorted_repos


class DataConnector:
    """Connect to GitHub API and retrieve repository and contribution data."""

    def __init__(
        self,
        github_token: str,
        github_user: str,
    ):
        """Initialize GitHub connector.

        Parameters
        ----------
        github_token : str
            GitHub personal access token for API authentication.
        github_user : str
            GitHub username.
        """
        self.github_token = github_token
        self.github_user = github_user

        # Initialize REST client
        self.gh = Github(github_token)

        # Initialize GraphQL client
        self.transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"token {github_token}"},
        )
        self.graphql_client = Client(transport=self.transport, execute_timeout=30)

    def get_organizations(self, blacklist: Optional[list[str]] = None) -> dict:
        """Get organizations that the user is a member of.

        Parameters
        ----------
        blacklist : list[str], optional
            List of organization names to exclude.

        Returns
        -------
        dict
            Dictionary mapping organization name to (id, description) tuple.
        """
        logger.info("Fetching organizations from GitHub...")

        blacklist = blacklist or []
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

        result = self.graphql_client.execute(query)
        orgs = {
            node["login"]: (node["id"], node["description"])
            for node in result["viewer"]["organizations"]["nodes"]
            if node["login"] not in blacklist
        }

        logger.info(f"Retrieved {len(orgs)} organizations")

        return orgs

    def get_contributions(self, org_id: str) -> dict:
        """Get user's contributions to an organization in the last year.

        Parameters
        ----------
        org_id : str
            Organization GraphQL ID.

        Returns
        -------
        dict
            Dictionary with contribution counts:
            - totalCommitContributions
            - totalIssueContributions
            - totalPullRequestContributions
            - totalPullRequestReviewContributions
        """
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

        one_year_ago = datetime.now() - timedelta(days=365)
        result = self.graphql_client.execute(
            query,
            variable_values={"org_id": org_id, "from": f"{one_year_ago.isoformat()}Z"},
        )

        return result["viewer"]["contributionsCollection"]

    def get_original_repos(self, repo_names: list[str]) -> list:
        """Get repository objects for original code repositories.

        Parameters
        ----------
        repo_names : list[str]
            List of repository names in format "owner/repo".

        Returns
        -------
        list
            List of PyGithub Repository objects.
        """
        logger.info(f"Fetching {len(repo_names)} original repositories...")

        repos = []
        for repo_name in repo_names:
            try:
                repo = self.gh.get_repo(repo_name)
                repos.append(repo)
            except Exception as e:
                logger.warning(f"Could not fetch {repo_name}: {e}")

        return sorted(repos, key=lambda r: r.stargazers_count, reverse=True)

    def get_collaborative_repos(
        self, min_contributions: int = 1, blacklist: Optional[list[str]] = None
    ) -> list:
        """Get all repositories the user contributes to.

        This is cached to disk since it requires fetching many repositories.

        Parameters
        ----------
        min_contributions : int
            Minimum number of contributions to include a repository.
        blacklist : list[str], optional
            List of original code repos to exclude.

        Returns
        -------
        list
            List of dicts with keys: repo, contributions, rank, ncontribs, contrib_percent
            (sorted by contribution count descending).
        """
        logger.info("Fetching collaborative repositories...")

        blacklist = blacklist or []
        user = self.gh.get_user()
        sorted_repos = _filter_repos(
            user,
            blacklist=blacklist,
            min_contributions=min_contributions,
            github_user=self.github_user,
        )

        logger.info(f"Retrieved {len(sorted_repos)} collaborative repositories")

        return [data for _, data in sorted_repos]

    def get(self, section_name: str, config_path: Path | str) -> Any:
        """Generic method to get section data from GitHub.

        Parameters
        ----------
        section_name : str
            Name of the section (should be 'software').
        config_path : Path or str
            Path to the section's TOML configuration file.

        Returns
        -------
        SoftwareList
            Populated software list with repositories from GitHub.

        Raises
        ------
        ValueError
            If the section_name is not 'software'.
        """
        config_path = Path(config_path)
        section_key = section_name.replace("-", "_")

        if section_key != "software":
            raise ValueError(
                f"DataConnector (github) does not support '{section_name}'. "
                f"Only 'software' is supported."
            )

        # Load settings from TOML file
        software_list = SoftwareList.read_toml(config_path)

        # Fetch organizations with contribution data
        org_map = self.get_organizations(blacklist=software_list.blacklist_orgs)
        organizations = []
        for org_name, (org_id, description) in org_map.items():
            # Get contribution data for this organization
            contrib_data = self.get_contributions(org_id)
            org = Organization(
                login=org_name,
                description=description or "",
                total_commits=contrib_data.get("totalCommitContributions", 0),
                total_issues=contrib_data.get("totalIssueContributions", 0),
                total_prs=contrib_data.get("totalPullRequestContributions", 0),
                total_reviews=contrib_data.get(
                    "totalPullRequestReviewContributions", 0
                ),
            )
            organizations.append(org)

        original_repos = [
            Repository(
                name=repo.name,
                url=repo.html_url,
                description=repo.description or "",
                stargazers=repo.stargazers_count,
                forks=repo.forks_count,
            )
            for repo in self.get_original_repos(software_list.original_codes)[
                : software_list.max_repos
            ]
        ]

        collab_repo_dicts = self.get_collaborative_repos(
            min_contributions=software_list.min_contributions,
            blacklist=software_list.blacklist_repos,
        )[: software_list.max_repos_collab]

        collab_repos = [
            Repository(
                name=repo_dict["repo"].name,
                url=repo_dict["repo"].html_url,
                description=repo_dict["repo"].description or "",
                stargazers=repo_dict["repo"].stargazers_count,
                forks=repo_dict["repo"].forks_count,
                user_contributions=repo_dict["contributions"],
                user_rank=repo_dict["rank"],
                total_contributors=repo_dict["ncontribs"],
            )
            for repo_dict in collab_repo_dicts
        ]

        # Create a new SoftwareList with populated data using evolve
        return attrs.evolve(
            software_list,
            organizations=organizations,
            original_repos=original_repos,
            collaborative_repos=collab_repos[: software_list.max_repos_collab],
        )
