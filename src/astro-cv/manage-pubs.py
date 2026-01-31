"""
Super simple script for printing out all the publications that you've written.

To setup for calling the script, you must install the ads package from the following fork:
`pip install git+git://github.com/steven-murray/ads` and
the `questionary` and `pyyaml` packages (`pip install questionary pyyaml`).
You also must create an ADS API key (go to your settings page on ADS) and save it in
`~/.ads/dev_key`.

Call simply as `astro-cv manage-pubs` and it will print out the results in HTML format
to stdout.

What happens under the hood is that it will perform an automatic search based on LoCo
members' names and affiliation, then it will compare that list to a library we maintain.
Anything new, and you will be prompted to add them to the library. Anything you decide NOT
to add to the library will be flagged as a false positive and added to a library of such, so
as never to come up again.
In the end, it will only print out docs in the library itself.
Use `--help` to get options.
New LoCo members should add their names to the `locos` list below. 
"""

# TODO: ability to add orcid

import ads
from datetime import datetime
import questionary as qs
from ads.libraries import Library
from pathlib import Path
import yaml

now = datetime.now()


def main(config: Path):
    """Main entry point for managing publications."""
def main(config: Path):
    """Main entry point for managing publications."""
    
    with open(config, 'r') as fl:
        cfg = yaml.safe_load(fl)


    affiliations = ['"' + aff + '"' for aff in cfg['affiliations']]


library = Library(cfg['library'])
false_lib = Library(cfg['false_lib'])

year = f"year:{cfg['started']}-{now.year}"
name = cfg['name']
affiliation_q = " OR ".join(affiliations)
orcid = cfg['orcid']

# Build up a query
q = f'(author:"{name}" aff:({affiliation_q}) {year}) OR orcid:{orcid} NOT docs(library/{false_lib.id})'

print(f"Performing following query:\n  > {q}")

papers = list(ads.SearchQuery(
    q=q,
    sort='date desc',
    max_pages=100,
    fl=['author', 'title', 'bibcode', 'pub', 'volume', 'issue', 'page', 'year', 'orcid_pub', 'aff']
))
n = len(papers)


# This shouldn't need to be done, but just in case...
falsebibs = [
    p.bibcode for p in ads.SearchQuery(
        q=f"docs(library/{false_lib.id})",
        sort='date desc',
        max_pages=100,
        fl=['bibcode']
    )
]

papers = [p for p in papers if p.bibcode not in falsebibs]

def get_author_index(authors, name) -> list[int]:
    """Get the index of the author."""
    if ',' in name:
        first = name.split(',')[1].strip()
        last = name.split(',')[0].strip()
    else:
        first = name.split(' ')[0].strip()
        last = name.split(' ')[1:].strip()

    # Reduce by last name first.
    bools = [last in a for a in authors]

    if sum(bools) == 1:
        return [bools.index(True)]
    elif sum(bools) == 0:
        return []

    # Otherwise, there are multiple authors with the author's last name. Try matching first.
    bools = [b and a.split(',')[1].strip().startswith(first[0]) for a, b in zip(authors, bools)]

    if sum(bools) == 1:
        return [bools.index(True)]
    elif sum(bools) == 0:
        return []

    return [idx for idx, b in enumerate(bools) if b]

indices = [get_author_index(p.author, name) for p in papers]
author_aff = [[p.aff[idx] for idx in idxs] for p, idxs in zip(papers, indices)]
orcids = [[p.orcid_pub[idx] if p.orcid_pub else '-' for idx in idxs] for p, idxs in zip(papers, indices)]


# Let's filter papers down by specifically checking affiliations and orcids at the author index.
mask = [(orcid in orc or '-' in orc or not orc) for orc in orcids ]
papers = [p for m, p in zip(mask, papers) if m]
indices = [p for m, p in zip(mask, indices) if m]
author_aff = [p for m, p in zip(mask, author_aff) if m]
orcids = [p for m, p in zip(mask, orcids) if m]


mask = [not affs or any(any(a in aff for a in cfg['affiliations']) for aff in affs) for affs in author_aff]
papers = [p for m, p in zip(mask, papers) if m]
indices = [p for m, p in zip(mask, indices) if m]
author_aff = [p for m, p in zip(mask, author_aff) if m]
orcids = [p for m, p in zip(mask, orcids) if m]


known_papers = list(ads.SearchQuery(q=f"docs(library/{library.id})", fl=['author', 'title', 'year', 'bibcode', 'aff', 'orcid_pub'], max_pages=100))

already_in = [p for p in papers if p in known_papers]
new_papers = [p for p in papers if p not in known_papers]
excess_papers = [p for p in known_papers if p not in papers]

new_indices = [a for a, p in zip(indices, papers) if p not in known_papers]
new_author_aff = [a for a, p in zip(author_aff, papers) if p not in known_papers]
new_orcids = [a for a, p in zip(orcids, papers) if p not in known_papers]

print(f"Found {len(papers)} papers in the search. {len(already_in)} were already in your library. {len(new_papers)} are new.")

if excess_papers:
    res = qs.select(f"WARNING: {len(excess_papers)} papers are in the library, but not in your search. Select whether to REMOVE them:", choices=['yes to all', 'no to all', 'choose each', 'just print']).ask()
    if res == 'yes to all':
       remove = [p.bibcode for p in excess_papers]
    elif res == 'no to all':
        remove = []
    elif res == 'just print':
        for p in excess_papers:
            print(f"{','.join(p.author)}: {p.title[0]} ({p.year}) / {p.aff} {p.orcid_pub}")
        remove = []
    else:
        remove = []
        for p in excess_papers:
            res = qs.select(f"{','.join(p.author)}: {p.title[0]} ({p.year})", choices=['yes', 'no'], default='yes').ask()
            if res =='yes':
                remove.append(p.bibcode)

    library.remove_documents(remove)

if n := len(new_papers):
    print(f"Found {n} new papers, please select whether each one should be in your library:")
    keep = []
    no_keep = []
    for (p, orc, aff, idx) in zip(new_papers, new_orcids, new_author_aff, new_indices):
        res = qs.select(f"{p.author[0]}: {p.title[0]} ({p.year}) orcid:{orc} aff:{aff} authnames: {[p.author[i] for i in idx]}", choices=['yes', 'no', 'not sure', 'quit'], default='yes').ask()
        if res =='yes':
            keep.append(p.bibcode)
        elif res=='no':
            no_keep.append(p.bibcode)
        elif res == 'quit':
    # Now we've updated the library, we re-get all the papers in the actual library.
    papers = list(ads.SearchQuery(
        q=f'docs(library/{library.id}) NOT orcid:{orcid}',
        sort='date desc',
        max_pages=100,
        fl=['author', 'title', 'bibcode', 'year', 'orcid_pub']
    ))

    if papers:
        print("The following papers were in your library but are not associated with your ORCID on ADS:")
        for p in papers:
            print(f"  - {p.author[0]}: {p.title[0]} ({p.year})")
        print("Follow this link to associate them: ")
        bibcodes = "%20OR%20".join([p.bibcode for p in papers])
        print(f'  https://ui.adsabs.harvard.edu/search/q=docs(library%2F{library.id})%20NOT%20orcid%3A{orcid}')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Print out all LoCo publications.')
    parser.add_argument("config", type=str)
    args = parser.parse_args()
    
    main(Path(args.config)
    for p in papers:
        print(f"  - {p.author[0]}: {p.title[0]} ({p.year})")
    print("Follow this link to associate them: ")
    bibcodes = "%20OR%20".join([p.bibcode for p in papers])
    print(f'  https://ui.adsabs.harvard.edu/search/q=docs(library%2F{library.id})%20NOT%20orcid%3A{orcid}')

