from .datatypes import Publication, PubList
from datetime import datetime

def compute_h_index(pub_list: PubList) -> int:
    """Compute the h-index for a given PubList."""
    citation_counts = sorted(
        (p.citation_count for p in pub_list.publications), 
        reverse=True
    )
    h_index = 0
    for i, count in enumerate(citation_counts, start=1):
        if count >= i:
            h_index = i
        else:
            break
    return h_index


def compute_i10_index(pub_list: PubList) -> int:
    """Compute the i10-index for a given PubList."""
    i10_index = sum(1 for p in pub_list.publications if p.citation_count >= 10)
    return i10_index

def citation_distribution(pub_list: PubList, bins: list[int] | None = None) -> dict[str, int]:
    """Compute the citation distribution for a given PubList."""
    if bins is None:
        bins = [0, 1, 5, 10, 20, 50, 100, 200, 500, 1000]
    citation_distribution = {f">{b}": 0 for b in bins}
    citation_distribution["<1"] = 0
    for p in pub_list.publications:
        count = p.citation_count
        placed = False
        for b in bins:
            if count < b:
                bin_label = f">{b}"
                citation_distribution[bin_label] += 1
                placed = True
                break
        if not placed:
            citation_distribution[f">{bins[-1]}"] += 1
    return citation_distribution

def average_citations(pub_list: PubList) -> float:
    """Compute the average number of citations per paper in a given PubList."""
    total_citations = sum(p.citation_count for p in pub_list.publications)
    num_papers = len(pub_list.publications)
    if num_papers == 0:
        return 0.0
    return total_citations / num_papers

def median_citations(pub_list: PubList) -> float:
    """Compute the median number of citations per paper in a given PubList."""
    citation_counts = sorted(p.citation_count for p in pub_list.publications)
    num_papers = len(citation_counts)
    if num_papers == 0:
        return 0.0
    mid = num_papers // 2
    if num_papers % 2 == 0:
        return (citation_counts[mid - 1] + citation_counts[mid]) / 2
    else:
        return float(citation_counts[mid])
    
def total_citations(pub_list: PubList) -> int:
    """Compute the total number of citations in a given PubList."""
    return sum(p.citation_count for p in pub_list)

def top_cited_papers(
    pub_list: PubList, 
    n: int = 5,
    per_year: bool = False,
) -> PubList:
    """Get the top n cited papers from a given PubList."""
    if per_year:
        key = lambda p: p.citations_per_year
    else:
        key = lambda p: p.citation_count

    sorted_pubs = sorted(
        pub_list.publications, 
        key=key, 
        reverse=True
    )
    return PubList(publications=tuple(sorted_pubs[:n]))

def average_citations_per_year(pub_list: PubList) -> float:
    """Compute the average citations per year for a given PubList."""
    total_citations = sum(p.citation_count for p in pub_list.publications)
    current_year = datetime.now().year
    total_years = sum(max(1, current_year - p.year) for p in pub_list.publications)
    if total_years == 0:
        return 0.0
    return total_citations / total_years