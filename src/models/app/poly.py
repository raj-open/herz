#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ...thirdparty.maths import *

from ...core.poly import *
from ..generated.app import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'onb_conditions',
    'onb_spectrum',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - ONB
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def onb_conditions(
    deg: int,
    conds: list[PolynomialCondition],
    t1: float = 0.0,
    t2: float = 1.0,
) -> np.ndarray:
    '''
    Let A be the condition-matrix.
    We first comput an ONB, B, in ℝ^{d+1} of the nullspace of A.
    The goal is to transform this to an ONB in C[0, T].

    Let p_j be the polynomial corresponding tso coeffs in B[:, j]
    Set

       S[i, j] = ⟨p_i, p_j⟩ = ∫ p_i p_j^* dt / T

    for each i, j.

    CLAIM: S is a positive definite metrix on ℝ^{d+1}.
    PROOF
        For v ∈ ℝ^{d+1}, setting p := ∑_j v[j]p_j ∈ C[0, T], one has

            ⟨Sv, v⟩_{ℝ^{d+1}} = ∑_ij  ⟨p_i, p_j⟩ v[i]v[j]^* = ⟨p, p⟩ ≥ 0,

        with ⟨Sv, v⟩_{ℝ^{d+1}} = 0
        ⟺ ⟨p, p⟩ = 0
        ⟺ p = 0
        ⟺ coeffs in p = 0
        ⟺ coeffs in ∑_j v[j] p_j = 0
        ⟺ ∑_j v[j]B[:, j] = 0
        ⟺ Bv = 0
        ⟺ v = 0, since B is a matrix consisting of linear indep vectors.
    QED.

    It follows that S = UDU^*,
    where U is unitary, D is diagonal and D > 0 (strictly).
    Set Q = B conj(U).
    Let q_j be the polynomial corresponding to coeffs in Q[:, j].
    So

       q_j[i] = Q[i, j] = B[i, :] conj(U)[:, j] = ∑ₖ U^*[j, k] · p_k[i]
       ==> q_j = ∑ₖ U[j, k]^* · p_k

    and

       ⟨q_i, q_j⟩
         = ∑ₖ₁, ₖ₂ U^*[i, k1] · ⟨p_k1, p_k2⟩ · (U^*[j, k2])^*
         = ∑ₖ₁, ₖ₂ U^*[i, k1] · S[k1, k2] · U[k2, j]
         = (U^* S U)[i, j]
         = D[i, j]

    In particular, the vectors {q_i} are orthogonal (in C[0, T]).
    Hence, { 1/√D[i,i] * q_i } is an ONB in C[0, T].
    '''
    # compute ONB for null-space of condition-matrix:
    A = force_poly_conditions(deg=deg, conds=conds)
    B = spla.null_space(A)

    # compute inner-products within C[0, T]:
    S = ip_basis_basis(B, t1=t1, t2=t2)

    # transform B into an ONB in C[0, T]:
    # U, D, V = np.linalg.svd(S)
    D, U = np.linalg.eigh(S)
    Q = B @ U.conj()  # orthogonal family
    Q = Q * 1 / np.sqrt(D)  # normalise each columns
    S = ip_basis_basis(Q, t1=t1, t2=t2)

    return Q


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - SPECTRUM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def onb_spectrum(
    Q: np.ndarray,
    x: list[float],
    t: Optional[list[float]] = None,
    T: float = 1.0,
    periodic: bool = False,
    in_standard_basis: bool = True,
) -> list[float]:
    '''
    computes
    ```
    ∫_[0, T] p(t)x(t) dt
    ```
    where

    - `p(t)` is determined by the coefficients in `coeff`
    - `x(t)` is interpolated from the array `x`,
    '''
    N = len(x)
    d = Q.shape[0] - 1  # degree of polynomials in ONB
    m = Q.shape[1]  # size of ONB
    if t is None:
        t = np.linspace(start=0, stop=T, endpoint=False)
    t = t.tolist()
    coeff = np.zeros(shape=(m,))
    for k, (t1, t2, x1, x2) in enumerate(zip(t, t[1:] + [T], x, x[1:] + [x[0]])):
        if k == N - 1 and not periodic:
            continue
        c1 = (x2 - x1) / (t2 - t1 or 1.0)
        c0 = x1 - c1 * t1
        coeff_seg = np.asarray([c0, c1], dtype=float)
        scale = (t2 - t1) / T

        # recompute generating matrix for inner products
        ip = []
        for j in range(m):
            coeff[j] += scale * ip_poly_poly(coeff_seg, Q[:, j], t1=t1, t2=t2, ip=ip)

    if in_standard_basis:
        coeff = Q @ np.asarray(coeff)

    return coeff.tolist()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS - CONDITIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def force_poly_conditions(
    deg: int,
    conds: list[PolynomialCondition],
) -> np.ndarray:
    A = np.asarray([force_poly_condition(deg=deg, cond=cond) for cond in conds], dtype=float)
    return A


def force_poly_condition(
    deg: int,
    cond: PolynomialCondition,
) -> list[float]:
    '''
    Linear condition on coefficients to determine if
    the `n`th derivate of a polynomial `p` of degree `deg` at point `t`
    satisfies `p⁽ⁿ⁾(t) = 0`.
    '''
    n = cond.derivative
    t = cond.time
    coeff = [0.0] * (deg + 1)
    if n <= deg:
        match t:
            case 0:
                coeff[n] = math.factorial(n)
            case 1.0:
                coeff[n:] = [nPr(k, k - n) for k in range(n, deg + 1)]
            case _:
                tpow = np.cumprod([1] + [t] * (deg - n))
                coeff[n:] = [nPr(k, k - n) * tt for k, tt in zip(range(n, deg + 1), tpow)]
    return coeff


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS - INNER PROD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def ip_poly_poly(
    coeff1: list[float],
    coeff2: list[float],
    t1: float = 0,
    t2: float = 1,
    ip: list[np.ndarray] = [],
) -> float:
    d1 = len(coeff1) - 1
    d2 = len(coeff2) - 1
    if len(ip) == 0:
        ip[:] = [ip_poly_generate_matrix(d1, d2, t1, t2)]
    coeffs = coeff1[:, np.newaxis] * coeff2[np.newaxis, :].conj()
    s = np.sum(ip[0] * coeffs)
    return s


def ip_basis_basis(
    B: np.ndarray,
    t1: float = 0.0,
    t2: float = 1.0,
) -> float:
    d = B.shape[0] - 1
    m = B.shape[1]
    ip = []
    S = np.zeros((m, m))

    for j1 in range(m):
        for j2 in range(j1 + 1):
            S[j1, j2] = ip_poly_poly(B[:, j1], B[:, j2], t1=t1, t2=t2, ip=ip)

    for j2 in range(m):
        for j1 in range(j2):
            S[j1, j2] = S[j2, j1]
    return S


def ip_poly_generate_matrix(
    d1: int,
    d2: int,
    t2: float = 1.0,
    t1: float = 0.0,
):
    powers1 = np.asarray(range(d1 + 1))
    powers2 = np.asarray(range(d2 + 1))
    sumpowers = powers1[:, np.newaxis] + powers2[np.newaxis, :] + 1

    match t1:
        case 0.0:
            tt1 = np.zeros((d1 + 1, d2 + 1))
        case 1.0:
            tt1 = np.ones((d1 + 1, d2 + 1))
        case _:
            tt1 = t1**sumpowers

    match t2:
        case 0.0:
            tt2 = np.zeros((d1 + 1, d2 + 1))
        case 1.0:
            tt2 = np.ones((d1 + 1, d2 + 1))
        case _:
            tt2 = t2**sumpowers

    T = t2 - t1 or 1.0
    ip = (tt2 - tt1) / (T * sumpowers)
    return ip
