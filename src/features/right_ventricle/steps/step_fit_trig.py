#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.code import *
from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.types import *

from ....core.log import *
from ....core.constants import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....algorithms.anomalies import *
from ....algorithms.fitting.trigonometric import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_fit_trig',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP fit trigonometric-model to data/poly-model', level=LOG_LEVELS.INFO)
def step_fit_trig(
    data: pd.DataFrame,
    poly: Poly[float],
    special: dict[str, SpecialPointsConfig],
    symb: str,
    cfg_fit: FitTrigConfig,
) -> tuple[
    FittedInfoTrig,
    list[tuple[float, float]],
    list[tuple[float, float]],
]:
    '''
    Fits trig curve to normalised model.
    '''
    # NOTE: polynomial must be rendered cyclic
    # to allow for consistent values upon shifting
    offset = 0
    period = 1

    # get environment variables for settings
    conf_ = cfg_fit.points
    env = {
        f'{symb.upper()}': special,
        f'T_{symb.lower()}': period,
    }
    env = get_schema_from_settings(conf_, env=env)

    # add bounds for non-linear part
    conf_ = cfg_fit.conditions
    omega_min, omega_max = get_bounds_from_settings(conf_, env=env)
    env = env | {'omega_min': omega_min, 'omega_max': omega_max}

    # determine initial guess
    conf_ = cfg_fit.initial
    fit_init = get_initialisation_from_settings(conf_, env=env)

    # get first part of restrictions based on environment
    conf_ = cfg_fit.intervals
    intervals = get_spatial_domain_from_settings(conf_, env=env)
    hull = [(min(a for a, b in intervals), max(b for a, b in intervals))]

    # perpare parts for solver depending upon settings
    conf_ = cfg_fit.solver
    match conf_.model:
        case EnumModelKind.DATA:
            # reduce data to bounds
            data = restrict_data_to_intervals(
                data=data,
                intervals=intervals,
                offset=offset,
                period=period,
            )
            # compute parts
            scale = fit_options_scale_data(data)
            gen_grad = fit_options_gradients_data(data, drift=conf_.drift)

        case EnumModelKind.POLY_MODEL:
            # reduce model to bounds
            models, intervals = resolve_to_piecewise_functions(poly=poly, intervals=intervals)
            # compute parts
            scale = fit_options_scale_poly_model(models, intervals)
            gen_grad = fit_options_gradients_poly_model(models, intervals, drift=conf_.drift)

        case _ as m:
            raise ValueError(f'No method available for running trig-fit algorithm for {m.value}.')

    # perform fitting
    fit, loss, dx = fit_trigonometric_curve(
        mode=conf_.mode,
        scale=scale,
        gen_grad=gen_grad,
        fit_init=fit_init,
        omega_min=omega_min,
        omega_max=omega_max,
        N_max=conf_.n_max,
        eps=SOLVE_TOLERANCE,
    )

    log_debug_wrapped(lambda: message_result(fit, loss, dx))
    return fit, hull, intervals


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def message_result(
    fit: FittedInfoTrig,
    loss: float,
    dx: float,
):
    return dedent(
        f'''
        Parameters of trigonometric model:
        (  Shift/Linear + Oscillation  )
        ----
        period:    {fit.hscale}
        amplitude: {fit.vscale}
        iso-max:   ({fit.hshift}, {fit.vshift + fit.vscale})
        ----
        Relativised loss of the approximation: {loss:.4g}
        Final movement of parameters during computation: {dx:.4e}
        '''
    )


def convert_dom_to_interval(
    I: RootModel[list[str]],
    env: dict[str, float],
) -> tuple[float, float]:
    '''
    Determines the value of the interval corresponding
    to a spatial configuration of an interval.
    '''
    key1, key2 = I.root
    return (env[key1], env[key2])


def resolve_to_piecewise_functions(
    poly: Poly[float],
    intervals: Iterable[tuple[float, float]],
) -> tuple[
    list[Poly[float]],
    list[tuple[float, float]],
]:
    '''
    Resolve cyclic polynomial to non-cyclic parts
    on disjoint (sub)intervals each contained within a full cycle.
    '''
    parts = list(poly.resolve_piecewise(*intervals))
    models = [q for q, a, b in parts]
    intervals = [(a, b) for q, a, b in parts]
    return models, intervals


def restrict_data_to_intervals(
    data: pd.DataFrame,
    intervals: Iterable[tuple[float, float]],
    offset: float,
    period: float,
) -> NDArray[np.float64]:
    '''
    Restricts time and values of data to intervals.
    '''
    # filter data
    intervals_ = [(offset + (a - offset) % period, offset + (b - offset) % period) for a, b in intervals]
    data = np.asarray(
        [
            data['time'],
            data['dt'],
            data['value'],
        ]
    ).T
    datas = [data[(a_ <= data[:, 0]) & (data[:, 0] < b_), :] for a_, b_ in intervals_]
    # rewrite time-values
    times = [data[:, 0] + (a - a_) for (a, b), (a_, b_), data in zip(intervals, intervals_, datas)]
    delta = [data[:, 1] for data in datas]
    values = [data[:, 2] for data in datas]
    # store in data structure
    data = np.row_stack([np.column_stack([t, dt, x]) for t, dt, x in zip(times, delta, values)])
    return data
