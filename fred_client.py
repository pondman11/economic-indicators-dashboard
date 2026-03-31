"""
fred_client.py — Thin wrapper around the FRED API.

Responsibilities:
  • Initialise the fredapi client once.
  • Fetch individual series with an in-memory cache so callbacks never
    re-fetch the same series during the app's lifetime.
  • Return pandas Series/DataFrames consistently.

FRED enforces strict rate limits (~120 req / min). The module-level cache
ensures we hit the API at most once per series per app restart.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

import pandas as pd
from fredapi import Fred

from config import FRED_API_KEY, DEFAULT_LOOKBACK_YEARS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cache: series_id → pd.Series
# ---------------------------------------------------------------------------
_cache: dict[str, pd.Series] = {}

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------
_fred: Optional[Fred] = None


def _get_client() -> Fred:
    """Lazily initialise and return the Fred client."""
    global _fred
    if _fred is None:
        if not FRED_API_KEY:
            raise EnvironmentError(
                "FRED_API_KEY environment variable is not set. "
                "Register for a free key at https://fred.stlouisfed.org/docs/api/api_key.html "
                "then export FRED_API_KEY=<your-key>."
            )
        _fred = Fred(api_key=FRED_API_KEY)
    return _fred


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_series(
    series_id: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> pd.Series:
    """
    Fetch a FRED series and cache it.  Subsequent calls for the same
    *series_id* return the cached copy instantly (ignoring date params — the
    full series is stored).

    Parameters
    ----------
    series_id : str
        FRED series identifier (e.g. "DGS10").
    start : date, optional
        Observation start date.  Defaults to *DEFAULT_LOOKBACK_YEARS* ago.
    end : date, optional
        Observation end date.  Defaults to today.

    Returns
    -------
    pd.Series with a DatetimeIndex and float values.
    """
    if series_id in _cache:
        return _cache[series_id]

    if start is None:
        start = date.today() - timedelta(days=DEFAULT_LOOKBACK_YEARS * 365)
    if end is None:
        end = date.today()

    fred = _get_client()
    logger.info("Fetching FRED series %s (%s → %s)", series_id, start, end)

    data: pd.Series = fred.get_series(series_id, observation_start=start, observation_end=end)
    data.name = series_id
    data = data.dropna()

    _cache[series_id] = data
    return data


def get_multiple(series_ids: list[str]) -> dict[str, pd.Series]:
    """Convenience: fetch several series and return as a dict."""
    return {sid: get_series(sid) for sid in series_ids}


def clear_cache() -> None:
    """Flush the in-memory cache (useful for manual refresh)."""
    _cache.clear()
