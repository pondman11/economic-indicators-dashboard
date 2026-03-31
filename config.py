"""
config.py — Central configuration for FRED series IDs, maturity mappings,
NBER recession dates, and other constants used across the dashboard.
"""

import os

from dotenv import load_dotenv

# Load variables from .env file (if present) so the API key doesn't need to
# be exported manually every time.
load_dotenv()

# ---------------------------------------------------------------------------
# FRED API Key
# ---------------------------------------------------------------------------
# Loaded from environment so it is never committed to source control.
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# ---------------------------------------------------------------------------
# Treasury yield-curve maturities
# ---------------------------------------------------------------------------
# Ordered short → long. The dict maps FRED series IDs to human-readable labels.
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

# Numeric representation of each maturity in years (for x-axis positioning)
MATURITY_YEARS = {
    "1M": 1 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "1Y": 1,
    "2Y": 2,
    "3Y": 3,
    "5Y": 5,
    "7Y": 7,
    "10Y": 10,
    "20Y": 20,
    "30Y": 30,
}

# Ordered list of maturity labels (short → long) for consistent axis ordering.
MATURITY_ORDER = list(YIELD_CURVE_SERIES.values())

# ---------------------------------------------------------------------------
# Spread series
# ---------------------------------------------------------------------------
SPREAD_SERIES = {
    "T10Y2Y": "10Y − 2Y",
    "T10Y3M": "10Y − 3M",
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
RECESSION_SERIES = "USREC"  # 1 = recession, 0 = expansion

# ---------------------------------------------------------------------------
# Default lookback window (years)
# ---------------------------------------------------------------------------
DEFAULT_LOOKBACK_YEARS = 10

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_white"

# Muted color palette for chart lines
COLORS = [
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
]

# Recession shading fill color (translucent red/orange)
RECESSION_FILL_COLOR = "rgba(255, 100, 100, 0.15)"
