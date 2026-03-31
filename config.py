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
# Treasury yield-curve maturities (short → long)
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
RECESSION_SERIES = "USREC"

# ---------------------------------------------------------------------------
# Default lookback
# ---------------------------------------------------------------------------
DEFAULT_LOOKBACK_YEARS = 10

# ---------------------------------------------------------------------------
# Styling — Clean, minimal, refined
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_white"

# Backgrounds
BG_PRIMARY = "#fafbfc"
BG_SECONDARY = "#ffffff"

# A restrained, confident palette
COLORS = [
    "#2563eb",  # Clean blue — primary
    "#0d9488",  # Teal
    "#dc2626",  # Red — crisp, not angry
    "#7c3aed",  # Purple
    "#ea580c",  # Warm orange
    "#0891b2",  # Cyan
    "#4f46e5",  # Indigo
    "#059669",  # Emerald
    "#d97706",  # Amber
    "#be185d",  # Rose
]

# Recession shading — soft, unobtrusive
RECESSION_FILL_COLOR = "rgba(220, 38, 38, 0.06)"

# Text
TEXT_PRIMARY = "#1a1a2e"
TEXT_SECONDARY = "#8b919a"
TEXT_ACCENT = "#1a1a2e"

# Grid — barely visible, clean
GRID_COLOR = "rgba(0, 0, 0, 0.04)"
