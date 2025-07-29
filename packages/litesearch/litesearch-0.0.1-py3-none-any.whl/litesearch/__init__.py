"""
LiteSearch - A unified and extensible AI-oriented search abstraction layer.

A modern framework that bridges traditional search engine results with
AI-native applications.
"""

__version__ = "0.0.1"
__author__ = "xmingc"
__email__ = "chenxm35@gmail.com"

from .core import LiteSearch
from .engines import DuckDuckGoEngine, GoogleEngine, SearchEngine
from .models import SearchQuery, SearchResult

__all__ = [
    "LiteSearch",
    "SearchResult",
    "SearchQuery",
    "SearchEngine",
    "GoogleEngine",
    "DuckDuckGoEngine",
]
