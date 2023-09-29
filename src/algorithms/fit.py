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
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
) -> list[tuple[tuple[int, int], FittedInfo]]:
    '''
    Fits polynomial to cycles of a time-series:
    - minimises wrt. the L²-norm
    - forces certain conditions on n'th-derivatives at certain time points
    '''
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    # due to normalisation (drift-removal), force extra boundary conditions
    conds = conds[:]
    conds.append(PolyDerCondition(derivative=0, time=0.0))
    conds.append(PolyDerCondition(derivative=0, time=1.0))

    # refine conditions + determine degree of polynomial needed
    conds, deg = refine_conditions_determine_degree(conds)

    # fit each cycle
    fitinfos = []
    for i1, i2 in windows:
        # scale time
        tt, T = normalise_to_unit_interval(t[i1:i2])
        # remove drift
        c, m, s, xx = normalise_interpolated_drift(tt, x[i1:i2], T=1, periodic=True)
        # compute fitted curve
        coeff = fit_poly_cycle(t=tt, x=xx, deg=deg, conds=conds)
        params = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
        info = FittedInfo(coefficients=coeff, normalisation=params)
        fitinfos.append(((i1, i2), info))

    # --------------------------------
    # NOTE:
    # If all cycles are to be fit simultaenously by a single polynomial,
    # then since a method via ONB is, the optimal solution
    # (least L²-distance) is the average.
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
    coeff = np.mean(np.asarray([info.coefficients for _, info in fitinfos]), axis=0).tolist()  # fmt: skip
    T = np.median(np.asarray([info.normalisation.period for _, info in fitinfos]), axis=0).tolist()  # fmt: skip
    c = np.median(np.asarray([info.normalisation.intercept for _, info in fitinfos]), axis=0).tolist()  # fmt: skip
    m = np.median(np.asarray([info.normalisation.gradient for _, info in fitinfos]), axis=0).tolist()  # fmt: skip
    s = np.median(np.asarray([info.normalisation.scale for _, info in fitinfos]), axis=0).tolist()  # fmt: skip
    params = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
    info = FittedInfo(coefficients=coeff, normalisation=params)
    fitinfos.append(((-1, -1), info))

    return fitinfos


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


def refine_conditions_determine_degree(
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
) -> tuple[list[PolyDerCondition | PolyIntCondition], int]:
    conds_crit = [cond for cond in conds if isinstance(cond, PolyCritCondition)]
    conds_der = [cond for cond in conds if isinstance(cond, PolyDerCondition)]
    conds_int = [cond for cond in conds if isinstance(cond, PolyIntCondition)]

    # determine the number of unique ZEROES being forced by derivative conditions:
    n_max = max(
        [0]
        + [cond.derivative for cond in conds_der]
        + [cond.derivative + 1 for cond in conds_crit]
    )
    num_zeroes = [
        len(np.unique([cond.time for cond in conds_der if cond.derivative == n]))
        for n in range(n_max + 1)
    ]

    # ensure the number of forced CRITICAL POINTS on n'th derivatives:
    deg = 0
    for cond in conds_crit:
        # NOTE: n'th derivative has h critical <==> (n+1)'th derivative has h zeroes
        n = cond.derivative
        h = max(cond.num_critical, num_zeroes[n + 1])
        deg = max(deg, n + 1 + h)

    return conds_der + conds_int, deg


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
