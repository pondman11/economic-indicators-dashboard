"""
app.py — Dash application entry point.

Assembles the layout (tabs powered by dash-bootstrap-components) and wires up
callbacks that build charts from cached FRED data.  Data is fetched once at
startup and stored in a module-level dict so callbacks stay fast.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd

# Project modules
from config import (
    FRED_API_KEY,
    YIELD_CURVE_SERIES,
    SPREAD_SERIES,
    RECESSION_SERIES,
    DEFAULT_LOOKBACK_YEARS,
    MATURITY_ORDER,
)
from fred_client import get_series, get_multiple
from transforms import build_yield_curve_df, yield_curve_snapshot
from components.yield_curve import yield_curve_snapshot_figure, yield_curve_heatmap_figure
from components.spreads import spread_monitor_figure
from components.indicators import leading_indicators_figure
from components.inflation import inflation_policy_figure

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Economic Indicators & Yield Curve",
    suppress_callback_exceptions=True,
)
server = app.server  # Expose for gunicorn / production deploys

# ---------------------------------------------------------------------------
# Pre-fetch data at startup (cached by fred_client)
# ---------------------------------------------------------------------------
DATA_ERROR: str | None = None  # Will hold an error message if data load fails

# Containers filled during startup
yc_df = pd.DataFrame()
spread_data: dict[str, pd.Series] = {}
usrec = pd.Series(dtype=float)
umcsent = pd.Series(dtype=float)
icsa = pd.Series(dtype=float)
permit = pd.Series(dtype=float)
t10y2y = pd.Series(dtype=float)
cpi = pd.Series(dtype=float)
core_cpi = pd.Series(dtype=float)
pce = pd.Series(dtype=float)
fedfunds = pd.Series(dtype=float)


def _load_data() -> None:
    """Fetch all required FRED series.  Called once on import."""
    global DATA_ERROR, yc_df, spread_data, usrec
    global umcsent, icsa, permit, t10y2y
    global cpi, core_cpi, pce, fedfunds

    if not FRED_API_KEY:
        DATA_ERROR = (
            "⚠️ FRED_API_KEY is not set.  "
            "Export it as an environment variable before running the app.\n\n"
            "  export FRED_API_KEY=your_key_here\n\n"
            "Get a free key → https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        return

    try:
        # Yield-curve maturities
        yc_series = get_multiple(list(YIELD_CURVE_SERIES.keys()))
        yc_df = build_yield_curve_df(yc_series)

        # Spreads
        spread_data = {
            label: get_series(sid)
            for sid, label in SPREAD_SERIES.items()
        }

        # Recession indicator
        usrec = get_series(RECESSION_SERIES)

        # Leading indicators
        umcsent = get_series("UMCSENT")
        icsa = get_series("ICSA")
        permit = get_series("PERMIT")
        t10y2y = get_series("T10Y2Y")

        # Inflation & policy
        cpi = get_series("CPIAUCSL")
        core_cpi = get_series("CPILFESL")
        pce = get_series("PCEPI")
        fedfunds = get_series("FEDFUNDS")

    except Exception as exc:
        DATA_ERROR = f"Failed to load FRED data: {exc}"
        logger.exception("Data load error")


_load_data()

# ---------------------------------------------------------------------------
# Helper: build available historical-date options for yield-curve overlay
# ---------------------------------------------------------------------------
HISTORICAL_OFFSETS = {
    "6 Months Ago": timedelta(days=182),
    "1 Year Ago": timedelta(days=365),
    "2 Years Ago": timedelta(days=730),
    "5 Years Ago": timedelta(days=1825),
}


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _error_banner(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="danger", className="m-4", style={"whiteSpace": "pre-wrap"})


def _build_layout() -> dbc.Container:
    if DATA_ERROR:
        return dbc.Container([
            html.H2("Economic Indicators & Yield Curve", className="mt-3"),
            _error_banner(DATA_ERROR),
        ], fluid=True)

    return dbc.Container([
        # Header
        dbc.Row(dbc.Col(html.H2("Economic Indicators & Yield Curve Dashboard",
                                 className="mt-3 mb-2"))),

        # Tabs
        dbc.Tabs(id="main-tabs", active_tab="tab-yc", children=[
            dbc.Tab(label="Yield Curve", tab_id="tab-yc"),
            dbc.Tab(label="Spreads & Recession", tab_id="tab-spreads"),
            dbc.Tab(label="Leading Indicators", tab_id="tab-indicators"),
            dbc.Tab(label="Inflation & Policy", tab_id="tab-inflation"),
        ], className="mb-3"),

        # Tab content placeholder
        html.Div(id="tab-content"),
    ], fluid=True)


app.layout = _build_layout


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab"),
)
def render_tab(active_tab: str):
    """Switch visible content based on the selected tab."""
    if DATA_ERROR:
        return _error_banner(DATA_ERROR)

    try:
        if active_tab == "tab-yc":
            return _yield_curve_tab()
        elif active_tab == "tab-spreads":
            return _spreads_tab()
        elif active_tab == "tab-indicators":
            return _indicators_tab()
        elif active_tab == "tab-inflation":
            return _inflation_tab()
    except Exception as exc:
        return _error_banner(f"Error rendering tab: {exc}")

    return html.P("Select a tab above.")


# -- Yield Curve tab content builder -----------------------------------------

def _yield_curve_tab():
    """Return the layout for the Yield Curve tab, including a dropdown for
    historical curve overlays and both the snapshot & heatmap charts."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Overlay historical curves:", className="fw-bold"),
                dcc.Dropdown(
                    id="yc-overlay-dropdown",
                    options=[{"label": k, "value": k} for k in HISTORICAL_OFFSETS],
                    multi=True,
                    placeholder="Select dates to overlay…",
                ),
            ], md=6),
        ], className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(id="yc-snapshot-chart"))),
        dbc.Row(dbc.Col(dcc.Graph(
            id="yc-heatmap-chart",
            figure=yield_curve_heatmap_figure(yc_df),
        ))),
    ])


@app.callback(
    Output("yc-snapshot-chart", "figure"),
    Input("yc-overlay-dropdown", "value"),
)
def update_yc_snapshot(selected_overlays):
    """Rebuild the yield-curve snapshot whenever the user changes overlays."""
    curves: dict[str, pd.Series] = {}

    # Current curve (latest date)
    today_label = f"Latest ({yc_df.index[-1].strftime('%Y-%m-%d')})"
    curves[today_label] = yield_curve_snapshot(yc_df)

    if selected_overlays:
        for label in selected_overlays:
            offset = HISTORICAL_OFFSETS.get(label)
            if offset is None:
                continue
            target_date = date.today() - offset
            try:
                curves[label] = yield_curve_snapshot(yc_df, as_of=str(target_date))
            except Exception:
                pass  # Skip if date is outside data range

    return yield_curve_snapshot_figure(curves)


# -- Spreads tab -------------------------------------------------------------

def _spreads_tab():
    fig = spread_monitor_figure(spread_data, usrec)
    return dbc.Row(dbc.Col(dcc.Graph(figure=fig)))


# -- Leading Indicators tab --------------------------------------------------

def _indicators_tab():
    fig = leading_indicators_figure(umcsent, icsa, permit, t10y2y, usrec)
    return dbc.Row(dbc.Col(dcc.Graph(figure=fig)))


# -- Inflation & Policy tab --------------------------------------------------

def _inflation_tab():
    fig = inflation_policy_figure(cpi, core_cpi, pce, fedfunds, usrec)
    return dbc.Row(dbc.Col(dcc.Graph(figure=fig)))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
