"""
fred_client.py — Thin wrapper around the FRED API.

Responsibilities:
  • Initialise the fredapi client once.
  • Fetch individual series with an in-memory cache so callbacks never
    re-fetch the same series during the app's lifetime.
  • Return pandas Series/DataFrames consistently.
  • Retry on transient failures (500s, timeouts) with exponential backoff.

FRED enforces strict rate limits (~120 req / min). The module-level cache
ensures we hit the API at most once per series per app restart.
"""

from __future__ import annotations

import logging
import time
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
# Failed series tracker — so the UI can report what's missing
# ---------------------------------------------------------------------------
_failures: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------
_fred: Optional[Fred] = None

# Retry config
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubled each attempt


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
    Fetch a FRED series with retry logic and cache it.

    Retries up to MAX_RETRIES times on transient errors (500s, timeouts).
    Subsequent calls for the same *series_id* return the cached copy.

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

    Raises
    ------
    Exception if all retries are exhausted.
    """
    if series_id in _cache:
        return _cache[series_id]

    if start is None:
        start = date.today() - timedelta(days=DEFAULT_LOOKBACK_YEARS * 365)
    if end is None:
        end = date.today()

    fred = _get_client()

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            logger.info("Fetching FRED series %s (attempt %d)", series_id, attempt + 1)
            data: pd.Series = fred.get_series(
                series_id, observation_start=start, observation_end=end
            )
            data.name = series_id
            data = data.dropna()
            _cache[series_id] = data
            # Clear any prior failure record
            _failures.pop(series_id, None)
            return data
        except Exception as exc:
            last_exc = exc
            wait = RETRY_BACKOFF * (2 ** attempt)
            logger.warning(
                "FRED %s attempt %d failed: %s — retrying in %ds",
                series_id, attempt + 1, exc, wait,
            )
            time.sleep(wait)

    # All retries exhausted — record the failure and re-raise
    _failures[series_id] = str(last_exc)
    raise last_exc  # type: ignore[misc]


def get_series_safe(series_id: str) -> pd.Series:
    """
    Like get_series but returns an empty Series on failure instead of raising.
    Records the failure for the UI to display.
    """
    try:
        return get_series(series_id)
    except Exception as exc:
        logger.error("Could not load %s after retries: %s", series_id, exc)
        _failures[series_id] = str(exc)
        return pd.Series(dtype=float, name=series_id)


def get_multiple(series_ids: list[str], safe: bool = True) -> dict[str, pd.Series]:
    """Fetch several series. If safe=True, failures return empty Series."""
    fetcher = get_series_safe if safe else get_series
    return {sid: fetcher(sid) for sid in series_ids}


def get_failures() -> dict[str, str]:
    """Return dict of series_id → error message for any failed fetches."""
    return dict(_failures)


def clear_cache() -> None:
    """Flush the in-memory cache (useful for manual refresh)."""
    _cache.clear()
    _failures.clear()
