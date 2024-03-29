#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.plots import *
from ....thirdparty.system import *
from ....thirdparty.types import *

from ....setup import config
from ....core.log import *
from ....models.app import *
from ....models.fitting import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....queries.scientific import *
from ....algorithms.fitting.trigonometric import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_output_loop_plot',
    'step_output_time_plot',
    'quick_plot',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP output time-plot', level=LOG_LEVELS.INFO)
def step_output_time_plot(
    data: pd.DataFrame,
    info: FittedInfoNormalisation,
    fit_poly: FittedInfoPoly,
    fits_trig: tuple[list[tuple[float, float]], FittedInfoTrig | None],
    special: dict[str, SpecialPointsConfig],
    quantity: str,
    symb: str,
    plot_name: str,
    plot_label: str,
    cfg_output: UserOutput,
    N: int = 1000,
) -> pgo.Figure:
    cfg_font = cfg_output.plot.font
    cv = output_conversions(cfg_output.quantities, units=config.UNITS)
    units = output_units(cfg_output.quantities)
    T = info.period

    # compute series for fitted curves
    specials, _, time, data_poly = compute_fitted_curves_poly(
        info=info,
        fit=fit_poly,
        special=special,
        n_der=2,
        N=N,
    )

    time_trig = data_trig = None
    intervals, fit_trig = fits_trig
    if fit_trig is not None:
        time_trig, data_trig = compute_fitted_curves_trig(
            info=info,
            fit_trig=fit_trig,
            intervals=intervals,
            special=specials[0],
            N=N,
        )

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
            text=plot_name,
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
        showlegend=cfg_output.plot.legend,
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
        special={},
        showlegend=True,
        showlegend_points=False,
    )

    if time_trig is not None and data_trig is not None:
        add_plot_time_series(
            fig,
            name=f'{quantity.title()} [trig]',
            time=time_trig,
            values=data_trig,
            cv_time=cv['time'],
            cv_value=cv[quantity],
            row=1,
            col=1,
            mode='markers',
            marker=dict(
                size=3,
                color='hsla(100, 100%, 25%, 0.3)',
            ),
            special={},
            showlegend=True,
            showlegend_points=True,
        )

    add_plot_time_series(
        fig,
        name=f'{quantity.title()} [fit]',
        time=time,
        values=data_poly[0],
        cv_time=cv['time'],
        cv_value=cv[quantity],
        row=1,
        col=1,
        special=specials[0],
        showlegend=True,
        showlegend_points=True,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt){symb} [fit]',
        time=time,
        values=data_poly[1],
        cv_time=cv['time'],
        cv_value=cv[f'd[1,t]{quantity}[fit]'],
        row=2,
        col=1,
        special=specials[1],
        showlegend=False,
        showlegend_points=False,
    )

    add_plot_time_series(
        fig,
        name=f'(d/dt)²{symb} [fit]',
        time=time,
        values=data_poly[2],
        cv_time=cv['time'],
        cv_value=cv[f'd[2,t]{quantity}[fit]'],
        row=3,
        col=1,
        special=specials[2],
        showlegend=False,
        showlegend_points=False,
    )

    path = cfg_output.plot.path.root
    if path is not None:
        path = path.format(label=plot_label, kind=f'{quantity}-time')
        save_image(fig=fig, path=path)

    return fig


@echo_function(message='STEP output P-V loop plot', level=LOG_LEVELS.INFO)
def step_output_loop_plot(
    data_p: pd.DataFrame,
    data_v: pd.DataFrame,
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    fit_poly_p: FittedInfoPoly,
    fit_poly_v: FittedInfoPoly,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
    plot_name: str,
    plot_label: str,
    cfg_output: UserOutput,
    N: int = 1000,
) -> pgo.Figure:
    cfg_font = cfg_output.plot.font

    cv = output_conversions(cfg_output.quantities, units=config.UNITS)
    units = output_units(cfg_output.quantities)

    T_p = info_p.period
    T_v = info_v.period
    t_align_p = special_p['align'].time
    t_align_v = special_v['align'].time

    # compute series for fitted curves
    _, [model_p], time_p, [pressure_fit] = compute_fitted_curves_poly(info_p, fit_poly_p, special=special_p, n_der=0, N=N)  # fmt: skip
    _, [model_v], time_v, [volume_fit] = compute_fitted_curves_poly(info_v, fit_poly_v, special=special_v, n_der=0, N=N)  # fmt: skip

    # fit 'other' measurement to each time-series
    data_p['volume'] = model_v.values(((T_v / T_p) * data_p['time'] + t_align_v) % T_v)
    data_v['pressure'] = model_p.values(((T_p / T_v) * data_v['time'] + t_align_p) % T_p)

    # set up plots
    fig = make_subplots(rows=1, cols=1, subplot_titles=[])

    fig.update_layout(
        width=640,
        height=540,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family=cfg_font.family,
            size=cfg_font.size,
            color='hsla(0, 100%, 0%, 1)',
        ),
        plot_bgcolor='hsla(0, 100%, 0%, 0.1)',
        title=dict(
            text=plot_name,
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
        showlegend=cfg_output.plot.legend,
        legend=dict(
            title='Series/Points',
        ),
        updatemenus=[],  # use to add buttons to plots
    )

    fig.append_trace(
        pgo.Scatter(
            name='P vs. V(P) [data/poly-fit]',
            x=cv['volume'] * data_p['volume'],
            y=cv['pressure'] * data_p['pressure'],
            text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * data_p['time']],
            mode='markers',
            marker=dict(
                size=4,
                color='hsla(180, 75%, 50%, 1)',
                symbol='x',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    fig.append_trace(
        pgo.Scatter(
            name='P(V) vs. V [poly-fit/data]',
            x=cv['volume'] * data_v['volume'],
            y=cv['pressure'] * data_v['pressure'],
            text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * data_v['time']],
            mode='markers',
            marker=dict(
                size=4,
                color='hsla(300, 75%, 50%, 1)',
                symbol='x',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    fig.append_trace(
        pgo.Scatter(
            name='P-V [poly-fit/poly-fit]',
            # NOTE: Ensure that the cycle contains start+end points!
            x=cv['volume'] * np.concatenate([volume_fit, volume_fit[:1]]),
            y=cv['pressure'] * np.concatenate([pressure_fit, pressure_fit[:1]]),
            text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * np.concatenate([time_p, time_p[:1]])],
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
            ),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # plot fit-vs-data curves:
    points_ = []

    for _, point in special_p.items():
        if point.ignore or point.ignore_2_d:
            continue
        t_p = point.time
        t_ = (t_p - t_align_p) % T_p
        t_v = ((T_v / T_p) * t_ + t_align_v) % T_v
        p_ = model_p(t_p)
        v_ = model_v(t_v)
        point = point.copy(deep=True)
        point.format = point.format or PointFormat()
        point.format.size += 2
        points_.append((v_, p_, point))

    for _, point in special_v.items():
        if point.ignore or point.ignore_2_d:
            continue
        t_v = point.time
        t_ = (t_v - t_align_v) % T_v
        t_p = ((T_p / T_v) * t_ + t_align_p) % T_p
        p_ = model_p(t_p)
        v_ = model_v(t_v)
        point = point.copy(deep=True)
        point.format = point.format or PointFormat()
        point.format.size -= 2
        points_.append((v_, p_, point))

    for v_, p_, point in points_:
        fmt = point.format
        fig.append_trace(
            pgo.Scatter(
                name=point.name,
                x=[cv['volume'] * v_],
                y=[cv['pressure'] * p_],
                text=[fmt.text or ''],
                textposition=fmt.text_position,
                mode='markers+text',
                marker=dict(
                    symbol=fmt.symbol,
                    size=fmt.size,
                    color=fmt.colour,
                ),
                visible=True if point.found else 'legendonly',
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    # plot special P-V points:
    for _, point in special_pv.items():
        if point.ignore:
            continue
        data = np.asarray([[pt.volume, pt.pressure] for pt in point.data])
        if len(data) == 0:
            continue
        match point.kind:
            case EnumSpecialPointPVKind.PRESSURE | EnumSpecialPointPVKind.VOLUME as kind:
                quantity = kind.value.lower()
                value = cv[quantity] * point.value
                unit = units[quantity]
                # create text label
                text_data = f'{point.name} = {value:.4g} {unit}'
                # plot point
                fig.append_trace(
                    pgo.Scatter(
                        name=point.name,
                        x=cv['volume'] * data[:, 0],
                        y=cv['pressure'] * data[:, 1],
                        text=[text_data],
                        textposition=point.format.text_position,
                        mode='markers+text',
                        marker=dict(
                            symbol=point.format.symbol,
                            size=point.format.size,
                            color=point.format.colour,
                        ),
                        visible=True if point.found else 'legendonly',
                        showlegend=True,
                    ),
                    row=1,
                    col=1,
                )

            case EnumSpecialPointPVKind.GRADIENT:
                value = cv['pressure/volume'] * point.value
                unit = units['pressure/volume']
                data = np.asarray([[pt.volume, pt.pressure] for pt in point.data])
                # insert mid point
                N_pts = len(point.data)
                N_mid = int(len(point.data) / 2)
                data_mid = np.mean(data, axis=0)
                data = np.row_stack([data[:N_mid, :], [data_mid], data[N_mid:, :]])
                # create text label
                text_data = f'{point.name} = {value:.4g} {unit}'
                # plot geometric line + value
                fig.append_trace(
                    pgo.Scatter(
                        name=point.name,
                        x=cv['volume'] * data[:, 0],
                        y=cv['pressure'] * data[:, 1],
                        # TODO: This is inefficient!
                        # There has to be a better way to annotate
                        # + make the text disappear when disabling the curve.
                        text=[''] * N_mid + [text_data] + [''] * (N_pts - N_mid),
                        textposition=point.format.text_position,
                        mode='lines+text',
                        line=dict(
                            width=point.format.size,
                            color=point.format.colour,
                            # 'dash', 'dot', 'dotdash'
                            dash=point.format.symbol,
                        ),
                        visible=True if point.found else 'legendonly',
                        showlegend=True,
                    ),
                    row=1,
                    col=1,
                )

    # save
    path = cfg_output.plot.path.root
    if path is not None:
        path = path.format(label=plot_label, kind='pressure-volume')
        save_image(fig=fig, path=path)

    return fig


# ----------------------------------------------------------------
# SECONDARY METHODS
# ----------------------------------------------------------------


def quick_plot(
    data: pd.DataFrame,
    infos: list[tuple[tuple[int, int], FittedInfoNormalisation]],
    fit_poly: FittedInfoPoly,
    quantity: str,
    renormalise: bool = True,
    N: int = 1000,
) -> Generator[pgo.Figure, None, None]:
    _, info = infos[0]
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
            y=q.values(time),
            mode='lines',
            line_shape='spline',
            line=dict(
                width=1,
                color='black',
            ),
            showlegend=True,
        ),
    ]
    if renormalise:
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
            y=dq.values(time) / T,
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
            y=ddq.values(time) / T**2,
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
    time: NDArray[np.float64],
    values: NDArray[np.float64],
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
    special: dict[str, SpecialPointsConfig] = {},
    showlegend: bool = False,
    showlegend_points: bool = True,
) -> pgo.Figure:
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

    for _, point in special.items():
        if point.ignore:
            continue
        fmt = point.format or PointFormat()
        fig.append_trace(
            pgo.Scatter(
                name=point.name,
                x=[cv_time * point.time],
                y=[cv_value * point.value],
                text=[fmt.text or ''],
                textposition=fmt.text_position,
                mode='markers+text',
                marker=dict(
                    symbol=fmt.symbol,
                    size=fmt.size,
                    color=fmt.colour,
                ),
                visible=True if point.found else 'legendonly',
                showlegend=showlegend_points,
            ),
            row=row,
            col=col,
        )
        fig.add_vline(
            x=cv_time * point.time,
            line_width=0.5,
            line_dash='dash',
            line_color=fmt.colour,
        )

    return fig


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def save_image(fig: pgo.Figure, path: str):
    p = Path(os.path.dirname(path))
    p.mkdir(parents=True, exist_ok=True)
    if path.endswith('.html'):
        fig.write_html(path)
    else:
        fig.write_image(path)
    return


def compute_fitted_curves_poly(
    info: FittedInfoNormalisation,
    fit: FittedInfoPoly,
    special: dict[str, SpecialPointsConfig],
    n_der: int,
    N: int = 1000,
) -> tuple[
    list[dict[str, SpecialPointsConfig]],
    list[Poly],
    NDArray[np.float64],
    list[NDArray[np.float64]],
]:
    t_align = special['align'].time
    T = info.period

    # compute coefficients of (derivatives of) polynomial coefficients
    p = Poly[float](coeff=fit.coefficients)
    polys = [p]
    for _ in range(1, n_der + 1):
        p = p.derivative()
        polys.append(p)

    # compute and shift series
    time = np.linspace(start=0, stop=T, num=N, endpoint=False)
    time = np.concatenate([time[time >= t_align], time[time < t_align]])
    data = np.row_stack([p.values(time) for p in polys])
    time = (time - t_align) % T

    # compute and shift special points
    specials = []
    for k, p in enumerate(polys):
        special_ = {
            key: point.model_copy(deep=True)
            for key, point in special.items()
            if key == 'align' or (not point.ignore and (point.derivatives is None or k in point.derivatives))
        }
        for key, point in special_.items():
            if key == 'align':
                continue
            if k == 0:
                t = (point.time - t_align) % T
                point.time = t
            else:
                t = (point.time - t_align) % T
                point.time = t
                # TODO: Why does this work instead of -?
                t = (point.time + t_align) % T
                point.value = p(t)
        specials.append(special_)

    return specials, polys, time, data


def compute_fitted_curves_trig(
    info: FittedInfoNormalisation,
    fit_trig: FittedInfoTrig,
    intervals: list[tuple[float, float]],
    special: dict[str, SpecialPointsConfig],
    N: int = 1000,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
]:
    t_align = special['align'].time
    T = info.period

    t_min = min([min(I) for I in intervals] or [0])
    t_max = max([max(I) for I in intervals] or [1])
    time = np.linspace(start=t_min, stop=t_max, num=N, endpoint=False)
    time_mod = time % T
    time = np.concatenate([time[time_mod >= t_align], time[time_mod < t_align]])
    time_mod = (time - t_align) % T

    hshift = fit_trig.hshift
    hscale = fit_trig.hscale
    vshift = fit_trig.vshift
    vscale = fit_trig.vscale
    drift = fit_trig.drift
    omega = 2 * pi / hscale
    osc = vshift + drift * time + vscale * np.cos(omega * (time - hshift))

    return time_mod, osc
