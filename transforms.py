"""
transforms.py — Pure data-transformation helpers.

These functions operate on pandas objects and know nothing about FRED or Dash.
Keeping them separate makes testing and reuse straightforward.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import YIELD_CURVE_SERIES, MATURITY_ORDER


# ---------------------------------------------------------------------------
# Yield-curve helpers
# ---------------------------------------------------------------------------

def build_yield_curve_df(series_dict: dict[str, pd.Series]) -> pd.DataFrame:
    """
    Combine individual Treasury maturity series into a single DataFrame.

    Columns are ordered short → long and renamed to human labels (1M … 30Y).
    Index is a DatetimeIndex (daily observations).
    """
    frames = {}
    for sid, label in YIELD_CURVE_SERIES.items():
        if sid in series_dict:
            frames[label] = series_dict[sid]
    df = pd.DataFrame(frames)
    # Ensure column order matches short → long
    df = df[[c for c in MATURITY_ORDER if c in df.columns]]
    return df


def yield_curve_snapshot(df: pd.DataFrame, as_of: str | pd.Timestamp | None = None) -> pd.Series:
    """
    Return the yield curve for a single date.

    Parameters
    ----------
    df : DataFrame from build_yield_curve_df
    as_of : date string or Timestamp.  If None, use the last available date.

    Returns
    -------
    pd.Series indexed by maturity label.
    """
    if as_of is None:
        row = df.dropna(how="all").iloc[-1]
    else:
        # Find the closest prior business day if exact date missing
        idx = df.index.get_indexer([pd.Timestamp(as_of)], method="ffill")
        row = df.iloc[idx[0]]
    return row


# ---------------------------------------------------------------------------
# Spread / recession helpers
# ---------------------------------------------------------------------------

def recession_periods(usrec: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """
    Convert the binary USREC indicator into a list of (start, end) tuples
    suitable for adding shaded rectangles to a Plotly chart.
    """
    periods: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    in_recession = False
    start = None
    for dt, val in usrec.items():
        if val == 1 and not in_recession:
            start = dt
            in_recession = True
        elif val == 0 and in_recession:
            periods.append((start, dt))  # type: ignore[arg-type]
            in_recession = False
    # If the series ends inside a recession, close it at the last date
    if in_recession and start is not None:
        periods.append((start, usrec.index[-1]))
    return periods


# ---------------------------------------------------------------------------
# Inflation helpers
# ---------------------------------------------------------------------------

def yoy_pct_change(series: pd.Series, periods: int = 12) -> pd.Series:
    """
    Compute year-over-year percentage change for a monthly series.

    Formula: (value / value_12_months_ago − 1) × 100
    """
    return (series / series.shift(periods) - 1) * 100


# ---------------------------------------------------------------------------
# Leading-indicator helpers
# ---------------------------------------------------------------------------

def rolling_mean(series: pd.Series, window: int = 4) -> pd.Series:
    """Simple rolling mean (used for 4-week MA on initial claims)."""
    return series.rolling(window=window, min_periods=1).mean()
