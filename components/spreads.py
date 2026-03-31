"""
components/spreads.py — Spread Monitor with recession shading.

Full-width line chart of T10Y2Y and T10Y3M with:
  • USREC recession bands in translucent red
  • A horizontal zero line to mark the inversion threshold
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR
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

    # --- Recession shading ---------------------------------------------------
    for start, end in recession_periods(usrec):
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor=RECESSION_FILL_COLOR,
            layer="below",
            line_width=0,
        )

    # --- Spread lines --------------------------------------------------------
    for i, (label, series) in enumerate(spreads.items()):
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name=label,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
        ))

    # --- Zero reference line (inversion threshold) ---------------------------
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1,
                  annotation_text="Inversion", annotation_position="bottom right")

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Treasury Yield Spreads & Recession Indicator",
        xaxis_title="Date",
        yaxis_title="Spread (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    return fig
