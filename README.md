# Economic Indicators & Yield Curve Dashboard

A Plotly Dash application that pulls macroeconomic time series from the Federal Reserve Economic Data (FRED) API and visualizes yield curve dynamics, leading economic indicators, and recession signals.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## Features

| Tab | What it shows |
|-----|---------------|
| **Yield Curve** | Current US Treasury yield curve (1M–30Y) with historical overlays, plus a heatmap showing yield levels across maturities over time |
| **Spreads & Recession** | 10Y−2Y and 10Y−3M spreads with NBER recession shading and inversion threshold |
| **Leading Indicators** | 2×2 grid: Consumer Sentiment, Initial Claims (4-wk MA), Building Permits, 10Y−2Y spread — all with recession shading |
| **Inflation & Policy** | CPI / Core CPI / PCE year-over-year % with Fed 2% target line; Effective Fed Funds Rate step chart |

## Prerequisites

- Python 3.10+
- A free FRED API key

## Getting a FRED API Key

1. Go to <https://fred.stlouisfed.org/docs/api/api_key.html>
2. Create an account (or sign in)
3. Request an API key — it's free and instant

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd economic-indicators-dashboard

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your FRED API key
export FRED_API_KEY=your_key_here   # Windows: set FRED_API_KEY=your_key_here

# Run the app
python app.py
```

Open <http://localhost:8050> in your browser.

## Project Structure

```
economic-indicators-dashboard/
├── app.py                  # Dash app entry point, layout, and callbacks
├── fred_client.py          # FRED API wrapper with in-memory caching
├── transforms.py           # YoY calculations, spread computations, helpers
├── config.py               # FRED series IDs, maturity mappings, constants
├── components/
│   ├── yield_curve.py      # Yield curve snapshot & heatmap chart builders
│   ├── spreads.py          # Spread monitor with recession shading
│   ├── indicators.py       # Leading indicators 2×2 grid
│   └── inflation.py        # Inflation comparison & Fed Funds rate charts
├── requirements.txt
└── README.md
```

## Configuration

All FRED series IDs, maturity mappings, colour palettes, and default lookback windows live in `config.py`. Modify that file to add series or change styling.

## Deployment

The app exposes a `server` variable (`app.server`) compatible with WSGI servers:

```bash
gunicorn app:server -b 0.0.0.0:8050
```

## License

MIT
