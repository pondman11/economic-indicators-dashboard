"""
news_client.py — Fetch relevant financial news via Google News RSS.

No API key required. Uses feedparser to parse Google News RSS feeds
with topic-specific search queries. Results are cached to avoid
hammering Google on every tab switch.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import feedparser

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache settings
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[float, list["NewsItem"]]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published: str


# ---------------------------------------------------------------------------
# Search queries mapped to each dashboard tab
# ---------------------------------------------------------------------------
TAB_QUERIES = {
    "yield_curve": "treasury yield curve rates",
    "spreads": "yield curve inversion recession indicator",
    "indicators": "economic indicators consumer sentiment jobless claims",
    "inflation": "inflation CPI federal reserve interest rates",
}


def _parse_source(title: str) -> tuple[str, str]:
    """Google News titles include ' - Source' at the end. Split them."""
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        return parts[0].strip(), parts[1].strip()
    return title, ""


def fetch_news(tab_key: str, max_results: int = 8) -> list[NewsItem]:
    """
    Fetch news articles relevant to a dashboard tab.

    Uses Google News RSS with a search query. Results are cached for
    CACHE_TTL_SECONDS to avoid excessive requests.

    Parameters
    ----------
    tab_key : one of 'yield_curve', 'spreads', 'indicators', 'inflation'
    max_results : max articles to return

    Returns
    -------
    List of NewsItem with title, url, source, published date.
    """
    # Check cache
    if tab_key in _cache:
        cached_time, cached_items = _cache[tab_key]
        if time.time() - cached_time < CACHE_TTL_SECONDS:
            return cached_items[:max_results]

    query = TAB_QUERIES.get(tab_key, "economic indicators")
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(url)
        items: list[NewsItem] = []
        for entry in feed.entries[:max_results]:
            title, source = _parse_source(entry.get("title", ""))
            items.append(NewsItem(
                title=title,
                url=entry.get("link", ""),
                source=source,
                published=entry.get("published", ""),
            ))
        _cache[tab_key] = (time.time(), items)
        return items
    except Exception as exc:
        logger.warning("Failed to fetch news for %s: %s", tab_key, exc)
        return []
