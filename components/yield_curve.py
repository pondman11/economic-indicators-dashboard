"""
components/yield_curve.py — Yield Curve charts: snapshot and heatmap.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import (
    MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
)

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)
_TITLE_FONT = dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=15, weight=600)
_HOVERLABEL = dict(bgcolor="#ffffff", font_color=TEXT_PRIMARY, bordercolor="#eaedf0")


def yield_curve_snapshot_figure(curves: dict[str, pd.Series]) -> go.Figure:
    """Current yield curve with optional historical overlays."""
    fig = go.Figure()

    for i, (label, curve) in enumerate(curves.items()):
        maturities = [m for m in MATURITY_ORDER if m in curve.index]
        color = COLORS[i % len(COLORS)]

        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5, shape="spline"),
            marker=dict(size=5),
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_SECONDARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="US Treasury Yield Curve", font=_TITLE_FONT, x=0, xanchor="left"),
        xaxis=dict(title="Maturity", gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        yaxis=dict(title="Yield (%)", gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
        ),
        margin=dict(t=60, b=45, l=55, r=25),
        hovermode="x unified",
    )
    return fig


def yield_curve_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """Yield curve heatmap — time × maturity × yield."""
    weekly = df.resample("W").last() if not df.empty else df

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values if not weekly.empty else [[]],
        x=weekly.index if not weekly.empty else [],
        y=weekly.columns.tolist() if not weekly.empty else [],
        colorscale=[
            [0.0, "#eff6ff"],
            [0.25, "#93c5fd"],
            [0.5, "#3b82f6"],
            [0.75, "#1d4ed8"],
            [1.0, "#1e3a5f"],
        ],
        colorbar=dict(
            title=dict(text="Yield %", font=dict(size=11, color=TEXT_SECONDARY)),
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            thickness=12,
            len=0.6,
        ),
        hoverongaps=False,
        xgap=1,
        ygap=1,
    ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_SECONDARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="Yield Curve Over Time", font=_TITLE_FONT, x=0, xanchor="left"),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR, linecolor="#eaedf0"),
        yaxis=dict(
            title="Maturity",
            categoryorder="array", categoryarray=MATURITY_ORDER,
            gridcolor=GRID_COLOR, linecolor="#eaedf0",
        ),
        margin=dict(t=60, b=45, l=55, r=25),
    )
    return fig
