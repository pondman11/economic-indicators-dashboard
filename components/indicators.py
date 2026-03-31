"""
components/indicators.py — Leading Indicators panel (2×2 grid).

Each sub-chart displays one leading indicator with recession shading.
Dark terminal aesthetic with neon accent lines.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    CHART_LAYOUT_DEFAULTS, BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_ACCENT,
)
from transforms import recession_periods, rolling_mean


def leading_indicators_figure(
    umcsent: pd.Series,
    icsa: pd.Series,
    permit: pd.Series,
    t10y2y: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    """
    Build a 2×2 grid of leading-indicator line charts with recession shading.
    """
    # Compute 4-week moving average of initial claims
    icsa_ma = rolling_mean(icsa, window=4) if not icsa.empty else icsa

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "▸ CONSUMER SENTIMENT",
            "▸ INITIAL CLAIMS (4-WK MA)",
            "▸ BUILDING PERMITS",
            "▸ 10Y − 2Y SPREAD",
        ],
        vertical_spacing=0.14,
        horizontal_spacing=0.08,
    )

    rec_periods = recession_periods(usrec) if not usrec.empty else []

    def _shade(row: int, col: int) -> None:
        for start, end in rec_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below", line_width=0,
                row=row, col=col,
            )

    # --- Consumer Sentiment ---------------------------------------------------
    if not umcsent.empty:
        fig.add_trace(go.Scatter(
            x=umcsent.index, y=umcsent.values,
            mode="lines", name="Sentiment",
            line=dict(color=COLORS[0], width=1.8),
            showlegend=False,
        ), row=1, col=1)
    _shade(1, 1)

    # --- Initial Claims (4-wk MA) --------------------------------------------
    if not icsa_ma.empty:
        fig.add_trace(go.Scatter(
            x=icsa_ma.index, y=icsa_ma.values,
            mode="lines", name="Claims (4-Wk MA)",
            line=dict(color=COLORS[1], width=1.8),
            showlegend=False,
        ), row=1, col=2)
    _shade(1, 2)

    # --- Building Permits -----------------------------------------------------
    if not permit.empty:
        fig.add_trace(go.Scatter(
            x=permit.index, y=permit.values,
            mode="lines", name="Permits",
            line=dict(color=COLORS[2], width=1.8),
            showlegend=False,
        ), row=2, col=1)
    _shade(2, 1)

    # --- 10Y − 2Y Spread -----------------------------------------------------
    if not t10y2y.empty:
        fig.add_trace(go.Scatter(
            x=t10y2y.index, y=t10y2y.values,
            mode="lines", name="10Y−2Y",
            line=dict(color=COLORS[3], width=1.8),
            showlegend=False,
        ), row=2, col=2)
    fig.add_hline(
        y=0, line_dash="dash", line_color="#ff3366", line_width=1,
        row=2, col=2,
    )
    _shade(2, 2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=CHART_LAYOUT_DEFAULTS["font"],
        title=dict(text="◆ LEADING ECONOMIC INDICATORS", font=dict(color=TEXT_ACCENT, size=16)),
        height=650,
        margin=dict(t=90, b=50, l=60, r=30),
        hovermode="x unified",
    )

    # Style all subplot axes
    for i in range(1, 5):
        suffix = "" if i == 1 else str(i)
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR),
        })

    # Style subplot titles
    for ann in fig.layout.annotations:
        ann.font = dict(color=TEXT_ACCENT, size=12)

    return fig
