"""
Core LiteSearch functionality.
"""

from typing import Dict, List, Optional, Type

from dotenv import load_dotenv

from .engines import DuckDuckGoEngine, GoogleEngine, SearchEngine
from .models import SearchQuery, SearchResponse


class LiteSearch:
    """
    Main LiteSearch class for unified search operations.

    Provides a unified interface to multiple search engines with AI-oriented
    result processing and structured output.
    """

    def __init__(self):
        """Initialize LiteSearch with available search engines."""
        load_dotenv()

        self.engines: Dict[str, Type[SearchEngine]] = {
            "google": GoogleEngine,
            "duckduckgo": DuckDuckGoEngine,
        }

        self.default_engine = "google"

    def register_engine(self, name: str, engine_class: Type[SearchEngine]) -> None:
        """Register a new search engine."""
        self.engines[name] = engine_class

    def get_available_engines(self) -> List[str]:
        """Get list of available search engine names."""
        return list(self.engines.keys())

    async def search(
        self,
        query: str,
        engine: Optional[str] = None,
        max_results: int = 10,
        language: str = "en",
        region: Optional[str] = None,
        safe_search: bool = True,
    ) -> SearchResponse:
        """
        Perform a search using the specified engine.

        Args:
            query: Search query string
            engine: Search engine to use (defaults to default_engine)
            max_results: Maximum number of results to return
            language: Search language code
            region: Geographic region for search
            safe_search: Enable safe search filtering

        Returns:
            SearchResponse with results and metadata
        """
        # Create search query
        search_query = SearchQuery(
            query=query,
            engine=engine or self.default_engine,
            max_results=max_results,
            language=language,
            region=region,
            safe_search=safe_search,
        )

        # Get engine class
        engine_name = search_query.engine
        if engine_name not in self.engines:
            raise ValueError(f"Unknown search engine: {engine_name}")

        engine_class = self.engines[engine_name]

        # Perform search
        async with engine_class() as engine_instance:
            return await engine_instance.search(search_query)

    async def search_multiple(
        self,
        query: str,
        engines: List[str],
        max_results: int = 10,
        language: str = "en",
        region: Optional[str] = None,
        safe_search: bool = True,
    ) -> Dict[str, SearchResponse]:
        """
        Perform search using multiple engines concurrently.

        Args:
            query: Search query string
            engines: List of search engine names to use
            max_results: Maximum number of results per engine
            language: Search language code
            region: Geographic region for search
            safe_search: Enable safe search filtering

        Returns:
            Dictionary mapping engine names to SearchResponse objects
        """
        # Validate engines
        for engine in engines:
            if engine not in self.engines:
                raise ValueError(f"Unknown search engine: {engine}")

        # Create search tasks
        tasks = []
        for engine_name in engines:
            task = self.search(
                query=query,
                engine=engine_name,
                max_results=max_results,
                language=language,
                region=region,
                safe_search=safe_search,
            )
            tasks.append((engine_name, task))

        # Execute searches concurrently
        results = {}
        for engine_name, task in tasks:
            try:
                results[engine_name] = await task
            except Exception:
                # Create empty response for failed engines
                search_query = SearchQuery(
                    query=query,
                    engine=engine_name,
                    max_results=max_results,
                    language=language,
                    region=region,
                    safe_search=safe_search,
                )
                results[engine_name] = SearchResponse(
                    query=search_query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    engine_used=engine_name,
                )

        return results

    def set_default_engine(self, engine: str) -> None:
        """Set the default search engine."""
        if engine not in self.engines:
            raise ValueError(f"Unknown search engine: {engine}")
        self.default_engine = engine
