"""
components/yield_curve.py — Yield Curve tab charts.

1. Yield Curve Snapshot  — interactive line chart of current curve with
   optional historical overlays.  Glowing neon lines on dark background.
2. Yield Curve Heatmap   — 2-D heatmap showing yield levels across
   maturities and time.  Thermal-vision aesthetic.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS, CHART_LAYOUT_DEFAULTS


def yield_curve_snapshot_figure(
    curves: dict[str, pd.Series],
) -> go.Figure:
    """
    Build the yield-curve snapshot chart with glowing neon lines.

    Parameters
    ----------
    curves : dict mapping label (e.g. "Today", "1Y Ago") to a pd.Series
             indexed by maturity label with yield values.
    """
    fig = go.Figure()

    for i, (label, curve) in enumerate(curves.items()):
        maturities = [m for m in MATURITY_ORDER if m in curve.index]
        color = COLORS[i % len(COLORS)]

        # Glow effect: wider translucent line behind the main line
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines",
            line=dict(color=color, width=8),
            opacity=0.15,
            showlegend=False,
            hoverinfo="skip",
        ))

        # Main sharp line
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[curve[m] for m in maturities],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5),
            marker=dict(size=7, symbol="diamond", line=dict(width=1, color=color)),
        ))

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        template=PLOTLY_TEMPLATE,
        title="◆ US TREASURY YIELD CURVE",
        xaxis_title="Maturity",
        yaxis_title="Yield (%)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11),
        ),
        margin=dict(t=70, b=50, l=60, r=30),
        hovermode="x unified",
    )
    return fig


def yield_curve_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """
    Build a 2-D heatmap: x = date, y = maturity, colour = yield level.

    Uses a hot thermal colorscale — low yields glow cool blue, high yields
    burn red/white.
    """
    # Resample to weekly to keep the heatmap performant
    weekly = df.resample("W").last()

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values,
        x=weekly.index,
        y=weekly.columns.tolist(),
        colorscale=[
            [0.0, "#0a0a2e"],
            [0.15, "#1a1a6e"],
            [0.3, "#00d4ff"],
            [0.5, "#00ff88"],
            [0.7, "#ffcc00"],
            [0.85, "#ff6b35"],
            [1.0, "#ff3366"],
        ],
        colorbar=dict(
            title="Yield %",
            bgcolor="rgba(0,0,0,0)",
            tickfont=dict(color="#8888aa"),
        ),
        hoverongaps=False,
    ))

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        template=PLOTLY_TEMPLATE,
        title="◆ YIELD CURVE HEATMAP — THERMAL VIEW",
        xaxis_title="Date",
        yaxis_title="Maturity",
        yaxis=dict(
            categoryorder="array", categoryarray=MATURITY_ORDER,
            gridcolor="rgba(255,255,255,0.06)",
        ),
        margin=dict(t=70, b=50, l=60, r=30),
    )
    return fig
