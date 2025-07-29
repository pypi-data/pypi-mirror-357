"""
Data models for LiteSearch.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Represents a search query."""

    query: str = Field(..., description="The search query string")
    engine: str = Field(default="google", description="Search engine to use")
    max_results: int = Field(
        default=10, ge=1, le=100, description="Maximum number of results"
    )
    language: str = Field(default="en", description="Search language")
    region: Optional[str] = Field(
        default=None, description="Geographic region for search"
    )
    safe_search: bool = Field(default=True, description="Enable safe search filtering")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Python AI libraries",
                "engine": "google",
                "max_results": 10,
                "language": "en",
                "region": "US",
                "safe_search": True,
            }
        }


class SearchResult(BaseModel):
    """Represents a single search result."""

    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet/description")
    rank: int = Field(..., description="Result rank/position")
    engine: str = Field(..., description="Source search engine")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When result was fetched"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python AI Libraries - Top 10 Most Popular",
                "url": "https://example.com/python-ai-libraries",
                "snippet": "Discover the most popular Python AI libraries for machine learning...",
                "rank": 1,
                "engine": "google",
                "timestamp": "2024-01-01T12:00:00",
                "metadata": {"domain": "example.com", "language": "en"},
            }
        }


class SearchResponse(BaseModel):
    """Represents a complete search response."""

    query: SearchQuery = Field(..., description="Original search query")
    results: List[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    total_results: int = Field(default=0, description="Total number of results found")
    search_time: float = Field(
        default=0.0, description="Search execution time in seconds"
    )
    engine_used: str = Field(..., description="Search engine that was used")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When search was performed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": {"query": "Python AI libraries", "engine": "google"},
                "results": [],
                "total_results": 0,
                "search_time": 1.23,
                "engine_used": "google",
                "timestamp": "2024-01-01T12:00:00",
            }
        }
