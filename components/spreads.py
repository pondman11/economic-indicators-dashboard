"""
components/spreads.py — Spread Monitor with recession shading.

Neon lines on dark background with ominous red recession zones.
Zero-line inversion threshold glows like a warning.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR, CHART_LAYOUT_DEFAULTS
from transforms import recession_periods


def spread_monitor_figure(
    spreads: dict[str, pd.Series],
    usrec: pd.Series,
) -> go.Figure:
    """
    Build the spread monitor chart.

    Parameters
    ----------
    spreads : dict mapping display label → pd.Series of spread values.
    usrec   : USREC binary series for recession shading.
    """
    fig = go.Figure()

    # --- Recession shading — ominous red zones --------------------------------
    if not usrec.empty:
        for start, end in recession_periods(usrec):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below",
                line_width=0,
            )

    # --- Spread lines with glow effect ----------------------------------------
    for i, (label, series) in enumerate(spreads.items()):
        if series.empty:
            continue
        color = COLORS[i % len(COLORS)]

        # Glow
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", line=dict(color=color, width=6),
            opacity=0.12, showlegend=False, hoverinfo="skip",
        ))
        # Main line
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=label,
            line=dict(color=color, width=2),
        ))

    # --- Zero reference line — inversion threshold ----------------------------
    fig.add_hline(
        y=0, line_dash="dash", line_color="#ff3366", line_width=1.5,
        annotation_text="⚠ INVERSION",
        annotation_font=dict(color="#ff3366", size=11),
        annotation_position="bottom right",
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        template=PLOTLY_TEMPLATE,
        title="◆ TREASURY YIELD SPREADS — RECESSION MONITOR",
        xaxis_title="Date",
        yaxis_title="Spread (%)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11),
        ),
        margin=dict(t=70, b=50, l=60, r=30),
        hovermode="x unified",
    )
    return fig
