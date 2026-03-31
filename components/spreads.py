"""
components/spreads.py — Spread Monitor with recession shading.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
)
from transforms import recession_periods

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)
_TITLE_FONT = dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=15, weight=600)
_HOVERLABEL = dict(bgcolor="#ffffff", font_color=TEXT_PRIMARY, bordercolor="#eaedf0")


def spread_monitor_figure(
    spreads: dict[str, pd.Series],
    usrec: pd.Series,
) -> go.Figure:
    fig = go.Figure()

    # Recession shading
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

    # Inversion threshold
    fig.add_hline(
        y=0, line_dash="dash", line_color="#d0d3d8", line_width=1,
        annotation_text="Inversion threshold",
        annotation_font=dict(size=10, color=TEXT_SECONDARY),
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_SECONDARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="Treasury Yield Spreads", font=_TITLE_FONT, x=0, xanchor="left"),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        yaxis=dict(title="Spread (%)", gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
        ),
        margin=dict(t=60, b=45, l=55, r=25),
        hovermode="x unified",
    )
    return fig
