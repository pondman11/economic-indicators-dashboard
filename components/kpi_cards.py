"""
components/kpi_cards.py — KPI metric cards and news sidebar for each tab.

Generates compact stat cards showing current values, changes, and status.
Also builds a news feed panel with clickable headlines.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
from dash import html
import dash_bootstrap_components as dbc

from config import TEXT_PRIMARY, TEXT_SECONDARY, BG_SECONDARY, AXIS_COLOR
from news_client import fetch_news, NewsItem


# ---------------------------------------------------------------------------
# Styling constants for cards
# ---------------------------------------------------------------------------
CARD_STYLE = {
    "backgroundColor": "#0d1117",
    "border": "1px solid #21262d",
    "borderRadius": "8px",
    "padding": "1rem 1.25rem",
    "minWidth": "160px",
}

METRIC_STYLE = {
    "fontSize": "1.5rem",
    "fontWeight": "600",
    "color": TEXT_PRIMARY,
    "margin": "0",
    "lineHeight": "1.2",
}

LABEL_STYLE = {
    "fontSize": "0.7rem",
    "fontWeight": "600",
    "color": TEXT_SECONDARY,
    "letterSpacing": "0.04em",
    "textTransform": "uppercase",
    "marginBottom": "0.3rem",
}

CHANGE_UP = {"fontSize": "0.75rem", "color": "#3fb950", "margin": "0"}
CHANGE_DOWN = {"fontSize": "0.75rem", "color": "#f85149", "margin": "0"}
CHANGE_NEUTRAL = {"fontSize": "0.75rem", "color": TEXT_SECONDARY, "margin": "0"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _latest_value(series: pd.Series, decimals: int = 2) -> str:
    """Get the most recent non-NaN value, formatted."""
    if series.empty:
        return "N/A"
    val = series.dropna().iloc[-1]
    return f"{val:.{decimals}f}"


def _latest_float(series: pd.Series) -> Optional[float]:
    if series.empty:
        return None
    return float(series.dropna().iloc[-1])


def _change_text(current: Optional[float], previous: Optional[float], suffix: str = "") -> html.P:
    """Format a change indicator (up/down arrow + value)."""
    if current is None or previous is None:
        return html.P("--", style=CHANGE_NEUTRAL)
    diff = current - previous
    if abs(diff) < 0.005:
        return html.P(f"  {diff:+.2f}{suffix}", style=CHANGE_NEUTRAL)
    style = CHANGE_UP if diff > 0 else CHANGE_DOWN
    arrow = "▲" if diff > 0 else "▼"
    return html.P(f"{arrow} {diff:+.2f}{suffix}", style=style)


def _period_ago_value(series: pd.Series, months_back: int = 1) -> Optional[float]:
    """Get a value approximately N months ago."""
    if series.empty:
        return None
    s = series.dropna()
    if len(s) < 2:
        return None
    target = s.index[-1] - pd.DateOffset(months=months_back)
    idx = s.index.get_indexer([target], method="nearest")
    if idx[0] >= 0:
        return float(s.iloc[idx[0]])
    return None


def _kpi_card(label: str, value: str, change_el: html.P = None) -> html.Div:
    """Single KPI card."""
    children = [
        html.P(label, style=LABEL_STYLE),
        html.P(value, style=METRIC_STYLE),
    ]
    if change_el is not None:
        children.append(change_el)
    return html.Div(children, style=CARD_STYLE)


# ---------------------------------------------------------------------------
# KPI rows per tab
# ---------------------------------------------------------------------------

def yield_curve_kpis(
    yc_df: pd.DataFrame,
    t10y2y: pd.Series,
) -> html.Div:
    """KPIs: 10Y rate, 2Y rate, 10Y-2Y spread, curve status."""
    rate_10y = _latest_value(yc_df.get("10Y", pd.Series(dtype=float)))
    rate_2y = _latest_value(yc_df.get("2Y", pd.Series(dtype=float)))
    spread_val = _latest_float(t10y2y)

    # Determine curve status
    if spread_val is not None:
        if spread_val < 0:
            status = "Inverted"
            status_color = "#f85149"
        elif spread_val < 0.25:
            status = "Flattening"
            status_color = "#d29922"
        else:
            status = "Normal"
            status_color = "#3fb950"
    else:
        status = "N/A"
        status_color = TEXT_SECONDARY

    prev_spread = _period_ago_value(t10y2y, months_back=1)

    return dbc.Row([
        dbc.Col(_kpi_card("10Y Treasury", f"{rate_10y}%"), width="auto"),
        dbc.Col(_kpi_card("2Y Treasury", f"{rate_2y}%"), width="auto"),
        dbc.Col(_kpi_card(
            "10Y - 2Y Spread",
            f"{spread_val:.2f}%" if spread_val is not None else "N/A",
            _change_text(spread_val, prev_spread, " bps") if spread_val else None,
        ), width="auto"),
        dbc.Col(_kpi_card(
            "Curve Status",
            status,
        ).children[0:1] and html.Div([
            html.P("Curve Status", style=LABEL_STYLE),
            html.P(status, style={**METRIC_STYLE, "color": status_color, "fontSize": "1.3rem"}),
        ], style=CARD_STYLE), width="auto"),
    ], className="g-3 mb-4", style={"flexWrap": "nowrap", "overflowX": "auto"})


def spreads_kpis(
    t10y2y: pd.Series,
    t10y3m: pd.Series,
    usrec: pd.Series,
) -> html.Div:
    """KPIs: current 10Y-2Y, 10Y-3M, recession status."""
    val_2y = _latest_float(t10y2y)
    val_3m = _latest_float(t10y3m)
    prev_2y = _period_ago_value(t10y2y, 1)
    prev_3m = _period_ago_value(t10y3m, 1)

    # Recession status from USREC
    rec_status = "N/A"
    rec_color = TEXT_SECONDARY
    if not usrec.empty:
        latest_rec = usrec.dropna().iloc[-1]
        if latest_rec == 1:
            rec_status = "Recession"
            rec_color = "#f85149"
        else:
            rec_status = "Expansion"
            rec_color = "#3fb950"

    return dbc.Row([
        dbc.Col(_kpi_card(
            "10Y - 2Y Spread",
            f"{val_2y:.2f}%" if val_2y is not None else "N/A",
            _change_text(val_2y, prev_2y),
        ), width="auto"),
        dbc.Col(_kpi_card(
            "10Y - 3M Spread",
            f"{val_3m:.2f}%" if val_3m is not None else "N/A",
            _change_text(val_3m, prev_3m),
        ), width="auto"),
        dbc.Col(html.Div([
            html.P("NBER Status", style=LABEL_STYLE),
            html.P(rec_status, style={**METRIC_STYLE, "color": rec_color, "fontSize": "1.3rem"}),
        ], style=CARD_STYLE), width="auto"),
    ], className="g-3 mb-4", style={"flexWrap": "nowrap", "overflowX": "auto"})


def indicators_kpis(
    umcsent: pd.Series,
    icsa: pd.Series,
    permit: pd.Series,
) -> html.Div:
    """KPIs: sentiment, claims, permits with MoM changes."""
    sent_val = _latest_float(umcsent)
    sent_prev = _period_ago_value(umcsent, 1)

    claims_val = _latest_float(icsa)
    claims_prev = _period_ago_value(icsa, 1)

    perm_val = _latest_float(permit)
    perm_prev = _period_ago_value(permit, 1)

    return dbc.Row([
        dbc.Col(_kpi_card(
            "Consumer Sentiment",
            f"{sent_val:.1f}" if sent_val else "N/A",
            _change_text(sent_val, sent_prev),
        ), width="auto"),
        dbc.Col(_kpi_card(
            "Initial Claims (K)",
            f"{claims_val/1000:.0f}K" if claims_val else "N/A",
            _change_text(
                claims_val / 1000 if claims_val else None,
                claims_prev / 1000 if claims_prev else None,
                "K",
            ),
        ), width="auto"),
        dbc.Col(_kpi_card(
            "Building Permits (K)",
            f"{perm_val/1000:.0f}K" if perm_val else "N/A",
            _change_text(
                perm_val / 1000 if perm_val else None,
                perm_prev / 1000 if perm_prev else None,
                "K",
            ),
        ), width="auto"),
    ], className="g-3 mb-4", style={"flexWrap": "nowrap", "overflowX": "auto"})


def inflation_kpis(
    cpi_yoy: Optional[float],
    core_cpi_yoy: Optional[float],
    pce_yoy: Optional[float],
    fedfunds_val: Optional[float],
) -> html.Div:
    """KPIs: CPI YoY, Core CPI YoY, PCE YoY, Fed Funds."""
    def _fmt(v):
        return f"{v:.2f}%" if v is not None else "N/A"

    # Color CPI relative to 2% target
    cpi_color = TEXT_PRIMARY
    if cpi_yoy is not None:
        if cpi_yoy > 3.0:
            cpi_color = "#f85149"
        elif cpi_yoy > 2.5:
            cpi_color = "#d29922"
        elif cpi_yoy <= 2.0:
            cpi_color = "#3fb950"

    return dbc.Row([
        dbc.Col(html.Div([
            html.P("CPI YoY", style=LABEL_STYLE),
            html.P(_fmt(cpi_yoy), style={**METRIC_STYLE, "color": cpi_color}),
        ], style=CARD_STYLE), width="auto"),
        dbc.Col(_kpi_card("Core CPI YoY", _fmt(core_cpi_yoy)), width="auto"),
        dbc.Col(_kpi_card("PCE YoY", _fmt(pce_yoy)), width="auto"),
        dbc.Col(_kpi_card("Fed Funds Rate", _fmt(fedfunds_val)), width="auto"),
    ], className="g-3 mb-4", style={"flexWrap": "nowrap", "overflowX": "auto"})


# ---------------------------------------------------------------------------
# News panel
# ---------------------------------------------------------------------------

NEWS_CARD_STYLE = {
    "backgroundColor": "#0d1117",
    "border": "1px solid #21262d",
    "borderRadius": "8px",
    "padding": "1rem 1.25rem",
}


def news_panel(tab_key: str) -> html.Div:
    """
    Fetches and renders relevant news headlines for a tab.
    Each headline links out to the full article in a new tab.
    """
    items = fetch_news(tab_key, max_results=6)

    if not items:
        return html.Div()

    headlines = []
    for item in items:
        headlines.append(html.Div([
            html.A(
                item.title,
                href=item.url,
                target="_blank",
                style={
                    "color": "#58a6ff",
                    "textDecoration": "none",
                    "fontSize": "0.82rem",
                    "fontWeight": "500",
                    "lineHeight": "1.4",
                },
            ),
            html.Div(
                f"{item.source}  ·  {item.published[:16] if item.published else ''}",
                style={
                    "fontSize": "0.68rem",
                    "color": "#484f58",
                    "marginTop": "2px",
                },
            ),
        ], style={"marginBottom": "0.75rem"}))

    return html.Div([
        html.Div("Related News", style={
            **LABEL_STYLE,
            "marginBottom": "0.75rem",
        }),
        html.Div(headlines, style=NEWS_CARD_STYLE),
    ], className="mt-4")
