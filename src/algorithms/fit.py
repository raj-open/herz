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
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'fit_poly_cycle',
    'fit_poly_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def fit_poly_cycles(
    t: np.ndarray,
    x: np.ndarray,
    cycles: list[int],
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
    average: bool = False,
) -> list[FittedInfo]:
    '''
    Fits 'certain' polynomials to cycles in such a way,
    that special attributes can be extracted.
    '''
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    # fit each cycle
    N = len(t)
    x_fit = np.zeros(shape=(N,), dtype=float)
    infos = [[]] * len(windows)
    # due to normalisation, force the following condition
    conds = conds[:]
    conds.append(PolyDerCondition(derivative=0, time=0))
    conds.append(PolyDerCondition(derivative=0, time=1))
    for k, (i1, i2) in enumerate(windows):
        # scale time
        tt, T = normalise_to_unit_interval(t[i1:i2])
        # remove drift
        c, m, s, xx = normalise_interpolated_drift(tt, x[i1:i2], T=1)
        # compute fitted curve
        coeff = fit_poly_cycle(t=tt, x=xx, deg=deg, conds=conds)
        params = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
        infos[k] = FittedInfo(coefficients=coeff, normalisation=params)

    # --------------------------------
    # NOTE:
    # If all cycles are to be fit simultaenously by a single polynomial,
    # then since a method via ONB is, the optimal solution
    # (least L^2-distance) is the average.
    # Let (x⁽ᵏ⁾(t))ₖ be the respective (interpolated+normalised) curves in C[0, T].
    # Let x(t) := 1/n ∑ₖ x⁽ᵏ⁾(t) the avarage in C[0, T].
    # Then
    #
    #    res := 1/n · ∑ₖ ‖p - x⁽ᵏ⁾‖²
    #      = 1/n · ∑ₖ ‖p‖² + ‖x⁽ᵏ⁾‖² + 2Re ⟨x⁽ᵏ⁾, p⟩
    #      = const + ‖p‖² + 2Re ⟨x, p⟩
    #      = const + ‖x‖² + ‖p‖² + 2Re ⟨x, p⟩
    #      = const + ‖p - x‖²
    #
    # Hence to res minimsed ⟺ p minimised for the average, x(t).
    # We do not have access to x, since the x⁽ᵏ⁾ are not comensurable.
    # However, letting p⁽ᵏ⁾ be minimised for each x⁽ᵏ⁾,
    # one has via the ONB (qⱼ)ⱼ
    #
    #    p optimal for x
    #    ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨x, qⱼ⟩
    #    ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨1/n ∑ₖ x⁽ᵏ⁾, qⱼ⟩
    #    ⟺ ∀j: ⟨p, qⱼ⟩ = 1/n ∑ₖ ⟨x⁽ᵏ⁾, qⱼ⟩
    #    ⟺ ∀j: ⟨p, qⱼ⟩ = 1/n ∑ₖ ⟨p⁽ᵏ⁾, qⱼ⟩
    #    ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨1/n ∑ₖ p⁽ᵏ⁾, qⱼ⟩
    #    ⟺ p = 1/n ∑ₖ p⁽ᵏ⁾
    #
    # Hence the coefficients for p are just the average
    # of the coefficients of the p⁽ᵏ⁾.
    # --------------------------------
    if average:
        coeff = np.mean(np.asarray([info.coefficients for info in infos]), axis=0).tolist()
        T = np.median(
            np.asarray([info.normalisation.period for info in infos]), axis=0
        ).tolist()
        c = np.median(
            np.asarray([info.normalisation.intercept for info in infos]), axis=0
        ).tolist()
        m = np.median(
            np.asarray([info.normalisation.gradient for info in infos]), axis=0
        ).tolist()
        s = np.median(np.asarray([info.normalisation.scale for info in infos]), axis=0).tolist()
        params = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
        infos.append(FittedInfo(coefficients=coeff, normalisation=params))

    return infos


def fit_poly_cycle(
    t: np.ndarray,
    x: np.ndarray,
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
) -> list[float]:
    '''
    Fits 'certain' polynomials to a cycle in such a way,
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
    '''
    Q = onb_conditions(deg=deg, conds=conds)
    coeff = onb_spectrum(t=t, x=x, Q=Q, T=1, in_standard_basis=True)
    return coeff


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
        # coeff_d1 = get_derivative_coefficients(coeff, n=1)
        # coeff_dn = get_derivative_coefficients(coeff, n=n)
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
