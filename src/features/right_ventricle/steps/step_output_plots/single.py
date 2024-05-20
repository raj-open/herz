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
    interpol_trig: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    special: dict[str, SpecialPointsConfig],
    quantity: str,
    symb: str,
    plot_title: str,
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
    cycles = [0]
    collapse = cfg_output.plot.collapse_cycles
    if not collapse:
        cycles = sorted(np.unique(data['cycle'].to_numpy()))

    # compute series for fitted curves
    time, data_poly, specials = compute_fitted_curves_poly(info=info, poly=poly, quantity=quantity, special=special, n_der=2, N=N, cycles=cycles, cv=cv, units=units)  # fmt: skip

    # setup plot
    fig = setup_plot(title=plot_title, quantity=quantity, symb=symb, T=T, cycles=cycles, specials=specials, cfg=cfg_output, cv=cv, units=units)  # fmt: skip

    # plot data points
    for subplot in plot_data_vs_time(data, info=info, quantity=quantity, collapse=collapse, cv=cv, units=units):
        fig.append_trace(subplot, row=1, col=1)

    # plot interpolated trig fit
    for subplot in plot_interpolated_trig_fit(interpol_trig, info=info, quantity=quantity, cycles=cycles, N=N, cv=cv, units=units):  # fmt: skip
        fig.append_trace(subplot, row=1, col=1)

    # plot poly fit
    names = [f'{quantity.title()} [fit]', f'(d/dt){symb} [fit]', f'(d/dt)²{symb} [fit]']
    quantities = [quantity, f'd[1,t]{quantity}[fit]', f'd[2,t]{quantity}[fit]']
    for k, (name, quantity_, values, special_) in enumerate(zip(names, quantities, data_poly, specials)):
        for subplot in plot_poly_fit(fig, info=info, name=name, quantity=quantity_, time=time, values=values, special=special_, cycles=cycles, showlegend=k == 0, cv=cv, units=units):  # fmt: skip
            fig.append_trace(subplot, row=k + 1, col=1)

    # post setup
    setup_plot_post(fig, quantity=quantity, T=T, cv=cv, units=units)  # fmt: skip

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
    title: str,
    quantity: str,
    symb: str,
    T: float,
    cycles: list[int],
    specials: list[dict[str, SpecialPointsConfig]],
    cfg: UserOutput,
    cv: dict[str, float],
    units: dict[str, str],
) -> pgo.Figure:
    '''
    Initialises plot.
    '''
    cfg_font = cfg.plot.font

    cycle_min = min(cycles)
    cycle_max = max(cycles) + 1
    # N_cyles = cycle_max - cycle_min

    # set up plots
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'Time series for {name} (fitted, single cycle)'
            for name in [f'{quantity.title()}', f'(d/dt){symb}', f'(d/dt)²{symb}']
        ],
        shared_xaxes=True,
    )

    fig.update_layout(
        width=480,
        height=720,
        margin=dict(l=40, r=40, t=60, b=40),
        title=dict(
            text=title,
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

    t_sp = np.asarray([0] + [point.time for _, point in specials[0].items() if not point.ignore] + [T])
    t_sp = np.unique(np.concatenate([k * T + t_sp for k in cycles]))
    t_sp = cv['time'] * t_sp  # convert units

    for row in range(1, 3 + 1):
        fig.update_xaxes(
            title=f'Time    ({units["time"]})',
            rangemode='tozero',
            **opt,
            row=row,
            col=1,
            range=[cv['time'] * (cycle_min - 0.1) * T, cv['time'] * (cycle_min + 1 + 0.1) * T],
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

    fig.update_layout(
        xaxis_showticklabels=True,
        xaxis2_showticklabels=True,
        xaxis3_showticklabels=True,
    )

    return fig


def setup_plot_post(
    fig: pgo.Figure,
    quantity: str,
    T: float,
    cv: dict[str, float],
    units: dict[str, str],
):
    ...
    # FIXME: this places a rangeslider only for one subplot and does not control them simultaneously
    # fig.update_layout(
    #     xaxis_rangeslider_visible=True,
    #     # height=600,
    # )


def plot_data_vs_time(
    data: pd.DataFrame,
    info: FittedInfoNormalisation,
    quantity: str,
    collapse: bool,
    cv: dict[str, float],
    units: dict[str, str],
):
    '''
    Plots raw time series (collapsed onto one period).
    '''
    T = info.period
    time = data['time'] % T
    if not collapse:
        cycles = data['cycle']
        cycles = cycles - min(cycles)
        time = cycles * T + time

    yield from add_plot_time_series(
        name=f'{quantity.title()} [data]',
        text=f'{quantity}',
        time=cv['time'] * time,
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
    info: FittedInfoNormalisation,
    name: str,
    quantity: str,
    time: NDArray[np.float64],
    values: NDArray[np.float64],
    showlegend: bool,
    special: dict[str, SpecialPointsConfig],
    cycles: list[int],
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots poly-fitted curve + special points.
    '''
    T = info.period
    yield from add_plot_time_series(
        name=name,
        time=time,
        values=values,
        showlegend=showlegend,
    )
    for _, point in special.items():
        if point.ignore:
            continue
        yield from add_plot_point_plus_vline(
            fig,
            point=point,
            cycles=cycles,
            T=T,
            cv_time=cv['time'],
            cv_value=cv[quantity],
            showlegend=showlegend,
        )


def plot_interpolated_trig_fit(
    fitinfo: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    info: FittedInfoNormalisation,
    quantity: str,
    cycles: list[int],
    N: int,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creates subplot for the interpolated trig-fitting (if given).
    '''
    fit, _, _ = fitinfo
    if fit is None:
        return

    time, values, _ = compute_fitted_curves_trig(
        fitinfo,
        info,
        usehull=True,
        cycles=cycles,
        N=N,
        cv_time=cv['time'],
        cv_value=cv[quantity],
    )

    yield from add_plot_time_series(
        name=f'{quantity.title()} [trig]',
        time=time,
        values=values,
        mode='lines',
        line=dict(
            width=3,
            color='hsla(100, 100%, 25%, 0.5)',
        ),
        showlegend=True,
    )
