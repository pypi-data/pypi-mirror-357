"""
Search engine implementations for LiteSearch.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

from .models import SearchQuery, SearchResponse, SearchResult


class SearchEngine(ABC):
    """Abstract base class for search engines."""

    def __init__(self, name: str):
        self.name = name
        self.session: Optional[aiohttp.ClientSession] = None

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform a search and return results."""

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()


class GoogleEngine(SearchEngine):
    """Google search engine implementation using web scraping."""

    def __init__(self):
        super().__init__("google")
        self.base_url = "https://www.google.com/search"
        self.crawler = AsyncWebCrawler()

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Search Google and parse results."""
        start_time = time.time()

        # Build search URL
        params = {
            "q": query.query,
            "num": min(query.max_results, 10),  # Google limits to 10 per page
            "hl": query.language,
        }
        if query.region:
            params["gl"] = query.region
        if not query.safe_search:
            params["safe"] = "off"

        search_url = f"{self.base_url}?{'&'.join(f'{k}={quote_plus(str(v))}' for k, v in params.items())}"

        try:
            # Use Crawl4AI to fetch the page
            result = await self.crawler.arun(
                url=search_url,
                instructions="Extract all search result titles, URLs, and snippets from the Google search results page",
            )

            # Parse results (this is a simplified implementation)
            results = self._parse_google_results(result.content, query.max_results)

            search_time = time.time() - start_time

            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                engine_used=self.name,
            )

        except Exception:
            # Return empty response on error
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                engine_used=self.name,
            )

    def _parse_google_results(
        self, html_content: str, max_results: int
    ) -> List[SearchResult]:
        """Parse Google search results from HTML."""
        results = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Find search result containers
        result_divs = soup.find_all("div", class_="g")

        for i, div in enumerate(result_divs[:max_results]):
            try:
                # Extract title and URL
                title_elem = div.find("h3")
                link_elem = div.find("a")
                snippet_elem = div.find("div", class_="VwiC3b")

                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # Clean URL (remove Google redirect)
                    if url.startswith("/url?q="):
                        url = url.split("/url?q=")[1].split("&")[0]

                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            rank=i + 1,
                            engine=self.name,
                        )
                    )
            except Exception:
                continue

        return results


class DuckDuckGoEngine(SearchEngine):
    """DuckDuckGo search engine implementation."""

    def __init__(self):
        super().__init__("duckduckgo")
        self.base_url = "https://html.duckduckgo.com/html"

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Search DuckDuckGo and parse results."""
        start_time = time.time()

        # Build search URL
        params = {
            "q": query.query,
            "kl": query.language,
        }
        if query.region:
            params["kl"] = f"{query.language}-{query.region}"

        search_url = f"{self.base_url}?{'&'.join(f'{k}={quote_plus(str(v))}' for k, v in params.items())}"

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(search_url) as response:
                html_content = await response.text()

            results = self._parse_duckduckgo_results(html_content, query.max_results)
            search_time = time.time() - start_time

            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                engine_used=self.name,
            )

        except Exception:
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                engine_used=self.name,
            )

    def _parse_duckduckgo_results(
        self, html_content: str, max_results: int
    ) -> List[SearchResult]:
        """Parse DuckDuckGo search results from HTML."""
        results = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Find search result containers
        result_divs = soup.find_all("div", class_="result")

        for i, div in enumerate(result_divs[:max_results]):
            try:
                # Extract title and URL
                title_elem = div.find("a", class_="result__a")
                snippet_elem = div.find("a", class_="result__snippet")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            rank=i + 1,
                            engine=self.name,
                        )
                    )
            except Exception:
                continue

        return results
