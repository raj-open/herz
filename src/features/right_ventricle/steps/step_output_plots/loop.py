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
    'step_output_loop_plot',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP output P-V loop plot', level=LOG_LEVELS.INFO)
def step_output_loop_plot(
    data_p: pd.DataFrame,
    data_v: pd.DataFrame,
    data_pv: pd.DataFrame,
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    poly_p: Poly[float],
    poly_v: Poly[float],
    interpol_trig_p: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    interpol_trig_v: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
    plot_title: str,
    plot_label: str,
    cfg_output: UserOutput,
    N: int = 1000,
) -> pgo.Figure:
    '''
    Creates the 2D loop plot including:

    - P-V-curve data
    - P-V-curve fitted
    - special points from time-series
    - special points for P-V-curve.
    '''
    cv = output_conversions(cfg_output.quantities, units=config.UNITS)
    units = output_units(cfg_output.quantities)

    T_p = info_p.period
    T_v = info_v.period
    T_pv = (T_p + T_v) / 2

    # set up plots
    fig = setup_plot(title=plot_title, cfg=cfg_output, units=units)

    # plot data / curve
    for subplot in plot_data_vs_data(data_pv, T_pv, visible=True, cv=cv, units=units):
        fig.append_trace(subplot, row=1, col=1)

    for subplot in plot_data_vs_fits(data_p=data_p, data_v=data_v, poly_p=poly_p, poly_v=poly_v, T_p=T_p, T_v=T_v, visible=False, cv=cv, units=units):  # fmt: skip
        fig.append_trace(subplot, row=1, col=1)

    for subplot in plot_poly_fit(poly_p=poly_p, poly_v=poly_v, T_p=T_p, T_v=T_v, T_pv=T_pv, N=N, visible=True, cv=cv, units=units):  # fmt: skip
        fig.append_trace(subplot, row=1, col=1)

    # plot interpolated trig-curve
    for subplot in plot_interpolated_trig_curve(
        interpol_trig_p,
        interpol_trig_v,
        info_p=info_p,
        info_v=info_v,
        poly_p=poly_p,
        poly_v=poly_v,
        usehull=False,
        visible=False,
        N=N,
        cv=cv,
        units=units,
    ):
        fig.append_trace(subplot, row=1, col=1)

    # plot exp-curve
    for subplot in plot_exp_curve(fitinfo_exp, visible=True, N=N, cv=cv, units=units):
        fig.append_trace(subplot, row=1, col=1)

    # plot special points from time-series
    for subplot in plot_special_points(info_p=info_p, info_v=info_v, poly_p=poly_p, poly_v=poly_v, special_p=special_p, special_v=special_v, cv=cv, units=units):  # fmt: skip
        fig.append_trace(subplot, row=1, col=1)

    # plot special points for P-V-curve
    for key, point in special_pv.items():
        if point.ignore:
            continue
        for subplot in plot_special_points_pv(key, point, cv=cv, units=units):
            fig.append_trace(subplot, row=1, col=1)

    # save
    path = cfg_output.plot.path.root
    if path is not None:
        path = path.format(label=plot_label, kind='pressure-volume')
        save_image(fig=fig, path=path)

    return fig


# ----------------------------------------------------------------
# SECONDARY METHODS
# ----------------------------------------------------------------


def setup_plot(
    title: str,
    cfg: UserOutput,
    units: dict[str, str],
) -> pgo.Figure:
    '''
    Initialises plot.
    '''
    cfg_font = cfg.plot.font
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
            text=title,
            x=0.5,
            y=0.95,
            font=dict(
                family=cfg_font.family,
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
            font=dict(
                family=cfg_font.family,
                size=cfg_font.size_legend,
            ),
        ),
        updatemenus=[],  # use to add buttons to plots
    )
    return fig


def plot_data_vs_data(
    data: pd.DataFrame,
    T_pv: float,
    visible: bool,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots (linearly interpolated) data points.
    '''
    perc = data['time']
    t = T_pv * perc

    yield pgo.Scatter(
        name='P vs. V [data/data]',
        x=cv['volume'] * data['volume'],
        y=cv['pressure'] * data['pressure'],
        text=[f"ca. {tt:.0f}{units['time']} ({pc:.2%})" for pc, tt in zip(perc, cv['time'] * t)],
        mode='markers',
        marker=dict(
            size=3,
            color='hsla(0, 100%, 0%, 0.5)',
            symbol='cross',
        ),
        visible=True if visible else 'legendonly',
        showlegend=True,
    )


def plot_data_vs_fits(
    data_p: pd.DataFrame,
    data_v: pd.DataFrame,
    poly_p: Poly[float],
    poly_v: Poly[float],
    T_p: float,
    T_v: float,
    visible: bool,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots data points vs. fits
    '''
    # fit each 'other' measurement to each time-series
    time_p = data_p['time']
    data_p_volume = poly_v.values((T_v / T_p) * time_p)
    time_v = data_v['time']
    data_v_pressure = poly_p.values((T_p / T_v) * time_v)

    yield pgo.Scatter(
        name='P vs. V(P) [data/poly-fit]',
        x=cv['volume'] * data_p_volume,
        y=cv['pressure'] * data_p['pressure'],
        text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * time_p],
        mode='markers',
        marker=dict(
            size=3,
            color='hsla(180, 75%, 50%, 1)',
            symbol='x',
        ),
        visible=True if visible else 'legendonly',
        showlegend=True,
    )

    yield pgo.Scatter(
        name='P(V) vs. V [poly-fit/data]',
        x=cv['volume'] * data_v['volume'],
        y=cv['pressure'] * data_v_pressure,
        text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * time_v],
        mode='markers',
        marker=dict(
            size=3,
            color='hsla(300, 75%, 50%, 1)',
            symbol='x',
        ),
        visible=True if visible else 'legendonly',
        showlegend=True,
    )


def plot_poly_fit(
    poly_p: Poly[float],
    poly_v: Poly[float],
    T_p: float,
    T_v: float,
    T_pv: float,
    N: int,
    visible: bool,
    cv: dict[str, float],
    units: dict[str, str],
):
    # compute series for fitted curves
    time = np.linspace(start=0, stop=1, num=N, endpoint=False)
    pressure_fit = poly_p.values(T_p * time)
    volume_fit = poly_v.values(T_v * time)
    time = T_pv * time

    # make them periodic
    time = np.concatenate([time, [T_pv]])
    pressure_fit = np.concatenate([pressure_fit, pressure_fit[:1]])
    volume_fit = np.concatenate([volume_fit, volume_fit[:1]])

    yield pgo.Scatter(
        name='P-V [poly-fit/poly-fit]',
        # NOTE: Ensure that the cycle contains start+end points!
        x=cv['volume'] * volume_fit,
        y=cv['pressure'] * pressure_fit,
        text=[f'{tt:.0f}{units["time"]}' for tt in cv['time'] * time],
        mode='lines',
        line_shape='spline',
        line=dict(
            width=3,
            color='hsla(0, 100%, 0%, 0.5)',
        ),
        visible=True if visible else 'legendonly',
        showlegend=True,
    )


def plot_interpolated_trig_curve(
    interpol_trig_p: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    interpol_trig_v: tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]],
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    poly_p: Poly[float],
    poly_v: Poly[float],
    usehull: bool,
    visible: bool,
    N: int,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots fitted trig curves against data.
    '''
    T_p = info_p.period
    T_v = info_v.period
    fit_p, _, _ = interpol_trig_p
    fit_v, _, _ = interpol_trig_v

    if fit_p is not None:
        _, paxis, vaxis = compute_fitted_curves_trig(
            interpol_trig_p,
            info_p,
            usehull=usehull,
            N=N,
            cv_time=cv['time'],
            cv_value=cv['pressure'],
            cv_aux=cv['volume'],
            auxiliary=lambda t: poly_v.values((T_v / T_p) * t),
        )
        yield pgo.Scatter(
            name='P(t) ~ cos(ωt)',
            x=vaxis,
            y=paxis,
            mode='lines',
            line=dict(
                width=5,
                color='hsla(100, 100%, 25%, 0.75)',
            ),
            visible=True if visible else 'legendonly',
            showlegend=True,
        )

    if fit_v is not None:
        _, vaxis, paxis = compute_fitted_curves_trig(
            interpol_trig_v,
            info_v,
            usehull=usehull,
            N=N,
            cv_time=cv['time'],
            cv_value=cv['volume'],
            cv_aux=cv['pressure'],
            auxiliary=lambda t: poly_p.values((T_p / T_v) * t),
        )
        yield pgo.Scatter(
            name='V(t) ~ cos(ωt)',
            x=vaxis,
            y=paxis,
            mode='lines',
            line=dict(
                width=5,
                color='hsla(100, 100%, 25%, 0.75)',
            ),
            visible=True if visible else 'legendonly',
            showlegend=True,
        )

    return


def plot_exp_curve(
    fitinfo: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    visible: bool,
    N: int,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creates subplot for P(V) ~ exp(βV) fitting.
    '''
    # plot exp-curve
    vaxis, paxis = compute_fitted_curves_exp(fitinfo=fitinfo, N=N)
    yield pgo.Scatter(
        name='P(V) ~ exp(βV)',
        x=cv['volume'] * vaxis,
        y=cv['pressure'] * paxis,
        mode='lines',
        line_shape='spline',
        line=dict(
            width=5,
            color='hsla(235, 100%, 50%, 0.75)',
            # color='hsla(60, 100%, 50%, 0.5)',
        ),
        visible=True if visible else 'legendonly',
        showlegend=True,
    )


def plot_special_points(
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    poly_p: Poly[float],
    poly_v: Poly[float],
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creates subplot for all time-domain special points.
    '''
    T_p = info_p.period
    T_v = info_v.period

    points_ = []
    for _, point in special_p.items():
        if point.ignore or point.ignore_2_d:
            continue
        t_p = point.time
        t_v = (T_v / T_p) * t_p
        p_ = poly_p(t_p)
        v_ = poly_v(t_v)
        point = point.copy(deep=True)
        point.format = point.format or PointFormat()
        point.format.size += 2
        points_.append((v_, p_, point))

    for _, point in special_v.items():
        if point.ignore or point.ignore_2_d:
            continue
        t_v = point.time
        t_p = (T_p / T_v) * t_v
        p_ = poly_p(t_p)
        v_ = poly_v(t_v)
        point = point.copy(deep=True)
        point.format = point.format or PointFormat()
        point.format.size -= 2
        points_.append((v_, p_, point))

    for v_, p_, point in points_:
        fmt = point.format
        yield pgo.Scatter(
            name=point.name,
            x=[cv['volume'] * v_],
            y=[cv['pressure'] * p_],
            # text=[f'{point.name}'],
            # textposition=fmt.text_position,
            # mode='markers+text',
            mode='markers',
            marker=dict(
                symbol=fmt.symbol,
                size=fmt.size,
                color=fmt.colour,
            ),
            visible=True if point.found else 'legendonly',
            showlegend=True,
        )


def plot_special_points_pv(
    key: str,
    point: SpecialPointsConfigPV,
    cv: dict[str, float],
    units: dict[str, str],
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creats subplots for a PV-special point and/or associated line.
    '''
    visible = point.visible and point.found
    data = np.asarray([[pt.volume, pt.pressure] for pt in point.data])

    if len(data) == 0:
        return

    match point.kind:
        case EnumSpecialPointPVKind.PRESSURE | EnumSpecialPointPVKind.VOLUME as kind:
            quantity = kind.value.lower()
            value = cv[quantity] * point.value
            unit = units[quantity]
            # plot point
            yield pgo.Scatter(
                name=f'{point.name} = {value:.4g} {unit}',
                x=cv['volume'] * data[:, 0],
                y=cv['pressure'] * data[:, 1],
                text=[point.name],
                textposition=point.format.text_position,
                mode='markers+text',
                marker=dict(
                    symbol=point.format.symbol,
                    size=point.format.size,
                    color=point.format.colour,
                ),
                visible=True if visible else 'legendonly',
                showlegend=True,
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
            # plot geometric line + value
            yield pgo.Scatter(
                name=f'{point.name} = {value:.4g} {unit}',
                x=cv['volume'] * data[:, 0],
                y=cv['pressure'] * data[:, 1],
                # TODO: This is inefficient!
                # There has to be a better way to annotate
                # + make the text disappear when disabling the curve.
                text=[''] * N_mid + [point.name] + [''] * (N_pts - N_mid),
                textposition=point.format.text_position,
                mode='lines+text',
                line=dict(
                    width=point.format.size,
                    color=point.format.colour,
                    # 'dash', 'dot', 'dotdash'
                    dash=point.format.symbol,
                ),
                visible=True if visible else 'legendonly',
                showlegend=True,
            )
