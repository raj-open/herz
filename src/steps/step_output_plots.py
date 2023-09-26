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
    'step_output_time_plot_ideal',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_time_plot_ideal(
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
    cfg_markers = config.MARKERS

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    # normalise data
    data = get_renormalised_data(data, fitinfos, quantity=quantity)

    # rescale normalised polynomial + points:
    _, info = fitinfos[-1]
    q, points = get_rescaled_polynomial_and_points(info, points)
    q = [cv[quantity] * xx for xx in q]
    dq = get_derivative_coefficients(q)
    ddq = get_derivative_coefficients(dq)

    # convert everything to numpy-arrays for ease of computation
    points = {key: np.asarray(ts) for key, ts in points.items()}

    # define a time axis for [0, T], include endpoints:
    T = info.normalisation.period

    if 'split' in points:
        t_split = points['split'][0]
        shift_times = lambda t: np.concatenate(
            [t[t >= t_split] - t_split, (T - t_split) + t[t < t_split]]
        )
        shift_indices = lambda t: np.concatenate([t[t >= t_split], t[t < t_split]])
        time0 = np.linspace(start=0, stop=T, num=N, endpoint=False)
        time = time0[:]
        time = shift_times(time)
        t_data = data['time'].to_numpy(copy=True)
        data['time'] = t_data - t_split + T * (t_data < t_split)
    else:
        shift_times = lambda t: t
        shift_indices = lambda t: t
        time0 = np.linspace(start=0, stop=T, num=N + 1, endpoint=True)
        time = time0[:]

    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'<b>Time series for {name} (fitted, single cycle)</b>'
            for name in [f'{quantity.title()}', f'(d/dt){symb}', f'(d/dt)²{symb}']
        ],
    )

    fig.update_layout(
        width=480,
        height=720,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family=cfg_font.family,
            size=cfg_font.size,
            color='hsla(0, 100%, 0%, 1)',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        showlegend=cfg.plot.legend,
        legend=dict(title='Special points'),
    )

    opt = dict(
        linecolor='black',
        mirror=True,  # adds border on right/top too
        ticks='outside',
        showgrid=True,
        visible=True,
        # range=[0, None], # FIXME: does not work!
    )

    t_sp = np.concatenate([[0, T]] + list(points.values()))
    t_sp = np.asarray(list(set(t_sp.tolist())))  # unique elements
    t_sp = cv['time'] * shift_times(t_sp)  # convert units
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

    add_plot_time_series(
        fig,
        name=f'{quantity.title()}',
        text=f'{quantity} [renormalised]',
        time=cv['time'] * data['time'],
        values=cv[quantity] * data[quantity],
        mode='markers',
        row=1,
        col=1,
        markers={},
        showlegend_markers=False,
    )

    add_plot_time_series(
        fig,
        name=f'{symb} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time0), *q),
        row=1,
        col=1,
        markers={
            key: (
                cv['time'] * shift_times(ts),
                poly(shift_indices(ts), *q),
                cfg_markers.get(key, None),
            )
            for key, ts in points.items()
        },
        showlegend_markers=True,
    )
    add_plot_time_series(
        fig,
        name=f'(d/dt){symb} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time0), *dq),
        row=2,
        col=1,
        markers={
            key: (
                cv['time'] * shift_times(ts),
                poly(shift_indices(ts), *dq),
                cfg_markers.get(key, None),
            )
            for key, ts in points.items()
        },
        showlegend_markers=False,
    )
    add_plot_time_series(
        fig,
        name=f'(d/dt)²{symb} [fit]',
        time=cv['time'] * time,
        values=poly(shift_indices(time0), *ddq),
        row=3,
        col=1,
        markers={
            key: (
                cv['time'] * shift_times(ts),
                poly(shift_indices(ts), *ddq),
                cfg_markers.get(key, None),
            )
            for key, ts in points.items()
        },
        showlegend_markers=False,
    )

    path = cfg.plot.path.__root__
    if path is not None:
        path = path.format(label=case.label, kind=f'{quantity}-time-fit')
        save_image(fig=fig, path=path)

    return fig


def step_output_time_plot(
    case: UserCase,
    data: pd.DataFrame,
    points: dict[str, list[int]],
    quantity: str,
    symb: str,
    original_time: bool = True,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font
    cfg_markers = config.MARKERS

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    if original_time:
        data = data.sort_values(by=['time[orig]']).reset_index(drop=True)
        data['time'] = data['time[orig]']

    time = cv['time'] * data['time'].to_numpy(copy=True)
    marked = data['marked'].to_numpy(copy=True)

    x = {
        key: cv[key_] * data[key_].to_numpy(copy=True)
        for key, key_ in [
            ('orig', quantity),
            ('fit', f'{quantity}[fit]'),
            ('d', f'd[1,t]{quantity}[fit]'),
            ('dd', f'd[2,t]{quantity}[fit]'),
        ]
    }

    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'<b>Time series for {name}</b>'
            for name in [f'{quantity.title()}', f'(d/dt){symb}', f'(d/dt)²{symb}']
        ],
    )

    fig.update_layout(
        width=640,
        height=720,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family=cfg_font.family,
            size=cfg_font.size,
            color='hsla(0, 100%, 0%, 1)',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        showlegend=cfg.plot.legend,
        legend=dict(title='Special points'),
    )

    opt = dict(
        linecolor='black',
        mirror=True,  # adds border on right/top too
        ticks='outside',
        showgrid=True,
        visible=True,
        # range=[0, None], # FIXME: does not work!
    )

    for row in range(1, 3 + 1):
        fig.update_xaxes(
            title=f'Time    ({units["time"]})',
            rangemode='tozero',
            **opt,
            row=row,
            col=1,
        )

    for row, key, name in [
        (1, quantity, quantity.title()),
        (2, f'd[1,t]{quantity}[fit]', f'{symb}´(t)'),
        (3, f'd[2,t]{quantity}[fit]', f'{symb}´´(t)'),
    ]:
        unit = units[key]
        fig.update_yaxes(title=f'{name}    ({unit})', rangemode='normal', **opt, row=row, col=1)

    add_plot_time_series(
        fig,
        name=None,
        text='P [original]',
        time=time,
        values=x['orig'],
        mode='markers',
        row=1,
        col=1,
        markers={},
        showlegend_markers=False,
    )
    add_plot_time_series(
        fig,
        name=f'{symb} [fit]',
        time=time,
        values=x['fit'],
        row=1,
        col=1,
        markers={
            key: (time[indices], x['fit'][indices], cfg_markers.get(key, None))
            for key, indices in points.items()
        },
        showlegend_markers=True,
    )
    add_plot_time_series(
        fig,
        name=f'(d/dt){symb} [fit]',
        time=time,
        values=x['d'],
        row=2,
        col=1,
        markers={
            key: (time[indices], x['d'][indices], cfg_markers.get(key, None))
            for key, indices in points.items()
        },
        showlegend_markers=False,
    )
    add_plot_time_series(
        fig,
        name=f'(d/dt)²{symb} [fit]',
        time=time,
        values=x['dd'],
        row=3,
        col=1,
        markers={
            key: (time[indices], x['dd'][indices], cfg_markers.get(key, None))
            for key, indices in points.items()
        },
        showlegend_markers=False,
    )

    path = cfg.plot.path.__root__
    if path is not None:
        path = path.format(label=case.label, kind=f'{quantity}-time')
        save_image(fig=fig, path=path)

    return fig


def step_output_loop_plot(
    case: UserCase,
    data: pd.DataFrame,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    time = cv['time'] * data['time'].to_numpy(copy=True)
    pressure = cv['pressure'] * data['pressure'].to_numpy(copy=True)
    volume = cv['volume'] * data['volume'].to_numpy(copy=True)
    pressure_fit = cv['pressure'] * data['pressure[fit]'].to_numpy(copy=True)
    volume_fit = cv['volume'] * data['volume[fit]'].to_numpy(copy=True)

    text = np.asarray([f'{t:.0f}{units["time"]}' for t in time])

    fig = pgo.Figure(
        data=[
            pgo.Scatter(
                name='P-V [Original]',
                x=volume,
                y=pressure,
                text=text,
                mode='markers',
                marker=dict(
                    size=2,
                    color='black',
                ),
            ),
            pgo.Scatter(
                name='P-V [fit]',
                x=volume_fit,
                y=pressure_fit,
                text=text,
                mode='lines',
                line=dict(
                    width=1,
                    color='blue',
                ),
            ),
            # pgo.Scatter(
            #     name=None,
            #     x=volume[marked],
            #     y=pressure[marked],
            #     text=text[marked],
            #     mode='markers',
            #     marker=dict(
            #         symbol='circle',
            #         size=4,
            #         color='red',
            #     ),
            # ),
        ],
        layout=pgo.Layout(
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
                text=f'<b>{cfg.plot.title}</b>',
                x=0.5,
                y=0.95,
                font=dict(
                    size=cfg_font.size_title,
                    color='hsla(240, 100%, 50%, 1)',
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
                title='P-V Loops',
            ),
        ),
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
    ),
    text: Optional[str] = None,
    markers: dict[str, tuple[Iterable[float], Iterable[float], Optional[MarkerSettings]]] = {},
    showlegend_markers: bool = True,
) -> pgo.Figure:
    fig.append_trace(
        pgo.Scatter(
            name=name,
            x=time,
            y=values,
            text=[text or name for _ in time],
            line_shape='spline',
            mode=mode,
            line=dict(
                width=1,
                color='black',
                # color='hsla(0, 100%, 50%, 0)',
                # line=line,
            )
            if mode == 'lines'
            else None,
            marker=dict(
                size=1,
                color='hsla(0, 100%, 50%, 0)',
                line=line,
            )
            if mode == 'markers'
            else None,
            showlegend=False,
        ),
        row=row,
        col=col,
    )

    for key, (time_, values_, settings) in markers.items():
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
                showlegend=showlegend_markers,
            ),
            row=row,
            col=col,
        )
        for t in time_:
            fig.add_vline(x=t, line_width=1, line_dash='dash', line_color=settings.colour)

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
