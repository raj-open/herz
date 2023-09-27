#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.data import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.plots import *
from ..thirdparty.system import *
from ..thirdparty.types import *

from ..setup import config
from ..setup.conversion import *
from ..setup.plots import *
from ..core.utils import *
from ..core.poly import *
from ..models.internal import *
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_output_loop_plot',
    'step_output_time_plot',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_time_plot(
    case: UserCase,
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    points: dict[str, list[float]],
    quantity: str,
    symb: str,
    N: int = 1000,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font
    cfg_markers = get_markers(quantity)

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    # normalise data
    data = get_renormalised_data(data, fitinfos, quantity=quantity)

    # rescale normalised polynomial + points:
    _, info = fitinfos[-1]
    T = info.normalisation.period

    # re-normalise polynomials
    q, points = get_renormalised_polynomial_and_points(info, points)
    q = [cv[quantity] * xx for xx in q]
    dq = get_derivative_coefficients(q)
    ddq = get_derivative_coefficients(dq)

    # extract spltting-time:
    # NOTE: must be computed after renormalisation of points!
    t_split = points.get('split', [0.0])[0]

    # define a time axis for [0, T]:
    shift_times = shift_function_times(t_split=t_split, T=T)
    shift_indices = shift_function_indices(t_split=t_split, T=T)
    time_orig = np.linspace(start=0, stop=T, num=N, endpoint=False)
    time = shift_times(time_orig, strict=False)

    # re-normalise data
    data = get_renormalised_data(data, fitinfos, t_split=t_split, quantity=quantity)

    # re-normalise points
    points = {key: np.asarray(ts) for key, ts in points.items()}
    points_ = [
        {
            key: coordinates_special_points(ts, q, T=T, t_split=t_split)
            for key, ts in points.items()
        },
        {
            key: coordinates_special_points(ts, dq, T=T, t_split=t_split)
            for key, ts in points.items()
        },
        {
            key: coordinates_special_points(ts, ddq, T=T, t_split=t_split)
            for key, ts in points.items()
        },
    ]

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
            font=dict(
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

    t_sp = np.concatenate([[0, t_split, T]] + list(points.values()))
    t_sp = cv['time'] * np.unique(shift_times(t_sp, strict=False))  # convert units

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

    # add series
    add_plot_time_series(
        fig,
        name=f'{quantity.title()} [data]',
        text=f'{quantity}',
        time=cv['time'] * data['time'],
        values=cv[quantity] * data[quantity],
        mode='markers',
        row=1,
        col=1,
        points=[],
        showlegend=True,
        showlegend_points=False,
    )

    add_plot_time_series(
        fig,
        name=f'{quantity.title()} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time_orig, strict=False), *q),
        row=1,
        col=1,
        points=[
            (
                key,
                cv['time'] * ts,
                values,
                cfg_markers.get(key, None),
            )
            for key, (ts, values) in points_[0].items()
        ],
        showlegend=True,
        showlegend_points=True,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt){symb} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time_orig, strict=False), *dq),
        row=2,
        col=1,
        points=[
            (
                key,
                cv['time'] * ts,
                values,
                cfg_markers.get(key, None),
            )
            for key, (ts, values) in points_[1].items()
        ],
        showlegend=False,
        showlegend_points=False,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt)²{symb} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time_orig, strict=False), *ddq),
        row=3,
        col=1,
        points=[
            (
                key,
                cv['time'] * ts,
                values,
                cfg_markers.get(key, None),
            )
            for key, (ts, values) in points_[2].items()
        ],
        showlegend=False,
        showlegend_points=False,
    )

    path = cfg.plot.path.__root__
    if path is not None:
        path = path.format(label=case.label, kind=f'{quantity}-time')
        save_image(fig=fig, path=path)

    return fig


def step_output_loop_plot(
    case: UserCase,
    data_p: pd.DataFrame,
    fitinfos_p: list[tuple[tuple[int, int], FittedInfo]],
    points_p: dict[str, list[float]],
    data_v: pd.DataFrame,
    fitinfos_v: list[tuple[tuple[int, int], FittedInfo]],
    points_v: dict[str, list[float]],
    N: int = 1000,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font
    cfg_markers_p = get_markers('pressure')
    cfg_markers_v = get_markers('volume')

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    _, info_p = fitinfos_p[-1]
    _, info_v = fitinfos_v[-1]
    T_p = info_p.normalisation.period
    T_v = info_v.normalisation.period
    t_split_p = points_p.get('split', [0.0])[0]
    t_split_v = points_v.get('split', [0.0])[0]

    # define a time axis for [0, T]:
    shift_times_p = shift_function_times(t_split=t_split_p, T=T_p)
    shift_times_v = shift_function_times(t_split=t_split_v, T=T_v)
    shift_indices_p = shift_function_indices(t_split=t_split_p, T=T_p)
    shift_indices_v = shift_function_indices(t_split=t_split_v, T=T_v)
    unshift_times_p = shift_function_times(t_split=T_p - t_split_p, T=T_p)
    unshift_times_v = shift_function_times(t_split=T_v - t_split_v, T=T_v)
    unshift_indices_p = shift_function_indices(t_split=T_p - t_split_p, T=T_p)
    unshift_indices_v = shift_function_indices(t_split=T_v - t_split_v, T=T_v)
    time_orig_p = np.linspace(start=0, stop=T_p, num=N, endpoint=False)
    time_orig_v = np.linspace(start=0, stop=T_v, num=N, endpoint=False)
    time_p = shift_times_p(time_orig_p)
    time_v = shift_times_v(time_orig_v)

    # re-normalise data
    data_p = get_renormalised_data(data_p, fitinfos_p, t_split=t_split_p, quantity='pressure')
    data_v = get_renormalised_data(data_v, fitinfos_v, t_split=t_split_v, quantity='volume')

    # re-normalise polynomial + points:
    p, points_p = get_renormalised_polynomial_and_points(info_p, points_p)
    v, points_v = get_renormalised_polynomial_and_points(info_v, points_v)

    # convert units
    p = [cv['pressure'] * xx for xx in p]
    v = [cv['volume'] * xx for xx in v]
    data_p['pressure'] = cv['pressure'] * data_p['pressure']
    data_v['volume'] = cv['volume'] * data_v['volume']

    # fit 'other' measurement to each time-series
    data_p['volume'] = poly(
        unshift_indices_v(T_v / T_p * shift_times_p(data_p['time[orig]'])), *v
    )
    data_v['pressure'] = poly(
        unshift_indices_p(T_p / T_v * shift_times_v(data_v['time[orig]'])), *p
    )

    pressure_fit = poly(unshift_indices_p(time_p), *p)
    volume_fit = poly(unshift_indices_v(time_v), *v)

    # set up plots
    fig = make_subplots(
        rows=1,
        cols=1,
        subplot_titles=[cfg.plot.title],
    )

    fig.update_layout(
        width=640,
        height=480,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family=cfg_font.family,
            size=cfg_font.size,
            color='hsla(0, 100%, 0%, 1)',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        title=dict(
            text=cfg.plot.title,
            x=0.5,
            y=0.95,
            font=dict(
                size=cfg_font.size_title,
            ),
        ),
        xaxis=dict(
            title=f'Volume    ({units["volume"]})',
            linecolor='black',
            mirror=True,  # adds border on top too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # rangemode='tozero',
        ),
        yaxis=dict(
            title=f'Pressure    ({units["pressure"]})',
            linecolor='black',
            mirror=True,  # adds border on right too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # autorange='reversed',
            rangemode='tozero',
        ),
        showlegend=cfg.plot.legend,
        legend=dict(
            title='Series/Points',
        ),
    )

    fig.append_trace(
        pgo.Scatter(
            name='P-V [data/fit]',
            x=data_p['volume'],
            y=data_p['pressure'],
            text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * data_p['time']],
            mode='markers',
            marker=dict(
                size=2,
                color='black',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    fig.append_trace(
        pgo.Scatter(
            name='P-V [fit/data]',
            x=data_v['volume'],
            y=data_v['pressure'],
            text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * data_v['time']],
            mode='markers',
            marker=dict(
                size=2,
                color='black',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    fig.append_trace(
        pgo.Scatter(
            name='P-V [fit]',
            x=volume_fit,
            y=pressure_fit,
            text=[],
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
                # color='hsla(0, 100%, 50%, 0)',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    points_ = []

    for key, ts in points_p.items():
        _, p_ = coordinates_special_points(ts, p, T=T_p, t_split=t_split_p)
        _, v_ = coordinates_special_points(ts, v, T=T_p, t_split=t_split_p)
        settings = cfg_markers_p.get(key, None)
        points_.append((key, v_, p_, settings))

    for key, ts in points_v.items():
        _, p_ = coordinates_special_points(ts, p, T=T_v, t_split=t_split_v)
        _, v_ = coordinates_special_points(ts, v, T=T_v, t_split=t_split_v)
        settings = cfg_markers_v.get(key, None)
        points_.append((key, v_, p_, settings))

    for key, v_, p_, settings in points_:
        settings = settings or MarkerSettings(name=key, size=6, symbol='x')
        if settings.ignore:
            continue
        fig.append_trace(
            pgo.Scatter(
                name=settings.name,
                x=v_,
                y=p_,
                mode='markers+text',
                marker=dict(
                    symbol=settings.symbol,
                    size=settings.size,
                    color=settings.colour,
                ),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    path = cfg.plot.path.__root__
    if path is not None:
        path = path.format(label=case.label, kind='pressure-volume')
        save_image(fig=fig, path=path)

    return fig


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SECONDARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def add_plot_time_series(
    fig: pgo.Figure,
    name: Optional[str],
    time: np.ndarray,
    values: np.ndarray,
    row: int,
    col: int,
    mode: str = 'lines',
    line: dict = dict(
        width=1,
        color='black',
        # color='hsla(0, 100%, 50%, 0)',
    ),
    marker: dict = dict(
        size=1,
        color='hsla(0, 100%, 50%, 0)',
        line=dict(
            width=1,
            color='black',
        ),
    ),
    text: Optional[str] = None,
    points: list[tuple[str, Iterable[float], Iterable[float], Optional[MarkerSettings]]] = {},
    showlegend: bool = False,
    showlegend_points: bool = True,
) -> pgo.Figure:
    fig.append_trace(
        pgo.Scatter(
            name=name,
            x=time,
            y=values,
            text=[text or name for _ in time],
            mode=mode,
            line=line if mode == 'lines' else None,
            line_shape='spline',
            marker=marker if mode == 'markers' else None,
            showlegend=showlegend,
        ),
        row=row,
        col=col,
    )

    for key, time_, values_, settings in points:
        settings = settings or MarkerSettings(name=key, size=6, symbol='x')
        if settings.ignore:
            continue
        fig.append_trace(
            pgo.Scatter(
                name=settings.name,
                x=time_,
                y=values_,
                mode='markers+text',
                marker=dict(
                    symbol=settings.symbol,
                    size=settings.size,
                    color=settings.colour,
                ),
                showlegend=showlegend_points,
            ),
            row=row,
            col=col,
        )
        for t in time_:
            fig.add_vline(x=t, line_width=0.5, line_dash='dash', line_color=settings.colour)

    return fig


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_image(fig: pgo.Figure, path: str):
    p = Path(os.path.dirname(path))
    p.mkdir(parents=True, exist_ok=True)
    if path.endswith('.html'):
        fig.write_html(path)
    else:
        fig.write_image(path)
    return


def shift_function_times(t_split: float, T: float):
    def shift(t: np.ndarray, strict: bool = True) -> np.ndarray:
        if strict:
            parts = [t[t >= t_split] - t_split, (T - t_split) + t[t < t_split]]
        else:
            TT = 0 * t[t == t_split]  # add this for peridocity
            TT[:] = T
            parts = [t[t >= t_split] - t_split, (T - t_split) + t[t < t_split], TT]
        return np.concatenate(parts)

    return shift


def shift_function_indices(t_split: float, T: float):
    def shift(t: np.ndarray, strict: bool = True) -> np.ndarray:
        if strict:
            parts = [t[t >= t_split], t[t < t_split]]
        else:
            TT = 0 * t[t == t_split]  # add this for peridocity
            TT[:] = T if t_split == 0 else t_split
            parts = [t[t >= t_split], t[t < t_split], TT]
        return np.concatenate(parts)

    return shift


def coordinates_special_points(
    t: Iterable[float], p: list[float], T: float, t_split: float
) -> tuple[np.ndarray, np.ndarray]:
    shift_times = shift_function_times(t_split=t_split, T=T)
    shift_indices = shift_function_indices(t_split=t_split, T=T)

    t = np.unique(np.asarray(t))
    values = poly(shift_indices(t, strict=False), *p)
    t = shift_times(t, strict=False)

    return t, values
