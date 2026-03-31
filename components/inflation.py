"""
components/inflation.py — Inflation Monitor & Fed Policy charts.

Top chart:  CPI YoY%, Core CPI YoY%, PCE YoY% with 2% target line.
Bottom chart: Fed Funds Rate step chart with recession shading.
Dark terminal aesthetic.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    CHART_LAYOUT_DEFAULTS, BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_ACCENT,
)
from transforms import recession_periods, yoy_pct_change


def inflation_policy_figure(
    cpi: pd.Series,
    core_cpi: pd.Series,
    pce: pd.Series,
    fedfunds: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    """
    Two-row figure: inflation on top, Fed Funds rate below.
    """
    # --- Compute YoY % changes -----------------------------------------------
    cpi_yoy = yoy_pct_change(cpi) if not cpi.empty else cpi
    core_yoy = yoy_pct_change(core_cpi) if not core_cpi.empty else core_cpi
    pce_yoy = yoy_pct_change(pce) if not pce.empty else pce

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["▸ INFLATION — YOY %", "▸ EFFECTIVE FEDERAL FUNDS RATE"],
        vertical_spacing=0.14,
        row_heights=[0.55, 0.45],
    )

    rec_periods = recession_periods(usrec) if not usrec.empty else []

    def _shade(row: int) -> None:
        for start, end in rec_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below", line_width=0,
                row=row, col=1,
            )

    # --- Inflation panel (row 1) ---------------------------------------------
    for series, name, color in [
        (cpi_yoy,  "CPI YoY%",      COLORS[0]),
        (core_yoy, "Core CPI YoY%", COLORS[1]),
        (pce_yoy,  "PCE YoY%",      COLORS[2]),
    ]:
        if series.empty:
            continue
        # Glow
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", line=dict(color=color, width=5),
            opacity=0.1, showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
        # Main
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=name,
            line=dict(color=color, width=1.8),
        ), row=1, col=1)

    # Fed 2% inflation target — pulsing reference
    fig.add_hline(
        y=2.0, line_dash="dash", line_color="#ff3366", line_width=1.5,
        annotation_text="2% TARGET",
        annotation_font=dict(color="#ff3366", size=10),
        annotation_position="bottom right",
        row=1, col=1,
    )
    _shade(1)

    # --- Fed Funds panel (row 2) ---------------------------------------------
    if not fedfunds.empty:
        # Glow
        fig.add_trace(go.Scatter(
            x=fedfunds.index, y=fedfunds.values,
            mode="lines", line=dict(color=COLORS[4], width=6, shape="hv"),
            opacity=0.12, showlegend=False, hoverinfo="skip",
        ), row=2, col=1)
        # Main step line
        fig.add_trace(go.Scatter(
            x=fedfunds.index, y=fedfunds.values,
            mode="lines", name="Fed Funds Rate",
            line=dict(color=COLORS[4], width=2, shape="hv"),
        ), row=2, col=1)
    _shade(2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=CHART_LAYOUT_DEFAULTS["font"],
        title=dict(text="◆ INFLATION & MONETARY POLICY", font=dict(color=TEXT_ACCENT, size=16)),
        height=750,
        margin=dict(t=90, b=50, l=60, r=30),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11),
        ),
    )

    # Style axes
    for suffix in ["", "2"]:
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR),
        })

    fig.update_yaxes(title_text="YoY %", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=2, col=1)

    # Style subplot titles
    for ann in fig.layout.annotations:
        ann.font = dict(color=TEXT_ACCENT, size=12)

    return fig
