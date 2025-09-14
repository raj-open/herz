#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....algorithms.fitting.exponential import *
from ....core.constants import *
from ....core.log import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....queries.fitting import *
from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_fit_exp",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP fit exp-model to P-V curve", level=LOG_LEVELS.INFO)
def step_fit_exp(
    data: pd.DataFrame,
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    poly_p: Poly[float],
    poly_v: Poly[float],
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    cfg_fit: FitExpConfig,
) -> tuple[
    FittedInfoExp,
    tuple[float, float],
    tuple[float, float],
]:
    """
    Fits trig curve to P-V data points.
    """
    # get environment variables for settings
    env = {
        "P": special_p,
        "V": special_v,
        "T_p": info_p.period,
        "T_v": info_v.period,
    }
    conf_ = cfg_fit.points
    env = get_schema_from_settings(conf_, env=env)
    pmin = env["pmin"]
    vmax = env["vmax"]

    # reduce data to bounds - NOTE: need to do this before computing heuristics!
    data, range_v, range_p = restrict_data_to_intervals(
        data=data,
        info_p=info_p,
        info_v=info_v,
        env=env,
    )

    # add heuristics to env
    compute_heuristics(
        data=data,
        info_p=info_p,
        info_v=info_v,
        poly_p=poly_p,
        poly_v=poly_v,
        y_min=pmin,
    )
    env = env | {"beta_local": data["beta"]}

    # add bounds for non-linear part
    conf_ = cfg_fit.conditions
    beta_min, beta_max = get_bounds_from_settings(conf_, env=env)
    env = env | {"beta_min": beta_min, "beta_max": beta_max}

    # add initial guess
    conf_ = cfg_fit.initial
    fit_init = get_initialisation_from_settings(conf_, env=env)

    # reformat to numpy-array - and shift v-axis for stability
    arr = reformat_data(data, vmax)

    # perpare parts for solver depending upon settings
    scale = fit_options_scale_data(arr)
    gen_grad = fit_options_gradients_data(arr)

    # perform fitting
    conf_ = cfg_fit.solver
    fit, loss, dx = fit_exponential_curve(
        mode=conf_.mode,
        scale=scale,
        gen_grad=gen_grad,
        fit_init=fit_init,
        beta_min=beta_min,
        beta_max=beta_max,
        N_max=conf_.n_max,
        eps=SOLVE_TOLERANCE,
    )

    """
    This computes model
    ```
    P(V) ≈ A + B·e^{β·(V - V_max)}
         = A + (B·e^{-β·V_max}) e^{β·V}
    ```
    thus need to adjust vscale.
    """
    fit.vscale = fit.vscale * math.exp(-vmax / fit.hscale)

    log_debug_wrapped(lambda: message_result(fit, loss, dx))
    return fit, range_v, range_p


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def message_result(
    fit: FittedInfoExp,
    loss: float,
    dx: float,
):
    return dedent(
        f"""
        Parameters of exponential model:
        (  P(V) = A + B·e^{{β·V}}  )
        ----
        A:  {fit.vshift:.4g}
        B:  {fit.vscale:.4g}
        β:  {1 / fit.hscale:.4g}
        ----
        Relativised loss of the approximation: {loss:.4g}
        Final movement of parameters during computation: {dx:.4e}
        """
    )


def compute_heuristics(
    data: pd.DataFrame,
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    poly_p: Poly[float],
    poly_v: Poly[float],
    y_min: float,
    safety: float = 1,
) -> pd.DataFrame:
    """
    Determines the instaneous values of β
    and thereby heuristic-means for the
    of range of possible β values.
    """
    T_p = info_p.period
    T_v = info_v.period
    t = data["time"].to_numpy()
    t_p = T_p * t
    t_v = T_v * t

    P = poly_p
    dP = poly_p.derivative()
    dV = poly_v.derivative()
    P_values = P.values(t_p) - y_min + safety
    beta = 2 * (dP.values(t_p) / P_values) / dV.values(t_v)
    data["beta"] = beta
    return data


def restrict_data_to_intervals(
    data: pd.DataFrame,
    env: dict[str, float],
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
) -> tuple[
    pd.DataFrame,
    tuple[float, float],
    tuple[float, float],
]:
    """
    Restricts time and values of data to intervals.
    """
    T_p = info_p.period
    T_v = info_v.period

    vmin, vmax = env["vmin"], env["vmax"]
    pmin, pmax = env["pmin"], env["pmax"]

    tmin_v, tmax_v = env["tmin_v"], env["tmax_v"]
    tmin_p, tmax_p = env["tmin_p"], env["tmax_p"]
    tmin = max(tmin_v / T_v, tmin_p / T_p)
    tmax = min(tmax_v / T_v, tmax_p / T_p)

    t = data["time"]
    data = data[(tmin <= t) & (t <= tmax)]

    return data, (vmin, vmax), (pmin, pmax)


def reformat_data(
    data: pd.DataFrame,
    x_max: float,
) -> NDArray[np.float64]:
    """
    Reformats data frame to an np-array containing

    - t = time
    - dt = dt
    - x = V
    - y = P
    """
    t = data["time"].to_numpy()
    dt = data["dt"].to_numpy()
    x = data["volume"].to_numpy()
    y = data["pressure"].to_numpy()
    data = np.asarray([t, dt, x - x_max, y]).T
    return data
