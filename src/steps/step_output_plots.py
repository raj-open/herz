#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


def step_output_time_plots(data: pd.DataFrame) -> pgo.Figure:
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
    pressure_peak = data['pressure_peak'].to_numpy(copy=True)
    pressure_trough = data['pressure_trough'].to_numpy(copy=True)
    volume_peak = data['volume_peak'].to_numpy(copy=True)
    volume_trough = data['volume_trough'].to_numpy(copy=True)

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=[
            # dict(
            #     text=f'<b>Time series for {quantity}</b>',
            #     x=0.5,
            #     y=0.95,
            #     font=dict(
            #         size=cfg_font.size_title,
            #         color='hsla(240, 100%, 50%, 1)',
            #     ),
            # )
            f'<b>Time series for {quantity}</b>'
            for quantity in ['Pressure', 'Volume']
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
        legend=dict(
            title='Time series',
        ),
    )

    for row, name, y, peaks, troughs in [
        (1, 'Pressure', pressure, pressure_peak, pressure_trough),
        (2, 'Volume', volume, volume_peak, volume_trough),
    ]:
        fig.append_trace(
            pgo.Scatter(
                name=cfg.name,
                x=time,
                y=y,
                mode='markers',
                marker=dict(
                    size=2,
                    color='hsla(0, 100%, 50%, 0)',
                    line=dict(
                        width=1,
                        color='black',
                    ),
                ),
            ),
            row=row,
            col=1,
        )
        fig.append_trace(
            pgo.Scatter(
                name=None,
                x=time[peaks].tolist() + time[troughs].tolist(),
                y=y[peaks].tolist() + y[troughs].tolist(),
                mode='markers',
                marker=dict(
                    size=4,
                    color='hsla(0, 100%, 50%, 0)',
                    line=dict(
                        width=2,
                        color='blue',
                    ),
                ),
            ),
            row=row,
            col=1,
        )
        fig.append_trace(
            pgo.Scatter(
                name=None,
                x=time[marked],
                y=y[marked],
                mode='markers',
                marker=dict(
                    size=4,
                    color='hsla(0, 100%, 50%, 0)',
                    line=dict(
                        width=2,
                        color='red',
                    ),
                ),
            ),
            row=row,
            col=1,
        )

    for i, quantity, unit in [
        (1, 'Pressure', cfg.quantities.pressure.unit),
        (2, 'Volume', cfg.quantities.volume.unit),
    ]:
        fig.update_xaxes(
            row=i,
            col=1,
            title=f'Time ({cfg.quantities.time.unit})',
            linecolor='black',
            mirror=True,  # adds border on top too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            rangemode='tozero',
        )

        fig.update_yaxes(
            row=i,
            col=1,
            title=f'{quantity} ({unit})',
            linecolor='black',
            mirror=True,  # adds border on right too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # autorange='reversed',
            rangemode='normal',
        )

    save_image(fig=fig, path=cfg.plot.path.__root__, kind='time')
    return fig


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
    pressure_peak = data['pressure_peak'].to_numpy(copy=True)
    pressure_trough = data['pressure_trough'].to_numpy(copy=True)
    volume_peak = data['volume_peak'].to_numpy(copy=True)
    volume_trough = data['volume_trough'].to_numpy(copy=True)

    text = np.asarray([f'{t:.0f}{cfg.quantities.time.unit}' for t in time])

    fig = pgo.Figure(
        data=[
            pgo.Scatter(
                name=cfg.name,
                x=volume,
                y=pressure,
                text=text,
                mode='markers',
                marker=dict(
                    size=2,
                    color='hsla(0, 100%, 50%, 0)',
                    line=dict(
                        width=1,
                        color='black',
                        # color='hsla(0, 100%, 0%, 1)',
                        # color=PLOTLY_COLOUR_SCHEME.GREENS.value,
                    ),
                ),
            ),
            pgo.Scatter(
                name=cfg.name,
                x=volume[marked],
                y=pressure[marked],
                text=text[marked],
                mode='markers',
                marker=dict(
                    size=4,
                    color='hsla(0, 100%, 50%, 0)',
                    line=dict(
                        width=1,
                        color='red',
                        # color='hsla(0, 100%, 0%, 1)',
                        # color=PLOTLY_COLOUR_SCHEME.GREENS.value,
                    ),
                ),
            ),
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

    save_image(fig=fig, path=cfg.plot.path.__root__, kind='loop')

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
