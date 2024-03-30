#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from .....thirdparty.data import *
from .....thirdparty.maths import *
from .....thirdparty.plots import *
from .....thirdparty.types import *

from .....setup import config
from .....core.log import *
from .....models.fitting import *
from .....models.polynomials import *
from .....models.user import *
from .....queries.scientific import *
from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_output_time_plot',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP output time-plot', level=LOG_LEVELS.INFO)
def step_output_time_plot(
    data: pd.DataFrame,
    info: FittedInfoNormalisation,
    poly: Poly[float],
    fitinfo_trig: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    special: dict[str, SpecialPointsConfig],
    quantity: str,
    symb: str,
    plot_name: str,
    plot_label: str,
    cfg_output: UserOutput,
    N: int = 1000,
) -> pgo.Figure:
    '''
    Creates Time-Series plot for a quantity including:

    - subplots for 0th, 1st, 2nd derivatives;
    - data series (0th derivative only);
    - trig-fitted series (0th derivative only);
    - poly-fitted series (all derivatives);
    - special points (all derivatives).
    '''
    cv = output_conversions(cfg_output.quantities, units=config.UNITS)
    units = output_units(cfg_output.quantities)
    T = info.period

    # compute series for fitted curves
    time, data_poly, specials = compute_fitted_curves_poly(info=info, poly=poly, special=special, n_der=2, N=N)  # fmt: skip

    # setup plot
    fig = setup_plot(name=plot_name, quantity=quantity, symb=symb, T=T, specials=specials, cfg=cfg_output, cv=cv, units=units)  # fmt: skip

    # plot data points
    for subplot in plot_data_vs_time(data, quantity=quantity, cv=cv, units=units):
        fig.append_trace(subplot, row=1, col=1)

    # plot trig fit
    for subplot in plot_trig_fit(fitinfo_trig, info=info, quantity=quantity, N=N, cv=cv, units=units):
        fig.append_trace(subplot, row=1, col=1)

    # plot poly fit
    names = [f'{quantity.title()} [fit]', f'(d/dt){symb} [fit]', f'(d/dt)²{symb} [fit]']
    quantities = [quantity, f'd[1,t]{quantity}[fit]', f'd[2,t]{quantity}[fit]']
    for k, (name, quantity_, values, special_) in enumerate(zip(names, quantities, data_poly, specials)):
        for subplot in plot_poly_fit(fig, name=name, quantity=quantity_, time=time, values=values, special=special_, showlegend=k == 0, cv=cv, units=units):  # fmt: skip
            fig.append_trace(subplot, row=k + 1, col=1)

    # save plot
    path = cfg_output.plot.path.root
    if path is not None:
        path = path.format(label=plot_label, kind=f'{quantity}-time')
        save_image(fig=fig, path=path)

    return fig


# ----------------------------------------------------------------
# SECONDARY METHODS
# ----------------------------------------------------------------


def setup_plot(
    name: str,
    quantity: str,
    symb: str,
    T: float,
    specials: list[Any],
    cfg: UserOutput,
    cv: dict[str, float],
    units: dict[str, str],
) -> pgo.Figure:
    '''
    Initialises plot.
    '''
    cfg_font = cfg.plot.font

    # set up plots
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'Time series for {name} (fitted, single cycle)'
            for name in [f'{quantity.title()}', f'(d/dt){symb}', f'(d/dt)²{symb}']
        ],
    )

    fig.update_layout(
        width=480,
        height=720,
        margin=dict(l=40, r=40, t=60, b=40),
        title=dict(
            text=name,
            font=dict(
                family=cfg_font.family,
                size=cfg_font.size_title,
            ),
        ),
        font=dict(
            family=cfg_font.family,
            size=cfg_font.size,
            color='hsla(0, 100%, 0%, 1)',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        showlegend=cfg.plot.legend,
        legend=dict(
            title='Series/Points',
            font=dict(
                family=cfg_font.family,
                size=cfg_font.size_legend,
            ),
        ),
    )

    opt = dict(
        linecolor='black',
        mirror=True,  # adds border on right/top too
        ticks='outside',
        showgrid=True,
        visible=True,
        # range=[0, None], # FIXME: does not work!
    )

    t_sp = np.unique([0, T] + [point.time for _, point in specials[0].items()])
    t_sp = cv['time'] * t_sp  # convert units

    for row in range(1, 3 + 1):
        fig.update_xaxes(
            title=f'Time    ({units["time"]})',
            rangemode='tozero',
            **opt,
            row=row,
            col=1,
            range=[-0.1 * cv['time'] * T + 0, 1.1 * cv['time'] * T],
            tickvals=t_sp,
            ticktext=[f'{t:.3g}' for t in t_sp],
            tickangle=90,
        )

    for row, key, name in [
        (1, quantity, quantity.title()),
        (2, f'd[1,t]{quantity}[fit]', f'{symb}´(t)'),
        (3, f'd[2,t]{quantity}[fit]', f'{symb}´´(t)'),
    ]:
        unit = units[key]
        fig.update_yaxes(title=f'{name}    ({unit})', rangemode='normal', **opt, row=row, col=1)

    return fig


def plot_data_vs_time(
    data: pd.DataFrame,
    quantity: str,
    cv: dict[str, float],
    units: dict[str, str],
):
    '''
    Plots raw time series (collapsed onto one period).
    '''
    yield from add_plot_time_series(
        name=f'{quantity.title()} [data]',
        text=f'{quantity}',
        time=cv['time'] * data['time'],
        values=cv[quantity] * data[quantity],
        mode='markers',
        marker=dict(
            size=2,
            color='hsla(0, 100%, 0%, 0.5)',
            symbol='cross',
        ),
        showlegend=True,
    )


def plot_poly_fit(
    fig: pgo.Figure,
    name: str,
    quantity: str,
    time: NDArray[np.float64],
    values: NDArray[np.float64],
    showlegend: bool,
    special: dict[str, SpecialPointsConfig],
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots poly-fitted curve + special points.
    '''
    yield from add_plot_time_series(
        name=name,
        time=time,
        values=values,
        cv_time=cv['time'],
        cv_value=cv[quantity],
        showlegend=showlegend,
    )
    for key, point in special.items():
        if point.ignore:
            continue
        yield from add_plot_point_plus_vline(
            fig,
            key=key,
            point=point,
            cv_time=cv['time'],
            cv_value=cv[quantity],
            showlegend=showlegend,
        )


def plot_trig_fit(
    fitinfo: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    info: FittedInfoNormalisation,
    quantity: str,
    N: int,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creates subplot for the trig-fitting (if given).
    '''
    fit, _, _ = fitinfo
    if fit is None:
        return

    time_trig, data_trig = compute_fitted_curves_trig(fitinfo, info, usehull=True, N=N)

    yield from add_plot_time_series(
        name=f'{quantity.title()} [trig]',
        time=time_trig,
        values=data_trig,
        cv_time=cv['time'],
        cv_value=cv[quantity],
        mode='markers',
        marker=dict(
            size=3,
            color='hsla(100, 100%, 25%, 0.5)',
        ),
        showlegend=True,
    )
