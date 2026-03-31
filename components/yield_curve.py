"""
components/yield_curve.py — Yield Curve tab charts.

1. Yield Curve Snapshot  — interactive line chart of current curve with
   optional historical overlays.
2. Yield Curve Heatmap   — 2-D heatmap showing yield levels across
   maturities and time.
"""

from __future__ import annotations

import plotly.graph_objects as go

import pandas as pd

from config import MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR


def yield_curve_snapshot_figure(
    curves: dict[str, pd.Series],
) -> go.Figure:
    """
    Build the yield-curve snapshot chart.

    Parameters
    ----------
    curves : dict mapping label (e.g. "Today", "1Y Ago") to a pd.Series
             indexed by maturity label with yield values.

    Returns
    -------
    plotly Figure
    """
    fig = go.Figure()

    for i, (label, curve) in enumerate(curves.items()):
        # Filter to only maturities present in our standard order
        maturities = [m for m in MATURITY_ORDER if m in curve.index]
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines+markers",
            name=label,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            marker=dict(size=6),
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="US Treasury Yield Curve",
        xaxis_title="Maturity",
        yaxis_title="Yield (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    return fig


def yield_curve_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """
    Build a 2-D heatmap: x = date, y = maturity, colour = yield level.

    A diverging colour scale (RdYlGn_r) makes inversions pop visually —
    low yields appear green, high yields red.

    Parameters
    ----------
    df : DataFrame with DatetimeIndex and columns = maturity labels (ordered).
    """
    # Resample to weekly to keep the heatmap performant for multi-year data
    weekly = df.resample("W").last()

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values,
        x=weekly.index,
        y=weekly.columns.tolist(),
        colorscale="RdYlGn_r",
        colorbar=dict(title="Yield %"),
        hoverongaps=False,
    ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Yield Curve Heatmap (Weekly)",
        xaxis_title="Date",
        yaxis_title="Maturity",
        yaxis=dict(categoryorder="array", categoryarray=MATURITY_ORDER),
        margin=dict(t=60, b=40),
    )
    return fig
