"""
config.py — Central configuration for FRED series, styling, and constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# FRED API Key
# ---------------------------------------------------------------------------
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# ---------------------------------------------------------------------------
# Treasury yield-curve maturities (short to long)
# ---------------------------------------------------------------------------
YIELD_CURVE_SERIES = {
    "DGS1MO": "1M",
    "DGS3MO": "3M",
    "DGS6MO": "6M",
    "DGS1":   "1Y",
    "DGS2":   "2Y",
    "DGS3":   "3Y",
    "DGS5":   "5Y",
    "DGS7":   "7Y",
    "DGS10":  "10Y",
    "DGS20":  "20Y",
    "DGS30":  "30Y",
}

MATURITY_YEARS = {
    "1M": 1/12, "3M": 3/12, "6M": 6/12,
    "1Y": 1, "2Y": 2, "3Y": 3, "5Y": 5,
    "7Y": 7, "10Y": 10, "20Y": 20, "30Y": 30,
}

MATURITY_ORDER = list(YIELD_CURVE_SERIES.values())

# ---------------------------------------------------------------------------
# Spread series
# ---------------------------------------------------------------------------
SPREAD_SERIES = {
    "T10Y2Y": "10Y - 2Y",
    "T10Y3M": "10Y - 3M",
}

# ---------------------------------------------------------------------------
# Macro / leading-indicator series
# ---------------------------------------------------------------------------
MACRO_SERIES = {
    "FEDFUNDS": "Fed Funds Rate",
    "CPIAUCSL": "CPI (All Urban)",
    "CPILFESL": "Core CPI",
    "PCEPI":    "PCE Price Index",
    "UMCSENT":  "Consumer Sentiment",
    "ICSA":     "Initial Jobless Claims",
    "PERMIT":   "Building Permits",
}

# ---------------------------------------------------------------------------
# Recession indicator
# ---------------------------------------------------------------------------
RECESSION_SERIES = "USREC"

# ---------------------------------------------------------------------------
# Default lookback
# ---------------------------------------------------------------------------
DEFAULT_LOOKBACK_YEARS = 10

# ---------------------------------------------------------------------------
# Styling — Dark, clean
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_dark"

# Backgrounds
BG_PRIMARY = "#0f1117"
BG_SECONDARY = "#161b22"
BG_CHART = "#0d1117"

# Clean palette — high contrast on dark, no muddy tones
COLORS = [
    "#58a6ff",  # Blue
    "#3fb950",  # Green
    "#f85149",  # Red
    "#bc8cff",  # Purple
    "#d29922",  # Amber
    "#39d2c0",  # Teal
    "#79c0ff",  # Light blue
    "#f0883e",  # Orange
    "#a5d6ff",  # Pale blue
    "#ffa198",  # Salmon
]

# Recession shading
RECESSION_FILL_COLOR = "rgba(248, 81, 73, 0.07)"

# Text
TEXT_PRIMARY = "#e1e4e8"
TEXT_SECONDARY = "#7d8590"

# Grid
GRID_COLOR = "rgba(255, 255, 255, 0.04)"
AXIS_COLOR = "#21262d"
