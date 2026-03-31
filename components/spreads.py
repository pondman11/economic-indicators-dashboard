"""
components/spreads.py — The Spread Monitor, or:
How Far Apart the Promises Have Drifted.

When the spread goes negative, the yield curve has inverted.
This has preceded every recession since 1955.
Pynchon would note that the pattern recognition itself
is part of the conspiracy.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_ACCENT,
)
from transforms import recession_periods

_FONT = dict(
    family="'EB Garamond', Georgia, serif",
    color=TEXT_PRIMARY,
    size=13,
)
_HOVERLABEL = dict(
    bgcolor="#141425",
    font=dict(family="'JetBrains Mono', monospace", color=TEXT_PRIMARY, size=11),
    bordercolor="rgba(200, 168, 78, 0.3)",
)


def spread_monitor_figure(
    spreads: dict[str, pd.Series],
    usrec: pd.Series,
) -> go.Figure:
    fig = go.Figure()

    # Recession shading — the official record of when They admitted it
    if not usrec.empty:
        for start, end in recession_periods(usrec):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below",
                line_width=0,
            )

    for i, (label, series) in enumerate(spreads.items()):
        if series.empty:
            continue
        color = COLORS[i % len(COLORS)]

        # The echo
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", line=dict(color=color, width=7),
            opacity=0.07, showlegend=False, hoverinfo="skip",
        ))
        # The signal
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=label,
            line=dict(color=color, width=1.8),
        ))

    # The zero line — below this, the promises have inverted
    fig.add_hline(
        y=0, line_dash="dot", line_color="rgba(180, 60, 50, 0.6)", line_width=1,
        annotation_text="inversion",
        annotation_font=dict(
            family="'EB Garamond', serif", color="rgba(180, 60, 50, 0.7)",
            size=11,
        ),
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(
            text="<i>The Distance Between What Is Owed and What Is Believed</i>",
            font=dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=18),
        ),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(title="Spread (%)", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="'EB Garamond', serif", size=12),
        ),
        margin=dict(t=80, b=50, l=60, r=30),
        hovermode="x unified",
    )
    return fig
