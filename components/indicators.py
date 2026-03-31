"""
components/indicators.py — Leading Indicators panel (2x2 grid).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_CHART, BG_SECONDARY, GRID_COLOR, AXIS_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY,
)
from transforms import recession_periods, rolling_mean

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)


def leading_indicators_figure(
    umcsent: pd.Series,
    icsa: pd.Series,
    permit: pd.Series,
    t10y2y: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    icsa_ma = rolling_mean(icsa, window=4) if not icsa.empty else icsa

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Consumer Sentiment",
            "Initial Claims (4-Wk MA)",
            "Building Permits",
            "10Y - 2Y Spread",
        ],
        vertical_spacing=0.13,
        horizontal_spacing=0.07,
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

    if not umcsent.empty:
        fig.add_trace(go.Scatter(
            x=umcsent.index, y=umcsent.values,
            mode="lines", line=dict(color=COLORS[0], width=1.8),
            showlegend=False,
        ), row=1, col=1)
    _shade(1, 1)

    if not icsa_ma.empty:
        fig.add_trace(go.Scatter(
            x=icsa_ma.index, y=icsa_ma.values,
            mode="lines", line=dict(color=COLORS[1], width=1.8),
            showlegend=False,
        ), row=1, col=2)
    _shade(1, 2)

    if not permit.empty:
        fig.add_trace(go.Scatter(
            x=permit.index, y=permit.values,
            mode="lines", line=dict(color=COLORS[4], width=1.8),
            showlegend=False,
        ), row=2, col=1)
    _shade(2, 1)

    if not t10y2y.empty:
        fig.add_trace(go.Scatter(
            x=t10y2y.index, y=t10y2y.values,
            mode="lines", line=dict(color=COLORS[3], width=1.8),
            showlegend=False,
        ), row=2, col=2)
    fig.add_hline(
        y=0, line_dash="dash", line_color="#30363d", line_width=1,
        row=2, col=2,
    )
    _shade(2, 2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_CHART,
        font=_FONT,
        title=dict(text="Leading Economic Indicators", font=dict(size=15, color=TEXT_PRIMARY)),
        height=620,
        margin=dict(t=75, b=45, l=55, r=25),
        hovermode="x unified",
    )

    for i in range(1, 5):
        suffix = "" if i == 1 else str(i)
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        })

    for ann in fig.layout.annotations:
        ann.font = dict(family="Inter, sans-serif", color=TEXT_SECONDARY, size=12)

    return fig
