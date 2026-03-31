"""
components/indicators.py — Leading Indicators panel (2×2 grid of charts).

Each sub-chart displays one leading indicator with recession shading:
  1. Consumer Sentiment (UMCSENT)
  2. Initial Jobless Claims — 4-week MA (ICSA)
  3. Building Permits (PERMIT)
  4. 10Y − 2Y Spread (T10Y2Y)
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR
from transforms import recession_periods, rolling_mean


def leading_indicators_figure(
    umcsent: pd.Series,
    icsa: pd.Series,
    permit: pd.Series,
    t10y2y: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    """
    Build a 2×2 grid of leading-indicator line charts, each with recession
    shading.

    Parameters
    ----------
    umcsent : Consumer Sentiment series.
    icsa    : Initial Jobless Claims (raw weekly).
    permit  : Building Permits series.
    t10y2y  : 10Y−2Y spread series.
    usrec   : USREC binary indicator for recession shading.
    """
    # Compute 4-week moving average of initial claims
    icsa_ma = rolling_mean(icsa, window=4)
    icsa_ma.name = "ICSA_4WK_MA"

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Consumer Sentiment (UMCSENT)",
            "Initial Claims — 4-Wk MA (ICSA)",
            "Building Permits (PERMIT)",
            "10Y − 2Y Spread (T10Y2Y)",
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Helper: add recession shading to a specific subplot cell
    rec_periods = recession_periods(usrec)

    def _add_recession_shading(row: int, col: int) -> None:
        for start, end in rec_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below",
                line_width=0,
                row=row, col=col,
            )

    # --- Consumer Sentiment ---------------------------------------------------
    fig.add_trace(go.Scatter(
        x=umcsent.index, y=umcsent.values,
        mode="lines", name="Consumer Sentiment",
        line=dict(color=COLORS[0], width=1.5),
        showlegend=False,
    ), row=1, col=1)
    _add_recession_shading(1, 1)

    # --- Initial Claims (4-wk MA) --------------------------------------------
    fig.add_trace(go.Scatter(
        x=icsa_ma.index, y=icsa_ma.values,
        mode="lines", name="Initial Claims (4-Wk MA)",
        line=dict(color=COLORS[1], width=1.5),
        showlegend=False,
    ), row=1, col=2)
    _add_recession_shading(1, 2)

    # --- Building Permits -----------------------------------------------------
    fig.add_trace(go.Scatter(
        x=permit.index, y=permit.values,
        mode="lines", name="Building Permits",
        line=dict(color=COLORS[2], width=1.5),
        showlegend=False,
    ), row=2, col=1)
    _add_recession_shading(2, 1)

    # --- 10Y − 2Y Spread -----------------------------------------------------
    fig.add_trace(go.Scatter(
        x=t10y2y.index, y=t10y2y.values,
        mode="lines", name="10Y−2Y Spread",
        line=dict(color=COLORS[3], width=1.5),
        showlegend=False,
    ), row=2, col=2)
    # Zero line for inversion reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1,
                  row=2, col=2)
    _add_recession_shading(2, 2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Leading Economic Indicators",
        height=600,
        margin=dict(t=80, b=40),
        hovermode="x unified",
    )
    return fig
