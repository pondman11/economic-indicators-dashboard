"""
components/inflation.py — Inflation Monitor & Fed Policy charts.

Top chart:  CPI YoY%, Core CPI YoY%, PCE YoY% with a 2% Fed target line.
Bottom chart: Effective Federal Funds Rate (step line) with recession shading.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import PLOTLY_TEMPLATE, COLORS, RECESSION_FILL_COLOR
from transforms import recession_periods, yoy_pct_change


def inflation_policy_figure(
    cpi: pd.Series,
    core_cpi: pd.Series,
    pce: pd.Series,
    fedfunds: pd.Series,
    usrec: pd.Series,
) -> go.Figure:
    """
    Build a two-row figure: inflation comparison on top, Fed Funds rate below.

    Parameters
    ----------
    cpi       : CPI for All Urban Consumers (CPIAUCSL), monthly levels.
    core_cpi  : Core CPI less food & energy (CPILFESL), monthly levels.
    pce       : PCE Price Index (PCEPI), monthly levels.
    fedfunds  : Effective Federal Funds Rate (FEDFUNDS), monthly.
    usrec     : USREC binary indicator.
    """
    # --- Compute YoY % changes -----------------------------------------------
    cpi_yoy = yoy_pct_change(cpi)
    core_yoy = yoy_pct_change(core_cpi)
    pce_yoy = yoy_pct_change(pce)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Inflation — YoY %", "Effective Federal Funds Rate"],
        vertical_spacing=0.12,
        row_heights=[0.55, 0.45],
    )

    rec_periods = recession_periods(usrec)

    def _shade(row: int) -> None:
        for start, end in rec_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=RECESSION_FILL_COLOR,
                layer="below",
                line_width=0,
                row=row, col=1,
            )

    # --- Inflation panel (row 1) ---------------------------------------------
    for series, name, color in [
        (cpi_yoy,  "CPI YoY%",      COLORS[0]),
        (core_yoy, "Core CPI YoY%", COLORS[1]),
        (pce_yoy,  "PCE YoY%",      COLORS[2]),
    ]:
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            mode="lines", name=name,
            line=dict(color=color, width=1.5),
        ), row=1, col=1)

    # Fed 2% inflation target
    fig.add_hline(
        y=2.0, line_dash="dash", line_color="red", line_width=1,
        annotation_text="2% Target", annotation_position="bottom right",
        row=1, col=1,
    )
    _shade(1)

    # --- Fed Funds panel (row 2) ---------------------------------------------
    fig.add_trace(go.Scatter(
        x=fedfunds.index, y=fedfunds.values,
        mode="lines",
        name="Fed Funds Rate",
        line=dict(color=COLORS[4], width=2, shape="hv"),  # step line
    ), row=2, col=1)
    _shade(2)

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Inflation & Monetary Policy",
        height=700,
        margin=dict(t=80, b=40),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(title_text="YoY %", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=2, col=1)

    return fig
