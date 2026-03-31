"""
components/spreads.py — Spread Monitor with recession shading.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_CHART, BG_SECONDARY, GRID_COLOR, AXIS_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY,
)
from transforms import recession_periods

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)
_HOVERLABEL = dict(bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY, bordercolor=AXIS_COLOR)


def spread_monitor_figure(
    spreads: dict[str, pd.Series],
    usrec: pd.Series,
) -> go.Figure:
    fig = go.Figure()

    if not usrec.empty:
        for start, end in recession_periods(usrec):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below", line_width=0,
            )

    for i, (label, series) in enumerate(spreads.items()):
        if series.empty:
            continue
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=label,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))

    fig.add_hline(
        y=0, line_dash="dash", line_color="#30363d", line_width=1,
        annotation_text="Inversion threshold",
        annotation_font=dict(size=10, color=TEXT_SECONDARY),
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_CHART,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="Treasury Yield Spreads", font=dict(size=15, color=TEXT_PRIMARY),
                   x=0.01, xanchor="left", pad=dict(b=15)),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        yaxis=dict(title="Spread (%)", gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.06, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
        ),
        margin=dict(t=80, b=50, l=60, r=30),
        hovermode="x unified",
    )
    return fig
