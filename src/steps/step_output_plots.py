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

    cv = dict(
        time=convert_units(unitFrom=cfg_units.time, unitTo=cfg.quantities.time.unit),
        pressure=convert_units(
            unitFrom=cfg_units.pressure, unitTo=cfg.quantities.pressure.unit
        ),
        volume=convert_units(unitFrom=cfg_units.volume, unitTo=cfg.quantities.volume.unit),
    )

    cycles = data['cycle'].to_numpy(copy=True)
    marked = data['marked'].to_numpy(copy=True)
    time = cv['time'] * data['time'].to_numpy(copy=True)

    figs = dict()
    for quantity, symb, unit in [
        ('pressure', 'P', cfg.quantities.pressure.unit),
        ('volume', 'V', cfg.quantities.volume.unit),
    ]:
        scale = cv[f'{quantity}']
        x = scale * data[f'{quantity}'].to_numpy(copy=True)
        x_peak = data[f'{quantity}[peak]'].to_numpy(copy=True)
        x_trough = data[f'{quantity}[trough]'].to_numpy(copy=True)
        x_fit = scale * data[f'{quantity}[fit]'].to_numpy(copy=True)

        # s = cv['time']
        s = 1.0

        scale = cv[f'{quantity}'] / s
        dx_fit = scale * data[f'd[1,t]{quantity}[fit]'].to_numpy(copy=True)

        scale = cv[f'{quantity}'] / s**2
        ddx_fit = scale * data[f'd[2,t]{quantity}[fit]'].to_numpy(copy=True)

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
            legend=dict(title='Time series'),
        )

        opt = dict(
            linecolor='black',
            mirror=True,  # adds border on right/top too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
        )

        fig.update_xaxes(
            title=f'Time    ({cfg.quantities.time.unit})',
            rangemode='tozero',
            **opt,
            row=1,
            col=1,
        )
        fig.update_xaxes(
            title=f'Time    ({cfg.quantities.time.unit})',
            rangemode='tozero',
            **opt,
            row=2,
            col=1,
        )
        fig.update_xaxes(
            title=f'Time    ({cfg.quantities.time.unit})',
            rangemode='tozero',
            **opt,
            row=3,
            col=1,
        )
        fig.update_yaxes(
            title=f'{quantity.title()}    ({unit})', rangemode='normal', **opt, row=1, col=1
        )
        fig.update_yaxes(
            title=f'{symb}´(t)    ({unit}·s¯¹)', rangemode='normal', **opt, row=2, col=1
        )
        fig.update_yaxes(
            title=f'{symb}´´(t)    ({unit}·s¯²)', rangemode='normal', **opt, row=3, col=1
        )

        special = [
            SpecialPoints(name='peak', points=x_peak, colour='blue', size=6, symbol='x'),
            SpecialPoints(name='trough', points=x_trough, colour='blue', size=6, symbol='x'),
            # SpecialPoints(name='marked', points=marked, colour='red', size=4, symbol='circle'),
        ]
        add_plot_time_series(
            fig,
            name=None,
            text='P [original]',
            time=time,
            values=x,
            special=special,
            mode='markers',
            row=1,
            col=1,
        )
        special = []
        add_plot_time_series(
            fig,
            name=f'{symb} [fit]',
            time=time,
            values=x_fit,
            special=special,
            row=1,
            col=1,
        )
        special = []
        add_plot_time_series(
            fig,
            name=f'(d/dt){symb} [fit]',
            time=time,
            values=dx_fit,
            special=special,
            row=2,
            col=1,
        )
        add_plot_time_series(
            fig,
            name=f'(d/dt)²{symb} [fit]',
            time=time,
            values=ddx_fit,
            special=special,
            row=3,
            col=1,
        )

        save_image(fig=fig, path=cfg.plot.path.__root__, kind=f'{quantity}-time')
        figs[quantity] = fig

    return figs['pressure'], figs['volume']


def step_output_loop_plot(data: pd.DataFrame) -> pgo.Figure:
    cfg = config.OUTPUT_CONFIG
    cfg_units = config.UNITS
    cfg_font = cfg.plot.font

    cv = dict(
        time=convert_units(unitFrom=cfg_units.time, unitTo=cfg.quantities.time.unit),
        pressure=convert_units(
            unitFrom=cfg_units.pressure, unitTo=cfg.quantities.pressure.unit
        ),
        volume=convert_units(unitFrom=cfg_units.volume, unitTo=cfg.quantities.volume.unit),
    )

    cycles = data['cycle'].to_numpy(copy=True)
    marked = data['marked'].to_numpy(copy=True)
    time = cv['time'] * data['time'].to_numpy(copy=True)
    pressure = cv['pressure'] * data['pressure'].to_numpy(copy=True)
    volume = cv['volume'] * data['volume'].to_numpy(copy=True)
    pressure_fit = cv['pressure'] * data['pressure[fit]'].to_numpy(copy=True)
    volume_fit = cv['volume'] * data['volume[fit]'].to_numpy(copy=True)

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
                title=f'Volume    ({cfg.quantities.volume.unit})',
                linecolor='black',
                mirror=True,  # adds border on top too
                ticks='outside',
                showgrid=True,
                visible=True,
                # range=[0, None], # FIXME: does not work!
                # rangemode='tozero',
            ),
            yaxis=dict(
                title=f'Pressure    ({cfg.quantities.pressure.unit})',
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
