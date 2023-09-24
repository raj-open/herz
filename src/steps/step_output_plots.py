#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations
from ..thirdparty.code import *
from ..thirdparty.data import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.plots import *
from ..thirdparty.system import *
from ..thirdparty.types import *

from ..setup import config
from ..core.utils import *
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_output_loop_plot',
    'step_output_time_plots',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_time_plots(data: pd.DataFrame) -> tuple[pgo.Figure, pgo.Figure]:
    cfg = config.OUTPUT_CONFIG
    cfg_units = config.UNITS
    cfg_font = cfg.plot.font

    cv_t = convert_units(unitFrom=cfg_units.time, unitTo=cfg.quantities.time.unit)
    cv_p = convert_units(unitFrom=cfg_units.pressure, unitTo=cfg.quantities.pressure.unit)
    cv_v = convert_units(unitFrom=cfg_units.volume, unitTo=cfg.quantities.volume.unit)

    cycles = data['cycle'].to_numpy(copy=True)
    marked = data['marked'].to_numpy(copy=True)
    time = cv_t * data['time'].to_numpy(copy=True)
    pressure = cv_p * data['pressure'].to_numpy(copy=True)
    pressure_fit = cv_p * data['pressure[fit]'].to_numpy(copy=True)
    dpressure_fit = cv_p * data['d[1,t]pressure[fit]'].to_numpy(copy=True)
    ddpressure_fit = cv_p * data['d[2,t]pressure[fit]'].to_numpy(copy=True)
    volume = cv_v * data['volume'].to_numpy(copy=True)
    pressure_peak = data['pressure[peak]'].to_numpy(copy=True)
    pressure_trough = data['pressure[trough]'].to_numpy(copy=True)
    volume_peak = data['volume[peak]'].to_numpy(copy=True)
    volume_trough = data['volume[trough]'].to_numpy(copy=True)

    fig_p = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'<b>Time series for {quantity.title()}</b>'
            for quantity in ['Pressure', '(d/dt)P', '(d/dt)²P']
        ],
    )
    fig_v = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=[
            f'<b>Time series for {quantity.title()}</b>'
            for quantity in ['Volume', '(d/dt)V', '(d/dt)²V']
        ],
    )

    opt = dict(
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
        legend=dict(title='Time series'),
    )
    fig_p.update_layout(**opt)
    fig_v.update_layout(**opt)

    special = [
        SpecialPoints(name='peak', points=pressure_peak, colour='blue', size=6, symbol='x'),
        SpecialPoints(name='trough', points=pressure_trough, colour='blue', size=6, symbol='x'),
        # SpecialPoints(name='marked', points=marked, colour='red', size=4, symbol='circle'),
    ]
    add_plot_time_series(
        fig_p,
        name=None,
        text='P [original]',
        time=time,
        values=pressure,
        special=special,
        mode='markers',
        row=1,
        col=1,
    )
    special = []
    add_plot_time_series(
        fig_p,
        name='P [fit]',
        time=time,
        values=pressure_fit,
        special=special,
        row=1,
        col=1,
    )
    special = []
    add_plot_time_series(
        fig_p,
        name='(d/dt)P [fit]',
        time=time,
        values=dpressure_fit,
        special=special,
        row=2,
        col=1,
    )
    add_plot_time_series(
        fig_p,
        name='(d/dt)²P [fit]',
        time=time,
        values=ddpressure_fit,
        special=special,
        row=3,
        col=1,
    )

    special = [
        SpecialPoints(name='peak', points=pressure_peak, colour='blue', size=6),
        SpecialPoints(name='trough', points=pressure_trough, colour='blue', size=6),
        # SpecialPoints(name='marked', points=marked, colour='red', size=4, symbol='circle'),
    ]
    add_plot_time_series(
        fig_v,
        name=None,
        text='V [original]',
        time=time,
        values=volume,
        special=special,
        mode='markers',
        row=1,
        col=1,
    )

    for fig, quantity, unit in [
        (fig_p, 'Pressure', cfg.quantities.pressure.unit),
        (fig_v, 'Volume', cfg.quantities.volume.unit),
    ]:
        opt = dict(
            linecolor='black',
            mirror=True,  # adds border on right/top too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            row=1,
            col=1,
        )
        fig.update_xaxes(title=f'Time ({cfg.quantities.time.unit})', rangemode='tozero', **opt)
        fig.update_xaxes(title=f'{quantity} ({unit})', rangemode='normal', **opt)

    save_image(fig=fig_p, path=cfg.plot.path.__root__, kind='pressure-time')
    save_image(fig=fig_v, path=cfg.plot.path.__root__, kind='volume-time')
    return fig_p, fig_v


def step_output_loop_plot(data: pd.DataFrame) -> pgo.Figure:
    cfg = config.OUTPUT_CONFIG
    cfg_units = config.UNITS
    cfg_font = cfg.plot.font

    cv_t = convert_units(unitFrom=cfg_units.time, unitTo=cfg.quantities.time.unit)
    cv_p = convert_units(unitFrom=cfg_units.pressure, unitTo=cfg.quantities.pressure.unit)
    cv_v = convert_units(unitFrom=cfg_units.volume, unitTo=cfg.quantities.volume.unit)

    cycles = data['cycle'].to_numpy(copy=True)
    marked = data['marked'].to_numpy(copy=True)
    time = cv_t * data['time'].to_numpy(copy=True)
    pressure = cv_p * data['pressure'].to_numpy(copy=True)
    volume = cv_v * data['volume'].to_numpy(copy=True)
    pressure_fit = cv_p * data['pressure[fit]'].to_numpy(copy=True)
    volume_fit = volume

    text = np.asarray([f'{t:.0f}{cfg.quantities.time.unit}' for t in time])

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
            #     name=cfg.name,
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
                title=f'Volume ({cfg.quantities.volume.unit})',
                linecolor='black',
                mirror=True,  # adds border on top too
                ticks='outside',
                showgrid=True,
                visible=True,
                # range=[0, None], # FIXME: does not work!
                # rangemode='tozero',
            ),
            yaxis=dict(
                title=f'Pressure ({cfg.quantities.pressure.unit})',
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

    save_image(fig=fig, path=cfg.plot.path.__root__, kind='pressure-volume')

    return fig


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SECONDARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def add_plot_time_series(
    fig: pgo.Figure,
    name: Optional[str],
    time: np.ndarray,
    values: np.ndarray,
    special: list[tuple[Optional[str], list[int], Optional[str]]],
    row: int,
    col: int,
    mode: str = 'lines',
    line: dict = dict(
        width=1,
        color='black',
    ),
    text: Optional[str] = None,
) -> pgo.Figure:
    p = pgo.Scatter(
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
    )
    fig.append_trace(p, row=row, col=col)

    for s in special:
        p = pgo.Scatter(
            name=s.name,
            x=time[s.points].tolist(),
            y=values[s.points].tolist(),
            mode='markers+text',
            marker=dict(
                symbol=s.symbol,
                size=s.size,
                color=s.colour,
            ),
        )
        fig.append_trace(p, row=row, col=col)

    return fig


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def save_image(
    fig: pgo.Figure,
    path: Optional[str],
    kind: str,
):
    if path is None:
        return

    p = Path(os.path.dirname(path))
    p.mkdir(parents=True, exist_ok=True)

    path = path.format(kind=kind)
    if path.endswith('.html'):
        fig.write_html(path)
    else:
        fig.write_image(path)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY MODEL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@dataclass
class SpecialPoints:
    name: str = field()
    points: list = field()
    size: int = field(default=2)
    colour: str = field(default='black')
    # see https://plotly.com/python/marker-style
    symbol: str = field(default='x')
