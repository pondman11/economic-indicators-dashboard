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

from config import (
    MATURITY_ORDER, PLOTLY_TEMPLATE, COLORS,
    BG_PRIMARY, BG_SECONDARY, GRID_COLOR, TEXT_PRIMARY, TEXT_ACCENT,
)


# Build chart layout defaults inline (avoids kwarg collisions with
# CHART_LAYOUT_DEFAULTS which contains generic xaxis/yaxis keys).
_FONT = dict(
    family="'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
    color=TEXT_PRIMARY,
    size=12,
)
_HOVERLABEL = dict(
    bgcolor="#1a1a2e",
    font_color=TEXT_PRIMARY,
    bordercolor=TEXT_ACCENT,
)


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
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="◆ US TREASURY YIELD CURVE", font=dict(color=TEXT_ACCENT, size=16)),
        xaxis=dict(title="Maturity", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(title="Yield (%)", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
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
    weekly = df.resample("W").last() if not df.empty else df

    fig = go.Figure(data=go.Heatmap(
        z=weekly.T.values if not weekly.empty else [[]],
        x=weekly.index if not weekly.empty else [],
        y=weekly.columns.tolist() if not weekly.empty else [],
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
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=BG_SECONDARY,
        plot_bgcolor=BG_PRIMARY,
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        title=dict(text="◆ YIELD CURVE HEATMAP — THERMAL VIEW", font=dict(color=TEXT_ACCENT, size=16)),
        xaxis=dict(title="Date", gridcolor=GRID_COLOR),
        yaxis=dict(
            title="Maturity",
            categoryorder="array",
            categoryarray=MATURITY_ORDER,
            gridcolor=GRID_COLOR,
        ),
        margin=dict(t=70, b=50, l=60, r=30),
    )
    return fig
