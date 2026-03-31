"""
components/yield_curve.py — The Yield Curve, or:
What They're Willing to Pay You to Wait.

The curve is a promise.  Every point is a bet against entropy.
When it inverts, the promise breaks.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import (
    MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_ACCENT,
)

_FONT = dict(
    family="'EB Garamond', Georgia, 'Times New Roman', serif",
    color=TEXT_PRIMARY,
    size=13,
)
_HOVERLABEL = dict(
    bgcolor="#141425",
    font=dict(family="'JetBrains Mono', monospace", color=TEXT_PRIMARY, size=11),
    bordercolor="rgba(200, 168, 78, 0.3)",
)


def yield_curve_snapshot_figure(
    curves: dict[str, pd.Series],
) -> go.Figure:
    """The yield curve snapshot — each historical overlay is a ghost."""
    fig = go.Figure()

    for i, (label, curve) in enumerate(curves.items()):
        maturities = [m for m in MATURITY_ORDER if m in curve.index]
        color = COLORS[i % len(COLORS)]

        # The ghost — a faint echo of the line, like a memory
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines",
            line=dict(color=color, width=10),
            opacity=0.08,
            showlegend=False,
            hoverinfo="skip",
        ))

        # The signal
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2, shape="spline"),
            marker=dict(size=6, symbol="circle",
                        line=dict(width=1.5, color=color)),
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(
            text="<i>The Term Structure of Promises</i>",
            font=dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=18),
        ),
        xaxis=dict(title="Maturity", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(title="Yield (%)", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="'EB Garamond', serif", size=12, color=TEXT_PRIMARY),
        ),
        margin=dict(t=80, b=50, l=60, r=30),
        hovermode="x unified",
    )
    return fig


def yield_curve_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """
    The heatmap — a thermal photograph of promises over time.
    Watch for the cold spots.  That's where the inversions breed.
    """
    weekly = df.resample("W").last() if not df.empty else df

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values if not weekly.empty else [[]],
        x=weekly.index if not weekly.empty else [],
        y=weekly.columns.tolist() if not weekly.empty else [],
        colorscale=[
            [0.0, "#07070d"],       # The void
            [0.15, "#1a1a3e"],      # Deep uncertainty
            [0.3, "#5e9e7e"],       # Institutional green — money
            [0.5, "#c8a84e"],       # Parchment gold — the document
            [0.7, "#c4705a"],       # Terracotta — warming
            [0.85, "#c44"],         # Red — they already know
            [1.0, "#e8d5a3"],       # Bright amber — full signal
        ],
        colorbar=dict(
            title=dict(text="Yield %", font=dict(color=TEXT_PRIMARY, size=11)),
            bgcolor="rgba(0,0,0,0)",
            tickfont=dict(color="#6a6a88", size=10),
        ),
        hoverongaps=False,
    ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(
            text="<i>A Thermal History of What Was Promised</i>",
            font=dict(family="'EB Garamond', serif", color=TEXT_ACCENT, size=18),
        ),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR),
        yaxis=dict(
            title="Maturity",
            categoryorder="array",
            categoryarray=MATURITY_ORDER,
            gridcolor=GRID_COLOR,
        ),
        margin=dict(t=80, b=50, l=60, r=30),
    )
    return fig
