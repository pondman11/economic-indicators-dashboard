"""
components/yield_curve.py — Yield Curve snapshot and heatmap charts.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import (
    MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS,
    BG_CHART, BG_SECONDARY, GRID_COLOR, AXIS_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY,
)

_FONT = dict(family="Inter, -apple-system, sans-serif", color=TEXT_PRIMARY, size=12)
_HOVERLABEL = dict(bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY, bordercolor=AXIS_COLOR)


def yield_curve_snapshot_figure(curves: dict[str, pd.Series]) -> go.Figure:
    """Current yield curve with optional historical comparison."""
    fig = go.Figure()

    for i, (label, curve) in enumerate(curves.items()):
        maturities = [m for m in MATURITY_ORDER if m in curve.index]
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines+markers",
            name=label,
            line=dict(color=COLORS[i % len(COLORS)], width=2.5, shape="spline"),
            marker=dict(size=5),
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_CHART,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="US Treasury Yield Curve", font=dict(size=15, color=TEXT_PRIMARY)),
        xaxis=dict(title="Maturity", gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        yaxis=dict(title="Yield (%)", gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
        ),
        margin=dict(t=55, b=45, l=55, r=25),
        hovermode="x unified",
    )
    return fig


def yield_curve_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """Heatmap: time x maturity x yield. Real heat — cool to hot."""
    weekly = df.resample("W").last() if not df.empty else df

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values if not weekly.empty else [[]],
        x=weekly.index if not weekly.empty else [],
        y=weekly.columns.tolist() if not weekly.empty else [],
        colorscale=[
            [0.0, "#0d1117"],
            [0.15, "#1a3a5c"],
            [0.30, "#2563eb"],
            [0.45, "#39d2c0"],
            [0.60, "#3fb950"],
            [0.75, "#d29922"],
            [0.90, "#f0883e"],
            [1.0, "#f85149"],
        ],
        colorbar=dict(
            title=dict(text="Yield %", font=dict(size=11, color=TEXT_SECONDARY)),
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            thickness=12,
            len=0.6,
        ),
        hoverongaps=False,
        xgap=0.5,
        ygap=1,
    ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_CHART,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="Yield Curve Over Time", font=dict(size=15, color=TEXT_PRIMARY)),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR, linecolor=AXIS_COLOR),
        yaxis=dict(
            title="Maturity",
            categoryorder="array", categoryarray=MATURITY_ORDER,
            gridcolor=GRID_COLOR, linecolor=AXIS_COLOR,
        ),
        margin=dict(t=55, b=45, l=55, r=25),
    )
    return fig
