#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


from typing import Generator

import numpy as np
import pandas as pd

# NOTE: reference https://plotly.com/python/reference
import plotly.graph_objects as pgo

from .....models.fitting import *
from .....models.polynomials import *
from .....queries.fitting import *
from .....thirdparty.maths import *
from .....thirdparty.plots import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "quick_plot",
]

# ----------------------------------------------------------------
# SECONDARY METHODS
# ----------------------------------------------------------------


def quick_plot(
    data: pd.DataFrame,
    infos: list[tuple[FittedInfoNormalisation, tuple[int, int]]],
    fit_poly: FittedInfoPoly,
    quantity: str,
    renormalise: bool = True,
    N: int = 1000,
) -> Generator[pgo.Figure, None, None]:
    info, _ = infos[0]
    if renormalise:
        T = info.period
        q = get_unnormalised_polynomial(fit_poly, info=info)
    else:
        T = 1.0
        q = Poly(coeff=fit_poly.coefficients)

    data = get_unnormalised_data(data, infos, quantity=quantity, renormalise=renormalise)

    dq = q.derivative()
    ddq = dq.derivative()
    time = np.linspace(start=0.0, stop=T, num=N + 1, endpoint=True)

    layout = pgo.Layout(
        width=640,
        height=480,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family="Calibri",
            size=10,
            color="black",
        ),
        plot_bgcolor="hsla(0, 100%, 0%, 0.1)",
        title=dict(
            text="Debug plot",
            x=0.5,
            y=0.95,
            font=dict(size=12),
        ),
        xaxis=dict(
            title="time",
            linecolor="black",
            mirror=True,  # adds border on top too
            ticks="outside",
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # rangemode='tozero',
        ),
        yaxis=dict(
            title=quantity,
            linecolor="black",
            mirror=True,  # adds border on right too
            ticks="outside",
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # autorange='reversed',
            # rangemode='tozero',
        ),
        showlegend=True,
    )

    plot_data = [
        pgo.Scatter(
            name="debug [fit]",
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=q.values(time),
            mode="lines",
            line_shape="spline",
            line=dict(
                width=1,
                color="black",
            ),
            showlegend=True,
        ),
    ]
    if renormalise:
        plot_data.append(
            pgo.Scatter(
                name="debug [data]",
                # NOTE: Ensure that the cycle contains start+end points!
                x=data["time"],
                y=data[quantity],
                mode="markers",
                line_shape="spline",
                marker=dict(
                    size=2,
                    color="black",
                ),
                showlegend=True,
            ),
        )
    yield pgo.Figure(layout=layout, data=plot_data)

    plot_data = [
        pgo.Scatter(
            name="dx/dt [fit]",
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=dq.values(time) / T,
            mode="lines",
            line_shape="spline",
            line=dict(
                width=1,
                color="black",
            ),
            showlegend=True,
        ),
    ]
    yield pgo.Figure(layout=layout, data=plot_data)

    plot_data = [
        pgo.Scatter(
            name="d²x/dt² [fit]",
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=ddq.values(time) / T**2,
            mode="lines",
            line_shape="spline",
            line=dict(
                width=1,
                color="black",
            ),
            showlegend=True,
        ),
    ]
    yield pgo.Figure(layout=layout, data=plot_data)
    return
