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
    conds: list[PolyDerCondition | PolyIntCondition],
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
    @inputs
    - `Q` - a `d x m` array, where `Q[:,j]` denote the coefficients of a polynomial qⱼ
      and {qⱼ}ⱼ is an ONB
    - (`t`, `x`) - a discrete time-series
    - `T` - the total time-duration
    - `periodic` - whether the series is periodic
    - `in_standard_basis` - whether to convert the computed innerproducts
       to coefficients wrt the standard basis {tʲ}ⱼ.

    @returns
    coefficients of best fit polynomial either wrt. the ONB {qⱼ}ⱼ
    or the standard basis {tʲ}ⱼ

    Computes
    ```
    cⱼ := ⟨x, qⱼ⟩
       := 1/T · ∫_[0, T] x(t)·qⱼ(t)^* dt
    ```
    where `x(t)` is a piecewise linear interpolation of a discrete time-series `x`.
    This yields a polynomial:
    ```
    p = ∑ⱼ cⱼ·qⱼ
    ```
    satisfying
    ```
    L²-norm ‖x – p‖ minimal
    ```
    amongst all possibly polynomials in the subspace `V ⊆ C[0, T]`
    spanned by {qⱼ}ⱼ.
    '''
    deg = Q.shape[0] - 1  # degree of polynomials in ONB
    m = Q.shape[1]  # size of ONB

    if t is None:
        t = np.linspace(start=0, stop=T, endpoint=False)

    # --------------------------------
    # NOTE:
    # The interval [0, T] is subdivided into
    # intervals [t1ᵢ, t2ᵢ] with endpoints
    # from the discrete time-series.
    # The monom
    #
    #    C0[i] + C1[i]·t
    #
    # is a piecewise-linear interpolation
    # for x(t) on [t1ᵢ, t2ᵢ].
    # --------------------------------
    t = (np.asarray(t) - t[0]).tolist() + [T]  # normalise to [0, T]
    if periodic:
        x = x.tolist() + [x[0]]
    else:
        x1 = np.asarray(x[1:])
        x2 = np.asarray(x[:-1])
        x = np.concatenate([[x[0]], (x1 + x2) / 2, [x[-1]]]).tolist()
    dt = np.diff(t)
    dx = np.diff(x)
    dt[dt == 0.0] = 1.0
    C1 = dx / dt
    C0 = np.asarray(x[:-1]) - C1 * np.asarray(t[:-1])

    # --------------------------------
    # Determine coefficients of integrals of polynomials:
    # NOTE:
    # Q[:, j] = coeff of polynomial qⱼ
    # Q1[:, j] = coeff of polynomial q1ⱼ, a stemfunction of qⱼ
    # Q2[:, j] = coeff of polynomial q2ⱼ, a stemfunction of q1ⱼ
    # R[:, j] = coeff of polynomial rⱼ = t·q1ⱼ - q2ⱼ
    # --------------------------------
    Q1 = np.asarray([integral_coefficients(Q[:, j].tolist()) for j in range(m)]).T
    Q2 = np.asarray([integral_coefficients(Q1[:, j].tolist()) for j in range(m)]).T
    zeros = np.zeros((1, m))
    R = np.concatenate([zeros, Q1]) - Q2
    Q1 = np.concatenate([Q1, zeros])  # pad

    # --------------------------------
    # NOTE:
    # Set
    #
    #    dmonomes[i, k] = t2ᵢᵏ - t2ᵢᵏ
    #
    # for each i and for k ∈ {0, 1, ..., deg + 2}
    # The polynomial evaluations of an array of `deg+2`-degree
    # computed by
    #
    #    dmonomes @ P
    #
    # satisfies
    #
    #    (dmonomes @ P)[i, j]
    #      = ∑ₖ dmonomes[i, k]·P[k, j]
    #      = ∑ₖ P[k, j]·t2ᵢᵏ - P[k, j]·t2ᵢᵏ
    #      = pⱼ(t2ᵢ) - pⱼ(t1ᵢ)
    # --------------------------------
    monomes = np.asarray([[1] + [tt**k for k in range(1, deg + 2 + 1)] for tt in t])
    dmonomes = monomes[1:, :] - monomes[:-1, :]
    I0 = dmonomes @ Q1
    I1 = dmonomes @ R

    # --------------------------------
    # NOTE:
    # Part of innerproduct ⟨x, qⱼ⟩ restricted to [t1ᵢ, t2ᵢ],
    # assuming interpolation
    #
    #    ∫ₜ₁ᵢ, ₜ₂ᵢ x(t)qⱼ(t)^* dt
    #
    #      = c₀ᵢ∫ₜ₁ᵢ, ₜ₂ᵢ 1 · qⱼ^* dt + c₁ᵢ∫ₜ₁, ₜ₂ t · qⱼ^* dt
    #
    #      = c₀ᵢ[q1ⱼ^*]ₜ₁ᵢ, ₜ₂ᵢ + c₁ᵢ·[t·q1ⱼ^* - q2ⱼ^*]ₜ₁ᵢ, ₜ₂ᵢ
    #
    #      = c₀ᵢ(q1ⱼ(t2ᵢ) - q1ⱼ(t1ᵢ))^*
    #        + c₁ᵢ·(rⱼ(t1ᵢ) - rⱼ(t1ᵢ))^*
    #
    #      = C0[i]·I0[i, j]^* + C1[i]·I1[i, j]^*
    #
    # Hence
    #
    #    coeffⱼ := ∫ x(t)qⱼ(t)^* dt
    #
    #      = ∑ᵢ ∫ₜ₁ᵢ, ₜ₂ᵢ x(t)qⱼ(t)^* dt
    #
    #      = ∑ᵢ C0[i]·I0[i, j]^* + C1[i]·I1[i, j]^*
    #
    #      = (I0^* · C0 + I1^* · C1)[j]
    #
    #
    # --------------------------------
    coeff = I0.conj().T @ C0 + I1.conj().T @ C1

    if in_standard_basis:
        coeff = Q @ coeff

    return coeff.tolist()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS - CONDITIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def force_poly_conditions(
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
) -> np.ndarray:
    m = len(conds)
    A = np.asarray(
        [force_poly_condition(deg=deg, cond=cond) for cond in conds], dtype=float
    ).reshape((m, deg + 1))
    return A


def force_poly_condition(
    deg: int,
    cond: PolyDerCondition | PolyIntCondition,
) -> list[float]:
    '''
    Linear condition on coefficients to determine if
    the `n`th derivate of a polynomial `p` of degree `deg` at point `t`
    satisfies `p⁽ⁿ⁾(t) = 0`.
    '''
    row = np.zeros(shape=(deg + 1,), dtype=float)
    if isinstance(cond, PolyDerCondition):
        n = cond.derivative
        t = cond.time
        if n <= deg:
            match t:
                case 0:
                    row[n] = math.factorial(n)
                case 1.0:
                    row[n:] = [nPr(k, n) for k in range(n, deg + 1)]
                case _:
                    tpow = np.cumprod([1] + [t] * (deg - n))
                    row[n:] = [nPr(k, n) * tt for k, tt in zip(range(n, deg + 1), tpow)]
    # elif isinstance(cond, PolyIntCondition):
    else:
        [t1, t2] = cond.times
        t1pow = np.cumprod([t1] * (deg + 1))
        t2pow = np.cumprod([t2] * (deg + 1))
        p = np.asarray(range(0, deg + 1))
        row = (t2pow - t1pow) / (p + 1)
    return row.tolist()


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
