"""
app.py — Dash application entry point.

Dark terminal aesthetic.  Bloomberg meets cyberpunk.
Assembles layout, wires callbacks, fetches FRED data once at startup.
Gracefully handles missing/failed series instead of crashing.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd

# Project modules
from config import (
    FRED_API_KEY,
    YIELD_CURVE_SERIES,
    SPREAD_SERIES,
    RECESSION_SERIES,
    MATURITY_ORDER,
    BG_PRIMARY,
    BG_SECONDARY,
    TEXT_ACCENT,
)
from fred_client import get_series_safe, get_multiple, get_failures
from transforms import build_yield_curve_df, yield_curve_snapshot
from components.yield_curve import yield_curve_snapshot_figure, yield_curve_heatmap_figure
from components.spreads import spread_monitor_figure
from components.indicators import leading_indicators_figure
from components.inflation import inflation_policy_figure

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App initialisation — DARKSIDE theme
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Economic Indicators & Yield Curve",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)
server = app.server  # Expose for gunicorn / production deploys

# ---------------------------------------------------------------------------
# Pre-fetch data at startup (cached by fred_client)
# ---------------------------------------------------------------------------
DATA_ERROR: str | None = None

# Containers filled during startup — all default to empty so the app
# never crashes even if FRED is down.
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
    """Fetch all required FRED series.  Uses safe fetchers so individual
    series failures don't kill the whole app."""
    global DATA_ERROR, yc_df, spread_data, usrec
    global umcsent, icsa, permit, t10y2y
    global cpi, core_cpi, pce, fedfunds

    if not FRED_API_KEY:
        DATA_ERROR = (
            "⚠ FRED_API_KEY is not set.\n\n"
            "1. Get a free key → https://fred.stlouisfed.org/docs/api/api_key.html\n"
            "2. Add it to your .env file:\n"
            "   FRED_API_KEY=your_key_here\n"
            "3. Restart the app."
        )
        return

    # Yield-curve maturities
    yc_series = get_multiple(list(YIELD_CURVE_SERIES.keys()), safe=True)
    yc_df = build_yield_curve_df(yc_series)

    # Spreads
    spread_data = {
        label: get_series_safe(sid)
        for sid, label in SPREAD_SERIES.items()
    }

    # Recession indicator
    usrec = get_series_safe(RECESSION_SERIES)

    # Leading indicators
    umcsent = get_series_safe("UMCSENT")
    icsa = get_series_safe("ICSA")
    permit = get_series_safe("PERMIT")
    t10y2y = get_series_safe("T10Y2Y")

    # Inflation & policy
    cpi = get_series_safe("CPIAUCSL")
    core_cpi = get_series_safe("CPILFESL")
    pce = get_series_safe("PCEPI")
    fedfunds = get_series_safe("FEDFUNDS")

    failures = get_failures()
    if failures:
        logger.warning("Some FRED series failed to load: %s", list(failures.keys()))


_load_data()

# ---------------------------------------------------------------------------
# Historical overlay options for yield-curve tab
# ---------------------------------------------------------------------------
HISTORICAL_OFFSETS = {
    "6 Months Ago": timedelta(days=182),
    "1 Year Ago": timedelta(days=365),
    "2 Years Ago": timedelta(days=730),
    "5 Years Ago": timedelta(days=1825),
}

# ---------------------------------------------------------------------------
# Layout components
# ---------------------------------------------------------------------------


def _failure_banner() -> html.Div | None:
    """If any FRED series failed, show a subtle warning banner."""
    failures = get_failures()
    if not failures:
        return None
    series_list = ", ".join(failures.keys())
    return dbc.Alert(
        f"⚠ Some series unavailable (FRED server errors): {series_list}. "
        "Charts will render with available data. Restart to retry.",
        color="warning",
        className="m-3 mb-0",
        dismissable=True,
    )


def _header() -> html.Div:
    """Top header bar with title and status indicators."""
    failures = get_failures()
    status_class = "status-dot" if not failures else "status-dot warn"
    status_text = "ALL FEEDS LIVE" if not failures else f"{len(failures)} FEEDS DOWN"

    return html.Div([
        html.Div([
            html.H1("◆ ECONOMIC INDICATORS & YIELD CURVE"),
            html.Div("Real-time FRED data · Treasury · Spreads · Macro · Policy",
                      className="subtitle"),
        ], className="dashboard-header"),
        html.Div([
            html.Div([
                html.Span(className=status_class),
                html.Span(f"FRED: {status_text}"),
            ], className="status-item"),
            html.Div([
                html.Span(className="status-dot"),
                html.Span(f"LOOKBACK: 10Y"),
            ], className="status-item"),
            html.Div([
                html.Span(className="status-dot"),
                html.Span(f"UPDATED: {date.today().isoformat()}"),
            ], className="status-item"),
        ], className="status-bar"),
    ])


def _build_layout() -> html.Div:
    if DATA_ERROR:
        return html.Div([
            _header(),
            dbc.Container([
                dbc.Alert(DATA_ERROR, color="danger", className="m-4",
                          style={"whiteSpace": "pre-wrap"}),
            ], fluid=True),
        ])

    return html.Div([
        _header(),
        _failure_banner(),

        # Tabs
        dbc.Tabs(id="main-tabs", active_tab="tab-yc", children=[
            dbc.Tab(label="YIELD CURVE", tab_id="tab-yc"),
            dbc.Tab(label="SPREADS & RECESSION", tab_id="tab-spreads"),
            dbc.Tab(label="LEADING INDICATORS", tab_id="tab-indicators"),
            dbc.Tab(label="INFLATION & POLICY", tab_id="tab-inflation"),
        ]),

        # Tab content
        html.Div(id="tab-content", className="tab-content-area"),
    ], style={"backgroundColor": BG_PRIMARY, "minHeight": "100vh"})


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
        return dbc.Alert(DATA_ERROR, color="danger", style={"whiteSpace": "pre-wrap"})

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
        logger.exception("Tab render error")
        return dbc.Alert(f"Error rendering tab: {exc}", color="danger")

    return html.P("Select a tab above.", style={"color": "#8888aa"})


# -- Yield Curve tab ---------------------------------------------------------

def _yield_curve_tab():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("OVERLAY HISTORICAL CURVES",
                           style={"color": "#8888aa", "fontSize": "0.75rem",
                                  "fontFamily": "'JetBrains Mono', monospace",
                                  "letterSpacing": "0.06em", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="yc-overlay-dropdown",
                    options=[{"label": k, "value": k} for k in HISTORICAL_OFFSETS],
                    multi=True,
                    placeholder="Select dates to overlay…",
                    style={"backgroundColor": "#1a1a2e", "color": "#e0e0e8"},
                ),
            ], md=6, lg=4),
        ], className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(id="yc-snapshot-chart"))),
        dbc.Row(dbc.Col(dcc.Graph(
            id="yc-heatmap-chart",
            figure=yield_curve_heatmap_figure(yc_df),
        )), className="mt-3"),
    ])


@app.callback(
    Output("yc-snapshot-chart", "figure"),
    Input("yc-overlay-dropdown", "value"),
)
def update_yc_snapshot(selected_overlays):
    curves: dict[str, pd.Series] = {}

    if not yc_df.empty:
        today_label = f"LATEST ({yc_df.index[-1].strftime('%Y-%m-%d')})"
        curves[today_label] = yield_curve_snapshot(yc_df)

        if selected_overlays:
            for label in selected_overlays:
                offset = HISTORICAL_OFFSETS.get(label)
                if offset is None:
                    continue
                target_date = date.today() - offset
                try:
                    curves[label.upper()] = yield_curve_snapshot(yc_df, as_of=str(target_date))
                except Exception:
                    pass

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
