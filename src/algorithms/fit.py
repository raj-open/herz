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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'fit_poly_right_ventricular_pressure_cycle',
    'fit_poly_right_ventricular_pressure_cycles',
    'fit_poly_nth_derivative',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def fit_poly_right_ventricular_pressure_cycles(
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
        x_fit[i1:i2], coeffs[k] = fit_poly_right_ventricular_pressure_cycle(
            t=tt, x=xx, n=n, h=h
        )

    return x_fit, coeffs


def fit_poly_nth_derivative(
    t: np.ndarray,
    coeffs: list[list[float]],
    cycles: list[int],
):
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    # get curve and compute nth derivative
    N = len(t)
    x_der = np.zeros(shape=(N,), dtype=float)
    coeffs_der = [[]] * len(windows)
    for k, (i1, i2) in enumerate(windows):
        coeffs_der[k] = derivative_coefficients(coeffs[k])
        tt, T = normalise_to_unit_interval(t[i1:i2])
        # compute derivate wrt. rescaled t, then rescale value
        x_der[i1:i2] = 1 / T * poly(tt, *coeffs_der[k])

    return x_der, coeffs_der


def fit_poly_right_ventricular_pressure_cycle(
    t: np.ndarray,
    x: np.ndarray,
    n: int = 3,
    h: int = 7,
) -> tuple[np.ndarray, list[tuple[int, float]]]:
    '''
    Fits 'certain' polynomials to a pressure cycle in such a way,
    that special attributes can be extracted.

    @inputs
    - `x` - a `1`-dimensional array of pressure-values in a cycle.
    - `dt` - the time increment.

    @returns
    - `[ (k, c_k) … ]` whereby `c_k` is the coefficient of the monom `t^k`,
      Here the polynomial is to be understood as being paramterised
      over time uniformly on `[0, T]`.
    - the fit polynomial

    ## Assumptions ##

    - Since it does not matter what the starting point is,
      one can assume that the time interval is `[0, T]`.
    - The `n-1`-th derivative `x⁽ⁿ⁻¹⁾` is a polynomial,
      with `h` alternating peaks/troughs,
      whereby the two end points `0` and `T` are peaks.

    This implies that the `n`-th derivative `x⁽ⁿ⁾` is a polynomial
    with `h` zeros, two of which are the end points.
    Hence for some polynomial `q(t)` of degree `h-2`

    ```
    x⁽ⁿ⁾(t) = t(t - T)q(t)
        = (t² - tT)∑ₖ₌₀..ₕ₋₂ cₖtᵏ
        = ∑ₖ₌₂..ₕ cₖ₋₂tᵏ - ∑ₖ₌₁..ₕ₋₁ Tcₖ₋₁tᵏ
        = - Tc₀t + ∑ₖ₌₂..ₕ₋₁ (cₖ₋₂ - Tcₖ₋₁)tᵏ + cₕ₋₂tʰ
    ```

    Thus

    ```
    x(t) = o(tⁿ) - Tc₀/n tⁿ
          + ∑ₖ₌₂..ₕ₋₁ (cₖ₋₂ - Tcₖ₋₁)/(k + n) tᵏ⁺ⁿ
          + cₕ₋₂/(h+n) tʰ⁺ⁿ
    ```
    '''

    N = len(x)
    fct = fit_function(n)

    coeff, cov = spo.curve_fit(
        fct,
        xdata=t,  # rescale to [0, 1]
        ydata=x,
        # initialise coefficients of o(tⁿ) and q(t)
        # i.e. n + (h-2 + 1) coefficients
        p0=[0.0] * (n + h - 1),
        absolute_sigma=False,
        check_finite=None,
        # bounds=(-np.inf, np.inf),
        # Method to use for optimisation.
        # Default: ‘lm’ for unconstrained problems, ‘trf’ if bounds are provided.
        # NOTE: ‘lm’ won’t work if number of observations < number of variables,
        # Use ‘trf’ or ‘dogbox’ in this case.
        method='lm',
        full_output=False,
        nan_policy='omit',
    )

    x_fit = fct(t, *coeff)
    coeff_x = effective_coefficients(n, 1.0, *coeff)

    return x_fit, coeff


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def effective_coefficients_pq(n: int, T: float, *coeff_q: float) -> list[float]:
    '''
    Determines coefficients of `p(t)·q(t)`,
    based on coefficients of `q(t)`,
    where `p(t) = t·(t - T)`.
    '''
    m = len(coeff_q)
    coeff_q = np.asarray(coeff_q, dtype=float)
    coeff_pq = np.zeros(shape=(m + 2,), dtype=float)
    coeff_pq[2:] += coeff_q
    coeff_pq[1:-1] -= T * coeff_q
    return coeff_pq


def effective_coefficients(n: int, T: float, *coeff: float) -> list[float]:
    '''
    Determines coefficients of `x(t)` based on algebraic constraints
    on coefficients that occur in polynomial for `x´´´(t)`.
    '''
    coeff_x_nth = effective_coefficients_pq(n, T, *coeff[n:])
    coeff_x = list(coeff[:n]) + [c / (k + n) for k, c in enumerate(coeff_x_nth)]
    return coeff_x


def fit_function(n: int):
    def fct(t: float, *coeff: float):
        '''
        Polynomial function for `x(t)` based on
        coefficients that occur in polynomial for `x´´´(t)`
        plus coefficients that arised during integration.

        NOTE: assumes time is normalised to `[0, 1]`
        '''
        coeff_x = effective_coefficients(n, 1.0, *coeff)
        x = poly(t, *coeff_x)
        return x

    return fct
