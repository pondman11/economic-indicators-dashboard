"""
components/indicators.py — The Leading Indicators, or:
Four Ways of Knowing What's Coming
(None of Them Reliable).

Consumer Sentiment: how the preterite feel.
Initial Claims: how many have been cast out this week.
Building Permits: the faith required to build something.
The Spread: see spreads.py; it follows you here too.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_ACCENT,
)
from transforms import recession_periods, rolling_mean

_FONT = dict(
    family="'EB Garamond', Georgia, serif",
    color=TEXT_PRIMARY,
    size=12,
)


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
            "<i>The Sentiment of the Preterite</i>",
            "<i>The Newly Dispossessed (4-Wk Avg)</i>",
            "<i>Acts of Faith in Concrete</i>",
            "<i>The Spread (It Follows You)</i>",
        ],
        vertical_spacing=0.16,
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

    # Consumer Sentiment — the mood of those not invited to the party
    if not umcsent.empty:
        fig.add_trace(go.Scatter(
            x=umcsent.index, y=umcsent.values,
            mode="lines", name="Sentiment",
            line=dict(color=COLORS[0], width=1.5),
            showlegend=False,
        ), row=1, col=1)
    _shade(1, 1)

    # Initial Claims — each data point is a person
    if not icsa_ma.empty:
        fig.add_trace(go.Scatter(
            x=icsa_ma.index, y=icsa_ma.values,
            mode="lines", name="Claims",
            line=dict(color=COLORS[2], width=1.5),
            showlegend=False,
        ), row=1, col=2)
    _shade(1, 2)

    # Building Permits — optimism denominated in lumber and permits
    if not permit.empty:
        fig.add_trace(go.Scatter(
            x=permit.index, y=permit.values,
            mode="lines", name="Permits",
            line=dict(color=COLORS[1], width=1.5),
            showlegend=False,
        ), row=2, col=1)
    _shade(2, 1)

    # The Spread — again, always
    if not t10y2y.empty:
        fig.add_trace(go.Scatter(
            x=t10y2y.index, y=t10y2y.values,
            mode="lines", name="10Y−2Y",
            line=dict(color=COLORS[3], width=1.5),
            showlegend=False,
        ), row=2, col=2)
    fig.add_hline(
        y=0, line_dash="dot", line_color="rgba(180, 60, 50, 0.5)", line_width=1,
        row=2, col=2,
    )
    _shade(2, 2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        title=dict(
            text="<i>Four Instruments, None of Them Tuned</i>",
            font=dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=18),
        ),
        height=680,
        margin=dict(t=100, b=50, l=60, r=30),
        hovermode="x unified",
    )

    # Style subplot axes
    for i in range(1, 5):
        suffix = "" if i == 1 else str(i)
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR),
        })

    # Subplot titles in Garamond
    for ann in fig.layout.annotations:
        ann.font = dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=12)

    return fig
