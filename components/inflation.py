"""
components/inflation.py — Inflation & Policy, or:
The Slow Unwinding of What a Dollar Meant.

The Fed sets a target of 2%.  This is the official story.
The chart below shows what actually happened.

"Entropy is the figure of Death."
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_ACCENT,
)
from transforms import recession_periods, yoy_pct_change

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
        subplot_titles=[
            "<i>Three Measures of Erosion</i>",
            "<i>The Rate at Which They Respond</i>",
        ],
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

    # --- Inflation (row 1) ---
    for series, name, color in [
        (cpi_yoy,  "CPI YoY%",      COLORS[2]),   # terracotta — erosion
        (core_yoy, "Core CPI YoY%", COLORS[0]),    # gold — the official version
        (pce_yoy,  "PCE YoY%",      COLORS[1]),    # green — the Fed's preferred lie
    ]:
        if series.empty:
            continue
        # Ghost
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", line=dict(color=color, width=6),
            opacity=0.06, showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
        # Signal
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=name,
            line=dict(color=color, width=1.5),
        ), row=1, col=1)

    # The target — a line drawn by committee, held sacred
    fig.add_hline(
        y=2.0, line_dash="dot", line_color="rgba(200, 168, 78, 0.5)", line_width=1,
        annotation_text="the 2% doctrine",
        annotation_font=dict(
            family="'EB Garamond', serif", color="rgba(200, 168, 78, 0.6)",
            size=10,
        ),
        annotation_position="bottom right",
        row=1, col=1,
    )
    _shade(1)

    # --- Fed Funds (row 2) ---
    if not fedfunds.empty:
        # Ghost
        fig.add_trace(go.Scatter(
            x=fedfunds.index, y=fedfunds.values,
            mode="lines", line=dict(color=COLORS[5], width=7, shape="hv"),
            opacity=0.07, showlegend=False, hoverinfo="skip",
        ), row=2, col=1)
        # The staircase — each step a meeting, a vote, a press conference
        fig.add_trace(go.Scatter(
            x=fedfunds.index, y=fedfunds.values,
            mode="lines", name="Fed Funds Rate",
            line=dict(color=COLORS[5], width=2, shape="hv"),
        ), row=2, col=1)
    _shade(2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(
            text="<i>The Entropy of Purchasing Power</i>",
            font=dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=18),
        ),
        height=750,
        margin=dict(t=100, b=50, l=60, r=30),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="'EB Garamond', serif", size=12),
        ),
    )

    for suffix in ["", "2"]:
        fig.update_layout(**{
            f"xaxis{suffix}": dict(gridcolor=GRID_COLOR),
            f"yaxis{suffix}": dict(gridcolor=GRID_COLOR),
        })

    fig.update_yaxes(title_text="YoY %", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=2, col=1)

    for ann in fig.layout.annotations:
        ann.font = dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=12)

    return fig
