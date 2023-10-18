#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.types import *

from .utils import *
from .poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'fourier_of_polynomial',
    'fourier_of_monomials',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def fourier_of_polynomial(
    p: Iterable[float],
    T: float = 1,
) -> Callable[[int], complex]:
    '''
    @returns Function `F`, where

    ```text
    F(n) = 1/T ∫_{t ∈ [0, T]} p(t) exp(-ι2πnt/T) dt.
    ```

    NOTE: Consider

    ```text
    F[tᵏ](n)
        := 1/T · ∫_{t ∈ [0, T]} tᵏ exp(-ι2πnt/T) dt
        = Tᵏ · ∫_{t ∈ [0, 1]} uᵏ exp(-ι2πnu) du
    ```

    Then

    ```text
    tᵏ = ∑_{n ∈ ℤ} F[tᵏ](n) exp(ι2πnt/T).
    ```

    It thus suffices to compute the Fourier-transform
    of (normalised) monomials and then piece these together appropriately.
    '''
    deg = len(p) - 1
    T_pow = np.cumprod([1] + [T] * deg)
    F_monom = list(fourier_of_monomials(k_max=deg))
    # --------
    # NOTE:
    # p(t) = ∑ₖ cₖ · tᵏ
    #
    # F_poly(n) = ∑ₖ cₖ · 1/T · ∫_{t ∈ [0, T]} tᵏ exp(-ι2πnt/T) dt
    #   = ∑ₖ cₖ · Tᵏ · ∫_{t ∈ [0, 1]} uᵏ exp(-ι2πnu) du
    #   = ∑ₖ cₖ · Tᵏ · F_monom[k](n)
    # --------
    F_poly = lambda n: sum(c * TT * FF(n) for c, TT, FF in zip(p, T_pow, F_monom))
    return F_poly


def fourier_of_monomials(k_max: int) -> Generator[Callable[[int], complex], None, None]:
    '''
    Set

    ```text
    F[tᵏ](n) := ∫_{t ∈ [0, 1]} tᵏ exp(st) dt,
    ```

    where `s = -ι2πn`, `n ∈ ℤ`.
    Then

    ```text
    s·F[tᵏ](n) = ∫_{t ∈ [0, 1]} tᵏ s·exp(st) dt
      = ∫_{t ∈ [0, 1]} tᵏ d/dt exp(st) dt
      = [tᵏ exp(st)] – ∫_{t ∈ [0, 1]} (d/dt tᵏ) exp(st) dt
      = [exp(s)–0·exp(0)] – k·∫_{t ∈ [0, 1]} tᵏ¯¹ exp(st) dt
      = 1 – k·F[tᵏ¯¹](n)
      (since s = -ι2πn, n ∈ ℤ)
    ```

    Thus the recursion holds:

    ```text
    F[tᵏ](n) = (1 – k·F[tᵏ¯¹](n))/s
      = ι(1 – k·F[tᵏ¯¹](n))/2πn
    ```

    if `n ≠ 0`, and otherwise

    ```text
    F[tᵏ](0) = ∫_{t ∈ [0, 1]} tᵏ dt = 1/(k+1).
    ```

    NOTE: The recursion in the case of `n ≠ 0` resolves to:

    ```text
    F[k](n) = 1/s · ∑_{j=1}^{k} (-s)^{j}/j! / ((-s)^{k}/k!)
    ```

    for `n ≠ 0`, and all `k ≥ 0`.
    '''
    FF = lambda n: 1 if n == 0 else 0
    yield FF
    for k in range(1, k_max + 1):
        FF = partial(generate_recursion, k=k, F_prev=FF)
        yield FF
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def generate_recursion(
    n: int,
    k: int,
    F_prev: Callable[[int], complex],
) -> complex:
    '''
    Used to recursively generate Fourier coefficients of monomials.
    '''
    if n == 0:
        return 1 / (k + 1)
    return (1 - k * F_prev(n)) / (1j * 2 * pi * n)
