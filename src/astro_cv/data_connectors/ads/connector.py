"""ADS (Astrophysics Data System) data connector for publications."""

from pathlib import Path
from typing import Optional, Any
from ads.libraries import Article

import attrs
from ads.libraries import Library
from astro_cv.sections.publications import PublicationList, Publication
from .nasa_ads import obtain_library_papers


class DataConnector:
    """Connect to ADS and retrieve publication data."""

    def __init__(
        self,
        library_id: Optional[str] = None,
        cache_path: Optional[Path | str] = None,
        verbose: bool = False,
    ):
        """Initialize ADS connector.

        Parameters
        ----------
        library_id : str, optional
            ADS library ID to fetch publications from.
        cache_path : Path or str, optional
            Path to cache file for publications. If provided, will read from cache.
        verbose : bool
            Print status messages.
        """
        self.library_id = library_id
        self.cache_path = Path(cache_path) if cache_path else None
        self.verbose = verbose

    def get_publication_list(
        self,
        library_id: Optional[str] = None,
        use_cache: bool = True,
    ) -> PublicationList:
        """Get publication list from ADS library.

        Parameters
        ----------
        library_id : str, optional
            ADS library ID. If not provided, uses the one from initialization.
        use_cache : bool
            Whether to use cached publications if available.

        Returns
        -------
        PublicationList
            Publication list populated with papers from ADS library.
        """
        lib_id = library_id or self.library_id

        if not lib_id:
            raise ValueError("No library_id provided")

        if self.verbose:
            print(f"Fetching publications from ADS library: {lib_id}")

        # Get papers from ADS library (with caching handled internally)
        library = Library(lib_id)
        papers = obtain_library_papers(
            library,
            extra_fields=(
                "citation_count",
                "orcid_pub",
                "property",
                "aff",
                "doctype",
                "pub",
                "read_count",
                "volume",
                "page",
                "doi",
            ),
        )

        if self.verbose:
            print(f"Retrieved {len(papers)} publications")

        # Convert to Publication objects
        publications = []
        for paper in papers:
            pub = self.ads_article_to_publication(paper)
            publications.append(pub)

        return PublicationList(publications=tuple(publications))

    @classmethod
    def ads_article_to_publication(cls, article: Article) -> Publication:
        """Convert an ADS article object to a Publication."""
        return Publication(
            title=article.title[0],
            authors=article.author,
            year=int(article.year),
            bibcode=article.bibcode,
            citation_count=article.citation_count or 0,
            refereed="REFEREED" in article.property
            if hasattr(article, "properties")
            else False,
            orcid_pub=article.orcid_pub if hasattr(article, "orcid_pub") else None,
            aff=getattr(article, "aff", []),
            pub=article.pub or "",
            read_count=article.read_count,
            volume=article.volume,
            page=article.page,
            doi=article.doi,
            doctype=getattr(article, "doctype", ""),
        )

    @classmethod
    def get(cls, section_name: str, config_path: Path | str) -> Any:
        """Generic method to get section data from ADS.

        Parameters
        ----------
        section_name : str
            Name of the section (should be 'publications').
        config_path : Path or str
            Path to the section's TOML configuration file.

        Returns
        -------
        PublicationList
            Publication list populated with papers from ADS.

        Raises
        ------
        ValueError
            If the section_name is not 'publications'.
        """
        config_path = Path(config_path)
        section_key = section_name.replace("-", "_")

        if section_key != "publications":
            raise ValueError(
                f"DataConnector (ads) does not support '{section_name}'. "
                f"Only 'publications' is supported."
            )

        # Load settings from TOML file
        pub_list = PublicationList.read_toml(config_path)

        # Fetch publications using library ID
        if not pub_list.library:
            print("Warning: No library ID in config, skipping publication fetch")
            return pub_list

        # Create a temporary connector with the library ID to fetch publications
        temp_conn = cls(library_id=pub_list.library, verbose=False)
        fetched_publications = temp_conn.get_publication_list(pub_list.library)

        # Return a new PublicationList with publications merged in
        return attrs.evolve(pub_list, publications=fetched_publications.publications)
