#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from .....thirdparty.maths import *
from .....thirdparty.plots import *
from .....thirdparty.system import *
from .....thirdparty.types import *

from .....models.fitting import *
from .....models.polynomials import *
from .....algorithms.fitting.trigonometric import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'add_plot_time_series',
    'add_plot_point_plus_vline',
    'compute_fitted_curves_exp',
    'compute_fitted_curves_poly',
    'compute_fitted_curves_trig',
    'save_image',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def add_plot_time_series(
    name: Optional[str],
    time: NDArray[np.float64],
    values: NDArray[np.float64],
    cv_time: float = 1.0,
    cv_value: float = 1.0,
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
    showlegend: bool = False,
) -> Generator[pgo.Scatter, None, None]:
    '''
    Creates a subplot for series.
    '''
    yield pgo.Scatter(
        name=name,
        x=cv_time * time,
        y=cv_value * values,
        text=[text or name for _ in time],
        mode=mode,
        line=line if mode == 'lines' else None,
        line_shape='spline',
        marker=marker if mode == 'markers' else None,
        showlegend=showlegend,
    )


def add_plot_point_plus_vline(
    fig: pgo.Figure,
    key: str,
    point: SpecialPointsConfig,
    cv_time: float = 1.0,
    cv_value: float = 1.0,
    showlegend: bool = True,
) -> Generator[pgo.Scatter, None, None]:
    '''
    Plots points + associated vline.
    '''
    # DEV-NOTE: externally, the yielded item is processed first
    # then the below effect takes place.
    fmt = point.format or PointFormat()
    yield pgo.Scatter(
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
        showlegend=showlegend,
    )
    fig.add_vline(
        x=cv_time * point.time,
        line_width=0.5,
        line_dash='dash',
        line_color=fmt.colour,
    )


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
    poly: Poly[float],
    special: dict[str, SpecialPointsConfig],
    n_der: int = 0,
    N: int = 1000,
) -> tuple[
    list[dict[str, SpecialPointsConfig]],
    list[Poly],
    NDArray[np.float64],
    list[NDArray[np.float64]],
]:
    T = info.period

    # compute coefficients of (derivatives of) polynomial coefficients
    p = poly
    polys = [p]
    for _ in range(1, n_der + 1):
        p = p.derivative()
        polys.append(p)

    # compute series
    time = np.linspace(start=0, stop=T, num=N, endpoint=False)
    data = np.row_stack([p.values(time) for p in polys])

    # compute derivatives of special points
    specials = []
    for k, p in enumerate(polys):
        special_ = {
            key: point.model_copy(deep=True)
            for key, point in special.items()
            if key == 'align' or (not point.ignore and (point.derivatives is None or k in point.derivatives))
        }
        for key, point in special_.items():
            if k == 0 or key == 'align':
                continue
            point.value = p(point.time)
        specials.append(special_)

    return time, data, specials


def compute_fitted_curves_trig(
    fitinfo: tuple[FittedInfoTrig, list[tuple[float, float]], list[tuple[float, float]]],
    info: FittedInfoNormalisation,
    usehull: bool,
    N: int,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
]:
    '''
    Prepares a data-series for fitted trig curve on the entire hull.
    '''
    T = info.period
    fit, hull, intervals = fitinfo
    if usehull:
        time = np.concatenate([np.linspace(start=a, stop=b, num=N, endpoint=False) for a, b in hull])
    else:
        time = np.concatenate([np.linspace(start=a, stop=b, num=N, endpoint=False) for a, b in intervals])

    omega = 2 * pi / fit.hscale
    osc = fit.vshift + fit.drift * time + fit.vscale * np.cos(omega * (time - fit.hshift))

    # put time in periodic mode
    time = time % T

    return time, osc


def compute_fitted_curves_exp(
    fitinfo: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    N: int,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
]:
    fit_exp, (vmin, vmax), (pmin, pmax) = fitinfo
    vaxis = np.linspace(start=vmin, stop=vmax, endpoint=True, num=N)
    vshift = fit_exp.vshift
    vscale = fit_exp.vscale
    hscale = fit_exp.hscale
    paxis = vshift + vscale * np.exp(vaxis / hscale)
    return vaxis, paxis
