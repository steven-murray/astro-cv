GH = "token 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"

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(url='https://api.github.com/graphql', headers={'Authorization': GH})
client = Client(transport=transport)

def get_contributions(org_id):
    query = gql(
        """
        query getContributions($org_id: ID!){
        viewer{
        contributionsCollection(from: "2020-10-01T00:00:00Z", organizationID: $org_id) {
        totalCommitContributions
        totalIssueContributions
        totalPullRequestContributions
        totalPullRequestReviewContributions
        }
        organizations(first: 10) {
        nodes {
        login
        id
        }
        }
        }
        }
        """
    )

    out = client.execute(query, variable_values={'org_id': org_id})
    return out
def get_orgs():
    query = gql(
        """
        {
        viewer{
          organizations(first: 20) {
            nodes {
              login
              id
            }
          }
        }

        }
        """
    )

    this = client.execute(query)
    out = {}
    for node in this['viewer']['organizations']['nodes']:
        out[node['login']] = node['id']

    return out

orgs = get_orgs()

contribs = {}
for org, id in orgs.items():
    contribs[org] = get_contributions(id)

print(orgs)
print(contribs)

