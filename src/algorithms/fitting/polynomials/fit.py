#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....models.fitting import *
from ....models.polynomials import *
from ....thirdparty.maths import *
from ....thirdparty.types import *
from ...interpolations import *
from .geometry import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_poly_cycle",
    "fit_poly_cycles",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_poly_cycles(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    windows: list[tuple[int, int]],
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    deg: int | None = None,
    intervals: Iterable[tuple[float, float]] = [(0.0, 1.0)],
) -> list[tuple[Poly[float], tuple[int, int]]]:
    """
    Fits polynomial to cycles of a time-series:
    - minimises wrt. the L²-norm
    - forces certain conditions on n'th-derivatives at certain time points
    """
    # due to normalisation (drift-removal), force extra boundary conditions
    conds = conds[:]
    conds.append(PolyDerCondition(derivative=0, time=0.0))
    conds.append(PolyDerCondition(derivative=0, time=1.0))
    # conds.append(PolyIntCondition(times=[TimeInterval(a=0., b=1.)]))

    # refine conditions + determine degree of polynomial needed
    conds, deg_ = refine_conditions_determine_degree(conds)
    if deg is None:
        deg = deg_

    # fit each cycle
    fits = []
    for i1, i2 in windows:
        tt, _, _, _ = normalise_to_unit_interval(t[i1:i2])
        xx = x[i1:i2]
        p = fit_poly_cycle(t=tt, x=xx, period=1, deg=deg, conds=conds, intervals=intervals)
        fits.append((p, (i1, i2)))

    p_sim = compute_simultaneous_fit([p for p, _ in fits], offset=0, period=1)
    fits.append((p_sim, (-1, -1)))

    return fits


# ----------------------------------------------------------------
# SECIONDARY METHODS
# ----------------------------------------------------------------


def fit_poly_cycle(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    period: float,
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
    intervals: Iterable[tuple[float, float]] = [(0.0, 1.0)],
) -> Poly[float]:
    """
    Fits 'certain' polynomials to a cycle in such a way,
    that special attributes can be extracted.

    @inputs
    - `t` - a `1`-dimensional array of time-values normalised to [0, 1].
    - `x` - a `1`-dimensional array of values in a cycle.
    - `dt` - the time increment.
    - `intervals` - list of subintervals `[a, b] ⊆ [0, 1]` for which the data is to be considered.

    @returns
    - `[ (k, c_k) … ]` whereby `c_k` is the coefficient of the monom `t^k`,
      Here the polynomial is to be understood as being paramterised
      over time uniformly on `[0, T]`.
    - the fit polynomial
    """
    Q = onb_conditions(deg=deg, conds=conds, intervals=intervals)
    p = onb_spectrum(t=t, x=x, T=period, Q=Q, intervals=intervals, cyclic=True)
    return p


def compute_simultaneous_fit(
    polys: list[Poly[float]],
    offset: float,
    period: float,
) -> Poly[float]:
    """
    Fits a single polynomial to all cycles simultaenously.

    Note:
    Since a method via ONB is used, the optimal solution
    (least L²-distance) is the average.
    Proof.
        Let (x⁽ᵏ⁾(t))ₖ be the respective (interpolated+normalised) curves in C[0, T].
        Let x(t) := 1/n ∑ₖ x⁽ᵏ⁾(t) the avarage in C[0, T].
        Then

        res := 1/n · ∑ₖ ‖p - x⁽ᵏ⁾‖²
            = 1/n · ∑ₖ ‖p‖² + ‖x⁽ᵏ⁾‖² + 2Re ⟨x⁽ᵏ⁾, p⟩
            = const + ‖p‖² + 2Re ⟨x, p⟩
            = const + ‖x‖² + ‖p‖² + 2Re ⟨x, p⟩
            = const + ‖p - x‖²

        Hence to res minimsed ⟺ p minimised for the average, x(t).
        We do not have access to x, since the x⁽ᵏ⁾ are not comensurable.
        However, letting p⁽ᵏ⁾ be minimised for each x⁽ᵏ⁾,
        one has via the ONB (qⱼ)ⱼ

        p optimal for x
        ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨x, qⱼ⟩
        ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨1/n ∑ₖ x⁽ᵏ⁾, qⱼ⟩
        ⟺ ∀j: ⟨p, qⱼ⟩ = 1/n ∑ₖ ⟨x⁽ᵏ⁾, qⱼ⟩
        ⟺ ∀j: ⟨p, qⱼ⟩ = 1/n ∑ₖ ⟨p⁽ᵏ⁾, qⱼ⟩
        ⟺ ∀j: ⟨p, qⱼ⟩ = ⟨1/n ∑ₖ p⁽ᵏ⁾, qⱼ⟩
        ⟺ p = 1/n ∑ₖ p⁽ᵏ⁾

        Hence the coefficients for p are just the average
        of the coefficients of the p⁽ᵏ⁾.
    QED

    """
    coeff = np.mean(np.asarray([p.coefficients for p in polys]), axis=0).tolist()
    return Poly[float](
        coeff=coeff,
        cyclic=True,
        offset=offset,
        period=period,
    )


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def refine_conditions_determine_degree(
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
) -> tuple[list[PolyDerCondition | PolyIntCondition], int]:
    """
    Extracts the minimum model size needed to satisfy all criteria.
    """
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
