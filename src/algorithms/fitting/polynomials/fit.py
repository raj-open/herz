#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....models.polynomials import *
from ....models.fitting import *
from ...interpolations import *
from .geometry import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fit_poly_cycle',
    'fit_poly_cycles',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_poly_cycles(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    windows: list[tuple[int, int]],
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
) -> list[tuple[tuple[int, int], FittedInfoPoly]]:
    '''
    Fits polynomial to cycles of a time-series:
    - minimises wrt. the L²-norm
    - forces certain conditions on n'th-derivatives at certain time points
    '''
    # due to normalisation (drift-removal), force extra boundary conditions
    conds = conds[:]
    conds.append(PolyDerCondition(derivative=0, time=0.0))
    conds.append(PolyDerCondition(derivative=0, time=1.0))
    # conds.append(PolyIntCondition(times=[TimeInterval(a=0., b=1.)]))

    # refine conditions + determine degree of polynomial needed
    conds, deg = refine_conditions_determine_degree(conds)

    # fit each cycle
    fits = []
    for i1, i2 in windows:
        p = fit_poly_cycle(t=t[i1:i2], x=x[i1:i2], deg=deg, conds=conds)
        fit = FittedInfoPoly(coefficients=p.coefficients)
        fits.append(((i1, i2), fit))

    fit = compute_simultaneous_fit([fit for _, fit in fits])
    fits.append(((-1, -1), fit))

    return fits


def fit_poly_cycle(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
) -> Poly[float]:
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
    p = onb_spectrum(t=t, x=x, Q=Q, T=1, in_standard_basis=True)
    return p


# ----------------------------------------------------------------
# SECIONDARY METHODS
# ----------------------------------------------------------------


def compute_simultaneous_fit(fits: list[FittedInfoPoly]) -> FittedInfoPoly:
    '''
    Fits a single polynomial to all cycles simultaenously.

    NOTE:
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
    '''
    coeff = np.mean(np.asarray([fit.coefficients for fit in fits]), axis=0).tolist()
    info = FittedInfoPoly(coefficients=coeff)
    return info


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def refine_conditions_determine_degree(
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
) -> tuple[list[PolyDerCondition | PolyIntCondition], int]:
    '''
    Extracts the minimum model size needed to satisfy all criteria.
    '''
    conds_crit = [cond for cond in conds if isinstance(cond, PolyCritCondition)]
    conds_der = [cond for cond in conds if isinstance(cond, PolyDerCondition)]
    conds_int = [cond for cond in conds if isinstance(cond, PolyIntCondition)]

    # determine the number of unique ZEROES being forced by derivative conditions:
    n_max = max([0] + [cond.derivative for cond in conds_der] + [cond.derivative + 1 for cond in conds_crit])
    num_zeroes = [len(np.unique([cond.time for cond in conds_der if cond.derivative == n])) for n in range(n_max + 1)]

    # ensure the number of forced CRITICAL POINTS on n'th derivatives:
    deg = 0
    for cond in conds_crit:
        # NOTE: n'th derivative has h critical <==> (n+1)'th derivative has h zeroes
        n = cond.derivative
        h = max(cond.num_critical, num_zeroes[n + 1])
        deg = max(deg, n + 1 + h)

    return conds_der + conds_int, deg
