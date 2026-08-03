"""ADS (Astrophysics Data System) integration for publications."""

from .connector import DataConnector
from .nasa_ads import (
    compare_query_to_library,
    obtain_library_papers,
    obtain_query_papers,
    read_library_cache,
    write_library_cache,
)

__all__ = [
    "DataConnector",
    "compare_query_to_library",
    "obtain_library_papers",
    "obtain_query_papers",
    "read_library_cache",
    "write_library_cache",
]
