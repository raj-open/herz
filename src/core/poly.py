#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from .utils import *
from .constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'poly',
    'poly_single',
    'print_poly',
    'get_real_polynomial_roots',
    'get_recentred_coefficients',
    'get_derivative_coefficients',
    'get_integral_coefficients',
    'get_critical_points',
    'get_critical_points_bounded',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - basic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def poly_single(t: float, *coeff: float) -> float:
    m = len(coeff)
    x = 0.0
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


def poly(t: Iterable[float], *coeff: float) -> np.ndarray:
    t = np.asarray(t)
    N = len(t)
    m = len(coeff)
    x = np.zeros(shape=(N,), dtype=float)
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - strings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def print_poly(coeff: list[float], var: str = 'X', unitise: bool = True) -> str:
    monoms = [(k, c) for k, c in enumerate(coeff) if c != 0]
    expr = '0'

    def coeff_pow_f(obj: tuple[int, float]) -> str:
        k, c = obj
        c_str = f'{c:.4f}'
        if k == 0:
            return c_str
        if k == 1:
            return f'{c_str} * {var}'
        return f'{c_str} * {var}^{k}'

    def coeff_pow_g(obj: tuple[int, float]) -> str:
        k, c = obj
        c_str = f'{c:.4g}'
        if k == 0:
            return c_str
        if k == 1:
            return f'{c_str} * {var}'
        return f'{c_str} * {var}^{k}'

    match len(monoms):
        case 0:
            expr = '0'
        case 1:
            expr = coeff_pow_g(monoms[-1])
        case _:
            (n, c_leading) = monoms[-1]
            if unitise:
                expr = ' + '.join([coeff_pow_f((k, c / c_leading)) for k, c in monoms])
                match c_leading:
                    case 1:
                        expr = expr
                    case -1:
                        expr = '-' + expr
                    case _:
                        expr = f'{c_leading:.4g} * ({expr})'
            else:
                expr = ' + '.join([coeff_pow_g(obj) for obj in monoms])
    return expr


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - algebra
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_real_polynomial_roots(coeff: list[float]) -> list[float]:
    '''
    Computes reals roots of polynomial with real coefficients,
    sorted in ascending order.

    For constant polynomials the empty set is returned, even for the 0-polynomial.

    NOTE: Roots with algebraic multiplicity = `n` > 1 occur with `n` times in list.
    '''
    if len(coeff) <= 1:
        return []

    roots = np.roots(list(coeff)[::-1]).tolist()
    roots = [t.real for t in roots if abs(t.imag) < MACHINE_EPS]
    # C = sum([ abs(c) for c in coeff ]) or 1.
    # roots = [ t for t in roots if abs(poly_single(t, *coeff)) < C*MACHINE_EPS ]
    roots = sorted(roots)
    return roots


def get_recentred_coefficients(coeff: list[float], t0: float) -> list[float]:
    '''
    Let `p` be a `d`-degree polynomial.
    Computes coeffients of p(t) expressed as
    ```
    p(t) = ∑ₖ cₖ·(t - t₀)ᵏ
    ```
    To do this, observe
    ```
    ∑ₖ cₖ·tᵏ = p(t + t₀)
        = ∑ⱼ aⱼ·(t + t₀)ʲ
        = ∑ⱼ aⱼ·∑ₖ (j choose k) t₀ʲ⁻ᵏtᵏ
        = ∑ₖ (∑ⱼ (j choose k) aⱼ·t₀ʲ⁻ᵏ) tᵏ
        = ∑ₖ (∑ⱼ (k+j choose k) aₖ₊ⱼ·t₀ʲ) tᵏ
    ```
    Let `A` be the `(d+1) x (d+1)` top-left-diagonal matrix with
    ```
    A[k, j] = (k+j choose k) aₖ₊ⱼ for 0 ≤ j ≤ d - k
    A[k, j] = 0 for d-k < j ≤ d
    ```
    and let `u` be the `d+1`-dim vector
    ```
    u[j] = t₀ʲ
    ```
    Then
    ```
    (A·u)[k] = ∑ⱼ A[k, j] u[j] from j = 0 to d-k
        = ∑ⱼ (k+j choose k) aⱼ₊ₖ·t₀ʲ
        = cₖ
    ```
    for each k.
    '''
    deg = len(coeff) - 1
    A = np.asarray(
        [[nCr(k + j, k) * a for j, a in enumerate(coeff[k:])] + [0] * k for k in range(deg + 1)]
    )
    u = np.cumprod([1] + [t0] * deg)
    coeff_recentred = (A @ u).tolist()
    return coeff_recentred


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - calculus
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_derivative_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [k * c for k, c in enumerate(coeff) if k >= 1]
    return [nPr(k, n) * c for k, c in enumerate(coeff) if k >= n]


def get_integral_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [0] + [c / (k + 1) for k, c in enumerate(coeff)]
    return [0] * n + [c / nPr(k + n, n) for k, c in enumerate(coeff)]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - critical points
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_critical_points(
    p: list[float],
    dp: Optional[list[float]] = None,
) -> list[tuple[float, float, int, CriticalPoint]]:
    results = []

    # if not precomputed, compute 1st and 2nd derivatives:
    dp = dp or get_derivative_coefficients(p)

    # necessary condition: t (real-valued) is critical ONLY IF p'(t) = 0:
    t_crit = get_real_polynomial_roots(dp)
    N = len(t_crit)
    if N == 0:
        return []

    # remove duplicates
    info = []
    C = 2 * max([abs(t0) for t0 in t_crit]) + 1
    delta = np.diff([-C] + t_crit + [C])  # difference between each point and previous neighbour
    indices = characteristic_to_where(delta >= MACHINE_EPS)
    for k1, k2 in zip(indices, indices[1:]):
        info.append((t_crit[k1], k2 - k1))

    # compute points between critical points
    t_crit = [t0 for t0, _ in info]
    delta = np.diff([-C] + t_crit + [C])
    t_between = [t0 - dt / 2 for (t0, dt) in zip(t_crit + [C], delta)]
    t_grid = [t_between[0]] + flatten(*list(zip(t_crit, t_between[1:])))

    # classify critical points:
    # FAST METHOD:
    N = len(t_grid)
    values = poly(t_grid, *p)
    values = [tuple(values[k - 1 :][:3]) for k in range(1, N - 1, 2)]
    for (t0, v), (ym_pre, y0, ym_post) in zip(info, values):
        # ----------------------------------------------------------------
        # NOTE:
        # Times between critical points:
        #
        #  ----O------|------O------|--------O----
        #     pre   tm_pre   t0    tm_post  post
        #
        # - y0 := p(t0)
        # - ym_pre := p(tm_pre)
        # - ym_post := p(tm_post)
        #
        # If any of these values are equal,then by mean-value-thm
        # a critical point occurs between them - contradiction!
        # Hence it is mathematically guaranteed,
        # that sgn(ym_pre - y0) = ±1
        # and sgn(ym_post - y0) = ±1
        # ----------------------------------------------------------------

        # classify based on pre/post-changes:
        change_post = signed_relative_change(y0, ym_post, eps=MACHINE_EPS)
        change_pre = signed_relative_change(ym_pre, y0, eps=MACHINE_EPS)
        match change_pre, change_post:
            case (-1, 1):
                results.append((t0, y0, v, CriticalPoint.LOCAL_MINIMUM))
            case (1, -1):
                results.append((t0, y0, v, CriticalPoint.LOCAL_MAXIMUM))
            case (-1, -1) | (1, 1):
                results.append((t0, y0, v, CriticalPoint.INFLECTION))
            case _:
                # NOTE: This case should not occur! If it does - reject!
                pass

    # CLASSICAL METHOD:
    # values = poly(t_crit, *dp)
    # for t0, y in zip(t_crit, values):
    #     if y > MACHINE_EPS:
    #         results.append((t0, CriticalPoint.MINIMUM))
    #     elif y < -MACHINE_EPS:
    #         results.append((t0, CriticalPoint.MAXIMUM))
    #     else:
    #         # ----------------------------------------------------------------
    #         # NOTE: this is computationally intensive
    #         # so only resort to this for unclear cases
    #         # Let q be the polynomial p centred on t₀,
    #         # i.e. q[k] = p⁽ᵏ⁾(t₀)/k! for each k.
    #         # Then q[1] = 0 (by previous computation)
    #         #
    #         # Case 1. For all k > 1 it holds that q[k] = 0.
    #         #     Then q is a constant function!
    #         #     NOTE:
    #         #     This case cannot occur, since 'roots' function
    #         #     returns [] for constant-polynomials.
    #         #
    #         # Case 1. There is some k≥1 for which q[k] ≠ 0.
    #         #     Then let k_min ≥ 1 be minimal occurrence.
    #         #
    #         #     Case 1.1 k_min is even and q[k_min] > 0.
    #         #       ---> LOCAL MIN
    #         #
    #         #     Case 1.2 k_min is even and q[k_min] < 0.
    #         #       ---> LOCAL MAX
    #         #
    #         #     Case 1.3 k_min is odd.
    #         #       ---> LOCAL INFLECTION
    #         # ----------------------------------------------------------------
    #         q = get_recentred_coefficients(p, t0)
    #         indices = [ k for k, c in enumerate(q) if k > 1 and abs(c) > MACHINE_EPS ]
    #         k_min = (indices + [-1])[0]
    #         if k_min == -1:
    #             # Should not occur! If it does, reject critical point.
    #             pass
    #         elif k_min % 2 == 1:
    #             results.append((t0, CriticalPoint.INFLECTION))
    #         elif q[k_min] > MACHINE_EPS:
    #             results.append((t0, CriticalPoint.MINIMUM))
    #         elif q[k_min] < -MACHINE_EPS:
    #             results.append((t0, CriticalPoint.MAXIMUM))

    return results


def get_critical_points_bounded(
    p: list[float],
    t_min: float,
    t_max: float,
    dp: Optional[list[float]] = None,
    only_min_max: bool = False,
) -> list[tuple[float, int, CriticalPoint]]:
    results = get_critical_points(p=p, dp=dp)

    # restrict to interval
    results = [
        (t0, y0, v, kind) for (t0, y0, v, kind) in results if t_min <= t0 and t0 <= t_max
    ]

    if len(results) == 0:
        return []

    t_crit = [results[0][0], results[-1][0]]
    values = poly([t_min, t_max], *p)

    # add in left-boundary or purify points that are too close
    if abs(t_crit[0] - t_min) < MACHINE_EPS:
        results[0] = (t_min, values[0], *results[-1][2:])
    else:
        results.insert(0, (t_min, values[0], 1, CriticalPoint.UNKNOWN))

    # add in right-boundary or purify points that are too close
    if abs(t_max - t_crit[-1]) < MACHINE_EPS:
        results[-1] = (t_max, values[-1], *results[-1][2:])
    else:
        t_crit.append(t_max)
        results.append((t_max, values[-1], 1, CriticalPoint.UNKNOWN))

    # compute absoulte min/max
    values = [y0 for t0, y0, v, kind in results]
    y_min = np.min(values)
    y_max = np.max(values)
    for k, (t0, y0, v, kind) in enumerate(results):
        if abs(relative_change(y_max, y0)) < MACHINE_EPS:
            results[k] = (t0, y_max, v, CriticalPoint.MAXIMUM)
        elif abs(relative_change(y_min, y0)) < MACHINE_EPS:
            results[k] = (t0, y_min, v, CriticalPoint.MINIMUM)

    # remove boundaries of not classified as absolute min/max
    kind = results[0][-1]
    if kind == CriticalPoint.UNKNOWN:
        results = results[1:]

    kind = results[-1][-1]
    if kind == CriticalPoint.UNKNOWN:
        results = results[:-1]

    # remove non-min/max
    if only_min_max:
        results = [
            (t0, y0, v, kind)
            for (t0, y0, v, kind) in results
            if kind
            in [
                CriticalPoint.LOCAL_MINIMUM,
                CriticalPoint.LOCAL_MAXIMUM,
                CriticalPoint.MINIMUM,
                CriticalPoint.MAXIMUM,
            ]
        ]

    return results
