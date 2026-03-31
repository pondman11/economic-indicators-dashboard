"""
components/inflation.py — Inflation Monitor & Fed Funds Rate.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
)
from transforms import recession_periods, yoy_pct_change

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)
_TITLE_FONT = dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=15, weight=600)
_HOVERLABEL = dict(bgcolor="#ffffff", font_color=TEXT_PRIMARY, bordercolor="#eaedf0")


def inflation_policy_figure(
    cpi: pd.Series,
    core_cpi: pd.Series,
    pce: pd.Series,
    fedfunds: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    cpi_yoy = yoy_pct_change(cpi) if not cpi.empty else cpi
    core_yoy = yoy_pct_change(core_cpi) if not core_cpi.empty else core_cpi
    pce_yoy = yoy_pct_change(pce) if not pce.empty else pce

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Inflation — Year-over-Year %", "Effective Federal Funds Rate"],
        vertical_spacing=0.13,
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

    for series, name, color in [
        (cpi_yoy,  "CPI YoY%",      COLORS[2]),
        (core_yoy, "Core CPI YoY%", COLORS[0]),
        (pce_yoy,  "PCE YoY%",      COLORS[1]),
    ]:
        if series.empty:
            continue
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=name,
            line=dict(color=color, width=1.8),
        ), row=1, col=1)

    # 2% target
    fig.add_hline(
        y=2.0, line_dash="dash", line_color="#d0d3d8", line_width=1,
        annotation_text="2% target",
        annotation_font=dict(size=10, color=TEXT_SECONDARY),
        annotation_position="bottom right",
        row=1, col=1,
    )
    _shade(1)

    if not fedfunds.empty:
        fig.add_trace(go.Scatter(
            x=fedfunds.index, y=fedfunds.values,
            mode="lines", name="Fed Funds Rate",
            line=dict(color=COLORS[6], width=2, shape="hv"),
        ), row=2, col=1)
    _shade(2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_SECONDARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="Inflation & Monetary Policy", font=_TITLE_FONT, x=0, xanchor="left"),
        height=700,
        margin=dict(t=80, b=45, l=55, r=25),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
        ),
    )

    for suffix in ["", "2"]:
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR, linecolor="#eaedf0"),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        })

    fig.update_yaxes(title_text="YoY %", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=2, col=1)

    for ann in fig.layout.annotations:
        ann.font = dict(family="Inter, sans-serif", color=TEXT_SECONDARY, size=12, weight=500)

    return fig
