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
# Dark Terminal Styling — Bloomberg meets the future
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_dark"

# Background colors
BG_PRIMARY = "#0a0a0f"       # Deep space black
BG_SECONDARY = "#12121a"     # Card/panel background
BG_TERTIARY = "#1a1a2e"      # Slightly lighter for hover states
BORDER_COLOR = "#2a2a3e"     # Subtle border glow

# Accent colors — electric, high contrast on dark
COLORS = [
    "#00d4ff",  # Electric cyan
    "#ff6b35",  # Hot orange
    "#00ff88",  # Neon green
    "#ff3366",  # Hot pink
    "#aa77ff",  # Electric purple
    "#ffcc00",  # Gold
    "#00ffcc",  # Mint
    "#ff77aa",  # Coral pink
    "#77aaff",  # Soft blue
    "#ffaa00",  # Amber
]

# Recession shading — ominous red glow
RECESSION_FILL_COLOR = "rgba(255, 50, 50, 0.12)"

# Text colors
TEXT_PRIMARY = "#e0e0e8"
TEXT_SECONDARY = "#8888aa"
TEXT_ACCENT = "#00d4ff"

# Chart grid
GRID_COLOR = "rgba(255, 255, 255, 0.06)"

# Plotly layout defaults applied to every figure
CHART_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=BG_SECONDARY,
    plot_bgcolor=BG_PRIMARY,
    font=dict(
        family="'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
        color=TEXT_PRIMARY,
        size=12,
    ),
    title_font=dict(size=16, color=TEXT_ACCENT),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    hoverlabel=dict(
        bgcolor=BG_TERTIARY,
        font_color=TEXT_PRIMARY,
        bordercolor=TEXT_ACCENT,
    ),
)
