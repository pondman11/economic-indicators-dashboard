"""
app.py — Economic Indicators & Yield Curve Dashboard.

Clean, minimal, fast.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd

from config import (
    FRED_API_KEY,
    YIELD_CURVE_SERIES,
    SPREAD_SERIES,
    RECESSION_SERIES,
    BG_PRIMARY,
    BG_SECONDARY,
    TEXT_SECONDARY,
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
# App
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Economic Indicators Dashboard",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)
server = app.server

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
DATA_ERROR: str | None = None

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
    global DATA_ERROR, yc_df, spread_data, usrec
    global umcsent, icsa, permit, t10y2y
    global cpi, core_cpi, pce, fedfunds

    if not FRED_API_KEY:
        DATA_ERROR = (
            "FRED_API_KEY is not set.\n\n"
            "1. Get a free key → https://fred.stlouisfed.org/docs/api/api_key.html\n"
            "2. Add to .env: FRED_API_KEY=your_key_here\n"
            "3. Restart the app."
        )
        return

    yc_series = get_multiple(list(YIELD_CURVE_SERIES.keys()), safe=True)
    yc_df = build_yield_curve_df(yc_series)

    spread_data = {
        label: get_series_safe(sid)
        for sid, label in SPREAD_SERIES.items()
    }

    usrec = get_series_safe(RECESSION_SERIES)
    umcsent = get_series_safe("UMCSENT")
    icsa = get_series_safe("ICSA")
    permit = get_series_safe("PERMIT")
    t10y2y = get_series_safe("T10Y2Y")
    cpi = get_series_safe("CPIAUCSL")
    core_cpi = get_series_safe("CPILFESL")
    pce = get_series_safe("PCEPI")
    fedfunds = get_series_safe("FEDFUNDS")

    failures = get_failures()
    if failures:
        logger.warning("Some series unavailable: %s", list(failures.keys()))


_load_data()

# ---------------------------------------------------------------------------
# Historical overlay options — just three clean choices
# ---------------------------------------------------------------------------
HISTORICAL_OPTIONS = [
    {"label": "Current only", "value": "none"},
    {"label": "vs 1 Year Ago", "value": "1y"},
    {"label": "vs 2 Years Ago", "value": "2y"},
    {"label": "vs 5 Years Ago", "value": "5y"},
]

OFFSET_MAP = {
    "1y": ("1 Year Ago", timedelta(days=365)),
    "2y": ("2 Years Ago", timedelta(days=730)),
    "5y": ("5 Years Ago", timedelta(days=1825)),
}


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _failure_banner() -> html.Div | None:
    failures = get_failures()
    if not failures:
        return None
    return dbc.Alert(
        f"Some FRED series unavailable: {', '.join(failures.keys())}. "
        "Charts render with available data. Restart to retry.",
        color="warning",
        className="mx-4 mt-3 mb-0",
        dismissable=True,
    )


def _header() -> html.Div:
    failures = get_failures()
    status_class = "status-dot" if not failures else "status-dot warn"
    status_text = "All feeds live" if not failures else f"{len(failures)} feeds unavailable"

    return html.Div([
        html.Div([
            html.H1("Economic Indicators & Yield Curve"),
            html.Div(
                f"FRED data · 10-year lookback · Updated {date.today().strftime('%b %d, %Y')}",
                className="subtitle",
            ),
        ], className="dashboard-header"),
        html.Div([
            html.Div([
                html.Span(className=status_class),
                html.Span(status_text),
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
        ], style={"backgroundColor": BG_PRIMARY, "minHeight": "100vh"})

    return html.Div([
        _header(),
        _failure_banner(),

        dbc.Tabs(id="main-tabs", active_tab="tab-yc", children=[
            dbc.Tab(label="Yield Curve", tab_id="tab-yc"),
            dbc.Tab(label="Spreads & Recession", tab_id="tab-spreads"),
            dbc.Tab(label="Leading Indicators", tab_id="tab-indicators"),
            dbc.Tab(label="Inflation & Policy", tab_id="tab-inflation"),
        ]),

        html.Div(id="tab-content", className="tab-content-area"),

        html.Div(
            "Data from Federal Reserve Bank of St. Louis (FRED)",
            className="footer-note",
        ),
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
        return dbc.Alert(f"Error: {exc}", color="danger")

    return html.P("Select a tab.", style={"color": TEXT_SECONDARY})


# -- Yield Curve tab ---------------------------------------------------------

def _yield_curve_tab():
    return html.Div([
        # Pill-style radio buttons instead of dropdown
        html.Div([
            html.Div("Compare", className="section-label"),
            html.Div(
                dcc.RadioItems(
                    id="yc-compare-radio",
                    options=HISTORICAL_OPTIONS,
                    value="none",
                    inline=True,
                    className="radio-pills",
                ),
                className="radio-pills-container",
            ),
        ], className="mb-4"),
        dbc.Row(dbc.Col(dcc.Graph(id="yc-snapshot-chart")), className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(
            id="yc-heatmap-chart",
            figure=yield_curve_heatmap_figure(yc_df),
        ))),
    ])


@app.callback(
    Output("yc-snapshot-chart", "figure"),
    Input("yc-compare-radio", "value"),
)
def update_yc_snapshot(compare_value: str):
    curves: dict[str, pd.Series] = {}

    if not yc_df.empty:
        today_label = f"Current ({yc_df.index[-1].strftime('%b %d, %Y')})"
        curves[today_label] = yield_curve_snapshot(yc_df)

        if compare_value and compare_value != "none":
            label, offset = OFFSET_MAP[compare_value]
            target_date = date.today() - offset
            try:
                curves[label] = yield_curve_snapshot(yc_df, as_of=str(target_date))
            except Exception:
                pass

    return yield_curve_snapshot_figure(curves)


def _spreads_tab():
    return dbc.Row(dbc.Col(
        dcc.Graph(figure=spread_monitor_figure(spread_data, usrec))
    ))


def _indicators_tab():
    return dbc.Row(dbc.Col(
        dcc.Graph(figure=leading_indicators_figure(umcsent, icsa, permit, t10y2y, usrec))
    ))


def _inflation_tab():
    return dbc.Row(dbc.Col(
        dcc.Graph(figure=inflation_policy_figure(cpi, core_cpi, pce, fedfunds, usrec))
    ))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
