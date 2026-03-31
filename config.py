"""
config.py — Central configuration.

"Entropy is the figure of Death."
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# FRED API Key
# ---------------------------------------------------------------------------
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# ---------------------------------------------------------------------------
# Treasury yield-curve maturities
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
    "1M": 1 / 12,  "3M": 3 / 12,  "6M": 6 / 12,
    "1Y": 1,  "2Y": 2,  "3Y": 3,  "5Y": 5,
    "7Y": 7,  "10Y": 10,  "20Y": 20,  "30Y": 30,
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
# Pynchon Terminal — Color System
#
# A palette drawn from old wartime dispatches, fading signal lamps,
# the amber of whiskey and suspicion, the green of radar and money,
# and the red that means it's already too late.
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_dark"

# Backgrounds — the void behind the signal
BG_PRIMARY = "#07070d"       # The deepest dark — pre-dawn Berlin
BG_SECONDARY = "#0d0d15"    # Panel/card — a room with no windows
BG_TERTIARY = "#141425"     # Hover — someone just walked in

# Border — barely perceptible, like a pattern you can't quite prove
BORDER_COLOR = "rgba(255, 200, 50, 0.08)"

# The palette: each color tells a lie
COLORS = [
    "#c8a84e",  # Aged parchment gold — the document you weren't supposed to see
    "#5e9e7e",  # Muted institutional green — the color of money and radar
    "#c4705a",  # Faded terracotta — rust, old blood, Rilke's autumn
    "#7a8ec4",  # Slate blue — the bureaucracy, the sky over Peenemünde
    "#c4a07a",  # Warm sand — North Africa, Valletta, the desert of the real
    "#8e7eb8",  # Dusted violet — twilight, the zone, Slothrop's dream
    "#6aaa8a",  # Verdigris — oxidation, entropy made visible
    "#c48a5e",  # Amber — whiskey, warning lights, late afternoon
    "#7a9ab4",  # Washed denim blue — the sea, distance, escape
    "#b47a7a",  # Muted rose — the memory of something that didn't happen
]

# Recession — They already know. The shading is just a formality.
RECESSION_FILL_COLOR = "rgba(180, 60, 50, 0.10)"

# Text
TEXT_PRIMARY = "#c8c8d4"     # Typewriter ribbon, slightly worn
TEXT_SECONDARY = "#6a6a88"   # Marginalia, pencil annotations
TEXT_ACCENT = "#e8d5a3"      # The signal — amber, warm, unreliable

# Grid — barely there, like a conspiracy
GRID_COLOR = "rgba(200, 168, 78, 0.06)"

# ---------------------------------------------------------------------------
# Pynchon Epigraphs — one per tab
# ---------------------------------------------------------------------------
EPIGRAPHS = {
    "yield_curve": (
        "\"If they can get you asking the wrong questions, "
        "they don't have to worry about answers.\"",
        "— Gravity's Rainbow"
    ),
    "spreads": (
        "\"Behind the hieroglyphic streets there would either be a "
        "transcendent meaning, or only the earth.\"",
        "— The Crying of Lot 49"
    ),
    "indicators": (
        "\"She had heard all about excluded middles; they were bad shit, "
        "to be avoided.\"",
        "— The Crying of Lot 49"
    ),
    "inflation": (
        "\"Entropy is the figure of Death.\"",
        "— Slow Learner"
    ),
}
