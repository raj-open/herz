#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from .constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'poly',
    'poly_single',
    'get_real_polynomial_roots',
    'derivative_coefficients',
    'ip_poly_poly',
    'ip_basis_basis',
    'onb_conditions',
    'onb_spectrum',
    'force_poly_conditions',
    'force_poly_condition',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
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


def poly(t: np.ndarray, *coeff: float) -> np.ndarray:
    N = len(t)
    m = len(coeff)
    x = np.zeros(shape=(N,), dtype=float)
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


def derivative_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    return [nPr(k + n, k) * c for k, c in enumerate(coeff[n:])]


def get_real_polynomial_roots(*coeff: float) -> list[float]:
    roots = np.roots(list(coeff)[::-1]).tolist()
    roots = [t.real for t in roots if abs(t.imag) < FLOAT_ERR]
    # C = sum([ abs(c) for c in coeff ]) or 1.
    # roots = [ t for t in roots if abs(poly_single(t, *coeff)) < C*FLOAT_ERR ]
    return roots


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - INNER PROD
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


def onb_conditions(
    d: int,
    opt: list[tuple[int, float]],
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
    A = force_poly_conditions(d=d, opt=opt)
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
# METHODS - CONDITIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def force_poly_conditions(
    d: int,
    opt: list[tuple[int, float]],
) -> np.ndarray:
    A = np.asarray([force_poly_condition(n=n, d=d, t=t) for n, t in opt], dtype=float)
    return A


def force_poly_condition(
    n: int,
    d: int,
    t: float,
) -> list[float]:
    '''
    Linear condition on coefficients to determine if
    the `n`th derivate of a polynomial `p` of degree `d` at point `t`
    satisfies `p⁽ⁿ⁾(t) = 0`.
    '''
    cond = [0.0] * (d + 1)
    if n <= d:
        match t:
            case 0:
                cond[n] = math.factorial(n)
            case 1.0:
                cond[n:] = [nPr(k, k - n) for k in range(n, d + 1)]
            case _:
                tpow = np.cumprod([1] + [t] * (d - n))
                cond[n:] = [nPr(k, k - n) * tt for k, tt in zip(range(n, d + 1), tpow)]
    return cond
