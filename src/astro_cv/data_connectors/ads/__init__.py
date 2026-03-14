"""ADS (Astrophysics Data System) integration for publications."""

from .connector import DataConnector
from .nasa_ads import (
    obtain_library_papers,
    obtain_query_papers,
    compare_query_to_library,
    write_library_cache,
    read_library_cache,
)

__all__ = [
    "DataConnector",
    "obtain_library_papers",
    "obtain_query_papers",
    "compare_query_to_library",
    "write_library_cache",
    "read_library_cache",
]
