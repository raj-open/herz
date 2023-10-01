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
from ..setup.series import *
from ..core.utils import *
from ..core.poly import *
from ..models.app import *
from ..models.internal import *
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_output_loop_plot',
    'step_output_time_plot',
    'quick_plot',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_time_plot(
    case: UserCase,
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    points: dict[str, SpecialPointsConfig],
    quantity: str,
    symb: str,
    shifted: bool = False,
    N: int = 1000,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font
    _, info = fitinfos[-1]
    T = info.normalisation.period
    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    # re-normalise data
    data = get_renormalised_data(data, fitinfos, quantity=quantity)

    # compute series for fitted curves
    special, _, time, data_fitted = compute_fitted_curves_for_plots(info, points=points, quantity=quantity, shift=shifted, n_der=2, N=N)  # fmt: skip

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

    t_sp = np.unique([0, T] + [point.time for point in special[0]])
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
        time=time,
        values=data_fitted[0],
        cv_time=cv['time'],
        cv_value=cv[quantity],
        row=1,
        col=1,
        points=special[0],
        showlegend=True,
        showlegend_points=True,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt){symb} [fit]',
        time=time,
        values=data_fitted[1],
        cv_time=cv['time'],
        cv_value=cv[f'd[1,t]{quantity}[fit]'],
        row=2,
        col=1,
        points=special[1],
        showlegend=False,
        showlegend_points=False,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt)²{symb} [fit]',
        time=time,
        values=data_fitted[2],
        cv_time=cv['time'],
        cv_value=cv[f'd[2,t]{quantity}[fit]'],
        row=3,
        col=1,
        points=special[2],
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
    points_p: dict[str, SpecialPointsConfig],
    data_v: pd.DataFrame,
    fitinfos_v: list[tuple[tuple[int, int], FittedInfo]],
    points_v: dict[str, SpecialPointsConfig],
    shifted: bool = False,
    N: int = 1000,
) -> pgo.Figure:
    cfg = case.output
    cfg_font = cfg.plot.font

    cv = output_conversions(cfg.quantities)
    units = output_units(cfg.quantities)

    _, info_p = fitinfos_p[-1]
    _, info_v = fitinfos_v[-1]
    T_p = info_p.normalisation.period
    T_v = info_v.normalisation.period
    t_align_p = get_alignment_time(info_p, points_p, quantity='pressure') if shifted else 0.0
    t_align_v = get_alignment_time(info_v, points_v, quantity='volume') if shifted else 0.0

    # re-normalise data
    data_p = get_renormalised_data(data_p, fitinfos_p, quantity='pressure')
    data_v = get_renormalised_data(data_v, fitinfos_v, quantity='volume')

    # compute series for fitted curves
    _, [p], time_p, [pressure_fit] = compute_fitted_curves_for_plots(info_p, points=points_p, quantity='pressure', shift=shifted, n_der=0, N=N)  # fmt: skip
    _, [v], time_v, [volume_fit] = compute_fitted_curves_for_plots(info_v, points=points_v, quantity='volume', shift=shifted, n_der=0, N=N)  # fmt: skip

    # fit 'other' measurement to each time-series
    data_p['volume'] = poly(T_v * ((data_p['time[orig]'] / T_p + t_align_v / T_v) % 1), *v)
    data_v['pressure'] = poly(T_p * ((data_v['time[orig]'] / T_v + t_align_p / T_p) % 1), *p)

    # set up plots
    fig = make_subplots(rows=1, cols=1, subplot_titles=[])

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
        updatemenus=[],  # use to add buttons to plots
    )

    # fig.append_trace(
    #     pgo.Scatter(
    #         name='P-V [data/fit]',
    #         x=data_p['volume'],
    #         y=data_p['pressure'],
    #         text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * data_p['time']],
    #         mode='markers',
    #         marker=dict(
    #             size=2,
    #             color='black',
    #         ),
    #         showlegend=True,
    #     ),
    #     row=1,
    #     col=1,
    # )

    fig.append_trace(
        pgo.Scatter(
            name='P-V [fit/data]',
            x=cv['volume'] * data_v['volume'],
            y=cv['pressure'] * data_v['pressure'],
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
            # NOTE: Ensure that the cycle contains start+end points!
            x=cv['volume'] * np.concatenate([volume_fit, volume_fit[:1]]),
            y=cv['pressure'] * np.concatenate([pressure_fit, pressure_fit[:1]]),
            text=[
                f'{tt:.0f}{units["time"]}'
                for tt in cv['time'] * np.concatenate([time_p, time_p[:1]])
            ],
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

    sh = t_align_p / T_p - t_align_v / T_v
    for _, point in points_p.items():
        if point.ignore:
            continue
        t_p = point.time
        t_v = (t_p - sh) % 1
        p_ = poly_single(T_p * t_p, *p)
        v_ = poly_single(T_v * t_v, *v)
        points_.append((v_, p_, point))

    for _, point in points_v.items():
        if point.ignore:
            continue
        t_v = point.time
        t_p = (t_v + sh) % 1
        v_ = poly_single(T_v * t_v, *v)
        p_ = poly_single(T_p * t_p, *p)
        points_.append((v_, p_, point))

    for v_, p_, point in points_:
        if point.ignore:
            continue
        marker = point.marker
        fig.append_trace(
            pgo.Scatter(
                name=point.name,
                x=[cv['volume'] * v_],
                y=[cv['pressure'] * p_],
                mode='markers+text',
                # text=[ point.name ],
                # textposition = 'middle right', # 'top|middle|bottom left|center|right'
                marker=dict(
                    symbol=marker.symbol,
                    size=marker.size,
                    color=marker.colour,
                ),
                visible=True if point.found else 'legendonly',
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


def quick_plot(
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
    renormalised: bool = True,
    N: int = 1000,
) -> Generator[pgo.Figure, None, None]:
    _, info = fitinfos[0]
    if renormalised:
        T = info.normalisation.period
        q = get_renormalised_polynomial(info)
        data = get_renormalised_data(data, fitinfos, quantity=quantity)
    else:
        T = 1.0
        q = info.coefficients

    dq = get_derivative_coefficients(q)
    ddq = get_derivative_coefficients(dq)
    time = np.linspace(start=0.0, stop=T, num=N + 1, endpoint=True)

    layout = pgo.Layout(
        width=640,
        height=480,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family='Calibri',
            size=10,
            color='black',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        title=dict(
            text='Debug plot',
            x=0.5,
            y=0.95,
            font=dict(size=12),
        ),
        xaxis=dict(
            title=f'time',
            linecolor='black',
            mirror=True,  # adds border on top too
            ticks='outside',
            showgrid=True,
            visible=True,
            # range=[0, None], # FIXME: does not work!
            # rangemode='tozero',
        ),
        yaxis=dict(
            title=quantity,
            linecolor='black',
            mirror=True,  # adds border on right too
            ticks='outside',
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
            name='debug [fit]',
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=poly(time, *q),
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
            ),
            showlegend=True,
        ),
    ]
    if renormalised:
        plot_data.append(
            pgo.Scatter(
                name='debug [data]',
                # NOTE: Ensure that the cycle contains start+end points!
                x=data['time'],
                y=data[quantity],
                mode='markers',
                line_shape='spline',
                marker=dict(
                    size=2,
                    color='black',
                ),
                showlegend=True,
            ),
        )
    yield pgo.Figure(layout=layout, data=plot_data)

    plot_data = [
        pgo.Scatter(
            name='dx/dt [fit]',
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=poly(time, *dq) / T,
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
            ),
            showlegend=True,
        ),
    ]
    yield pgo.Figure(layout=layout, data=plot_data)

    plot_data = [
        pgo.Scatter(
            name='d²x/dt² [fit]',
            # NOTE: Ensure that the cycle contains start+end points!
            x=time,
            y=poly(time, *ddq) / T**2,
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
            ),
            showlegend=True,
        ),
    ]
    yield pgo.Figure(layout=layout, data=plot_data)
    return


def add_plot_time_series(
    fig: pgo.Figure,
    name: Optional[str],
    time: np.ndarray,
    values: np.ndarray,
    cv_time: float = 1.0,
    cv_value: float = 1.0,
    row: int = 1,
    col: int = 1,
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
    points: list[tuple[str, SpecialPointsConfig]] = [],
    showlegend: bool = False,
    showlegend_points: bool = True,
) -> pgo.Figure:
    # indices = indices_non_outliers(values, sig=2)
    # time = time[indices]
    # values = values[indices]
    fig.append_trace(
        pgo.Scatter(
            name=name,
            x=cv_time * time,
            y=cv_value * values,
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

    for point in points:
        if point.ignore:
            continue
        marker = point.marker
        fig.append_trace(
            pgo.Scatter(
                name=point.name,
                x=[cv_time * point.time],
                y=[cv_value * point.value],
                mode='markers+text',
                marker=dict(
                    symbol=marker.symbol,
                    size=marker.size,
                    color=marker.colour,
                ),
                visible=True if point.found else 'legendonly',
                showlegend=showlegend_points,
            ),
            row=row,
            col=col,
        )
        fig.add_vline(
            x=cv_time * point.time, line_width=0.5, line_dash='dash', line_color=marker.colour
        )

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


def compute_fitted_curves_for_plots(
    info: FittedInfo,
    points: dict[str, SpecialPointsConfig],
    quantity: str,
    shift: bool,
    n_der: int,
    N: int = 1000,
) -> tuple[list[list[SpecialPointsConfig]], list[list[float]], np.ndarray, list[np.ndarray],]:
    t_align = get_alignment_time(info, points, quantity=quantity) if shift else 0.0
    T = info.normalisation.period

    # compute coefficients of (derivatives of) polynomial coefficients
    coeffs = [[]] * (n_der + 1)
    coeffs[0] = get_renormalised_polynomial(info)
    for k in range(1, n_der + 1):
        coeffs[k] = get_derivative_coefficients(coeffs[k - 1])

    # compute and shift series
    time = np.linspace(start=0, stop=T, num=N, endpoint=False)
    q = [poly(time, *coeff) for coeff in coeffs]
    q = [np.concatenate([qq[time >= t_align], qq[time < t_align]]) for qq in q]

    # compute and shift special points
    special = [{}] * (n_der + 1)
    for k, coeff in enumerate(coeffs):
        special[k] = [point.copy() for key, point in points.items()]
        t = T * np.asarray([point.time for point in special[k]])
        values = poly(t, *coeff)
        for t0, y0, point in zip(t, values, special[k]):
            if point.ignore:
                continue
            point.time = (t0 - t_align) % T
            point.value = y0

    return special, coeffs, time, q
