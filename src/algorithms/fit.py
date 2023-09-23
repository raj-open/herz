#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.types import *

from .peaks import *
from .cycles import *
from ..core.utils import *
from ..core.poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'fit_poly_ventricular_cycle',
    'fit_poly_ventricular_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def fit_poly_ventricular_cycles(
    t: np.ndarray,
    x: np.ndarray,
    cycles: list[int],
    n: int = 3,
    h: int = 7,
) -> np.ndarray:
    '''
    Fits 'certain' polynomials to pressure cycles in such a way,
    that special attributes can be extracted.
    '''
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    # fit each cycle
    N = len(t)
    x_fit = np.zeros(shape=(N,), dtype=float)
    coeffs = [[]] * len(windows)
    for k, (i1, i2) in enumerate(windows):
        xx = x[i1:i2]
        tt, T = normalise_to_unit_interval(t[i1:i2])
        x_fit[i1:i2], coeffs[k] = fit_poly_ventricular_cycle(t=tt, x=xx, n=n, h=h)

    return x_fit, coeffs


def fit_poly_ventricular_cycle(
    t: np.ndarray,
    x: np.ndarray,
    n: int,
    h: int,
) -> tuple[np.ndarray, list[tuple[int, float]]]:
    '''
    Fits 'certain' polynomials to a pressure cycle in such a way,
    that special attributes can be extracted.

    @inputs
    - `t` - a `1`-dimensional array of time-values normalised to [0, 1].
    - `x` - a `1`-dimensional array of values in a cycle.
    - `dt` - the time increment.

    @returns
    - `[ (k, c_k) … ]` whereby `c_k` is the coefficient of the monom `t^k`,
      Here the polynomial is to be understood as being paramterised
      over time uniformly on `[0, T]`.
    - the fit polynomial

    ## Assumptions ##

    - Assume `x(0) = x(1) =` local maximum.
    - The `n-1`-th derivative `x⁽ⁿ⁻¹⁾` is a polynomial,
      with `h` alternating peaks/troughs,
      whereby the two end points `0` and `T` are peaks.
    - This implies that the `n`-th derivative `x⁽ⁿ⁾` is a polynomial
      with `h` zeros (and hence of degree `h`),
      two of which are the end points.
      So `x` is a polynomial of degree `n + h`.
    '''

    d = h + n
    opt = [
        (0, 0.0),
        (0, 1.0),
        (1, 0.0),
        (1, 1.0),
        (n, 0.0),
        (n, 1.0),
    ]
    A = force_poly_conditions(d=d, opt=opt)
    Q = onb_conditions(d=d, opt=opt)

    coeff = onb_spectrum(
        t=t,
        x=x - x[0],
        Q=Q,
        T=1.0,
        in_standard_basis=True,
    )

    coeff[0] = x[0]
    x_fit = poly(t, *coeff)

    return x_fit, coeff


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def effective_coefficients_pq(n: int, *coeff_q: float) -> list[float]:
    '''
    Determines coefficients of `p(t)·q(t)`,
    based on coefficients of `q(t)`,
    where `p(t) = t·(t - 1)`.
    '''
    m = len(coeff_q)
    coeff_q = np.asarray(coeff_q, dtype=float)
    coeff_pq = np.zeros(shape=(m + 2,), dtype=float)
    coeff_pq[2:] += coeff_q
    coeff_pq[1:-1] -= coeff_q
    return coeff_pq


def effective_coefficients(n: int, *coeff: float) -> list[float]:
    '''
    Determines coefficients of `x(t)` based on algebraic constraints
    on coefficients that occur in polynomial for `x´´´(t)`.
    '''
    coeff_x_nth = effective_coefficients_pq(n, *coeff[n:])
    coeff_x = list(coeff[:n]) + [c / (k + n) for k, c in enumerate(coeff_x_nth)]
    # force x(0) = 0
    coeff_x[0] = 0
    # force x(1) = 0
    coeff_x[2] = 0
    coeff_x[2] = -sum(coeff_x)
    # force x´(0) = 0
    coeff_x[1] = 0
    # # force x´(1) = 0
    # coeff_x[2] = 0
    # coef_x_1st = [k * c for k, c in enumerate(coeff_x)]
    # coeff_x[2] = -1 / 2 * sum(coef_x_1st)
    return coeff_x


def objective_function(n: int):
    fct = fit_function(n)

    def obj(params: lmfit.Parameters, t: np.ndarray, x: np.ndarray):
        coeff = [params[key].value for key in params]
        # coeff_d1 = derivative_coefficients(coeff, n=1)
        # coeff_dn = derivative_coefficients(coeff, n=n)
        # # polynomial x´(0) and x´(1) must be 0 and x⁽ⁿ⁾(0) and x⁽ⁿ⁾(1) must be 0:
        # values = np.asarray([
        #     coeff_d1[0],
        #     sum(coeff_d1),
        #     coeff_dn[0],
        #     sum(coeff_dn),
        # ]);
        # d = np.linalg.norm(values)
        # fit curve should be close to original data:
        # x_fit = poly(t, *coeff)
        # res = max(d, 1) * x - x_fit
        x_fit = fct(t, *coeff)
        res = x - x_fit
        return res

    return obj


def fit_function(n: int):
    '''
    Polynomial function for `x(t)` based on
    coefficients that occur in polynomial for `x⁽ⁿ⁾(t)`
    plus coefficients that arised during integration.

    NOTE: assumes time is normalised to `[0, 1]`

    Forces:

    - x´(t) = 0 for t ∈ {0, 1}
    - x⁽ⁿ⁾(t) = 0 for t ∈ {0, 1}
    '''

    def fct(t: float, *coeff: float):
        coeff_x = effective_coefficients(n, *coeff)
        x = poly(t, *coeff_x)
        return x

    return fct
