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

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'onb_conditions',
    'onb_spectrum',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def onb_conditions(
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
    intervals: Iterable[tuple[float, float]] = [(0.0, 1.0)],
) -> NDArray[np.float64]:
    '''
    Let `Ω` denote the union of the intervals.
    Let `A` be the condition-matrix.
    We first compute an ONB, `B`, in `ℝᵈ⁺¹` of the nullspace of `A`.
    The goal is to transform this to an ONB in `(C(Ω), ‖·‖₂)`.

    Let `p_j` be the polynomial corresponding to coeffs in `B[:, j]`.
    Set

    ```
    S[i, j] = ⟨p_i, p_j⟩
        = ∫_{t ∈ Ω} p_i p_j^* dt
    ```

    for each `i, j`.

    **CLAIM:** `S` is a positive definite matrix on `ℝᵈ⁺¹`.

    *Proof:*
        For `v ∈ ℝᵈ⁺¹`, setting `ξ := ∑_j v[j]p_j ∈ C(Ω)`, one has
        ```
        ⟨Sv, v⟩_{ℝᵈ⁺¹} = ∑_ij  ⟨p_i, p_j⟩ v[i]v[j]^* = ⟨ξ, ξ⟩ ≥ 0,
        ```
        with
        ```
        ⟨Sv, v⟩_{ℝᵈ⁺¹} = 0
        ⟺ ⟨ξ, ξ⟩ = 0
        ⟺ ξ = 0
        ⟺ coeffs in ξ = 0
        ⟺ coeffs in ∑_j v[j] p_j = 0
        ⟺ ∑_j v[j]B[:, j] = 0
        ⟺ Bv = 0
        ⟺ v = 0,
        ```
        since `B` is a matrix consisting of linear indep vectors.
    QED

    It follows that `S = UDU^*`,
    where `U` is unitary, `D` is diagonal and `D > 0` (strictly).

    Set `Q = B conj(U)`.
    Let `q_j` be the polynomial corresponding to coeffs in `Q[:, j]`.
    So
    ```
    q_j[i] = Q[i, j]
        = B[i, :] conj(U)[:, j]
        = ∑ₖ U^*[j, k] · p_k[i]

    ⟹ q_j = ∑ₖ U[j, k]^* · p_k
    ```
    and
    ```
    ⟨q_i, q_j⟩
    = ∑ₖ₁, ₖ₂ U^*[i, k1] · ⟨p_k1, p_k2⟩ · (U^*[j, k2])^*
    = ∑ₖ₁, ₖ₂ U^*[i, k1] · S[k1, k2] · U[k2, j]
    = (U^* S U)[i, j]
    = D[i, j]
    ```
    In particular, the vectors `{q_i}` are orthogonal in `C(Ω)`.
    Hence, `{ 1/√D[i,i] * q_i }` is an ONB in `C(Ω)`.
    '''
    # compute ONB for null-space of condition-matrix:
    A = force_poly_conditions(deg=deg, conds=conds)
    B = spla.null_space(A)

    # compute inner-products within C(Ω):
    S = inner_product_polybasis(B, intervals)

    # transform B into an ONB in C(Ω):
    # U, D, V = np.linalg.svd(S)
    D, U = np.linalg.eigh(S)
    Q = B @ U.conj()  # orthogonal family
    Q = Q * 1 / np.sqrt(D)  # normalise each columns

    return Q


# ----------------------------------------------------------------
# METHODS - SPECTRUM
# ----------------------------------------------------------------


def onb_spectrum(
    Q: NDArray[np.float64],
    t: list[float],
    x: list[float],
    intervals: Iterable[tuple[float, float]],
    T: float | None = None,
    cyclic: bool = False,
) -> Poly[float]:
    '''
    @inputs
    - `Q` - a `d x m` array, where `Q[:,j]` denote the coefficients of a polynomial qⱼ
      and {qⱼ}ⱼ is an ONB
    - (`t`, `x`) - a discrete time-series
    - `intervals` - list of disjoint sub intervals of some interval
       on which the polynomial lives.
    - `cyclic` - whether the series is periodic

    @returns
    the unique polynomial, a linear combination of polynomials in `Q`
    ```
    p(t) = ∑ⱼ cⱼ·tⱼ
    ```
    which is the best fit polynomial wrt. the standard basis {tʲ}ⱼ.

    ## Computation ##

    Let `Ω` denote the union of the disjoint invervals.

    Determines
    ```
    cⱼ := ⟨x, qⱼ⟩
       := ∫_Ω x(t)·qⱼ(t)^* dt
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
    amongst all possibly polynomials in the subspace `V ⊆ C(Ω)`
    spanned by {qⱼ}ⱼ.

    ### Step 1 ###

    Determine coefficients of integrals of polynomials:
    - Q[:, j] = coeff of polynomial qⱼ
    - Q1[:, j] = coeff of polynomial q1ⱼ, a stemfunction of qⱼ
    - Q2[:, j] = coeff of polynomial q2ⱼ, a stemfunction of q1ⱼ
    - R[:, j] = coeff of polynomial rⱼ = t·q1ⱼ - q2ⱼ

    ### Step 2 - piecewise linear interpolations ###

    The intervals in Ω are subdivided into
    intervals [t1ᵢ, t2ᵢ] with endpoints
    from the discrete time-series.
    The monom
    ```
    C0[i] + C1[i]·t
    ```
    is a piecewise-linear interpolation
    for x(t) on [t1ᵢ, t2ᵢ].

    ### Step 3 ###

    Set
    ```
    dmonomes[i, k] = t2ᵢᵏ - t1ᵢᵏ
    ```
    for each i and for k ∈ {0, 1, ..., deg + 2}
    The polynomial evaluations of an array of `deg+2`-degree
    computed by
    ```
    dmonomes @ P
    ```
    satisfies
    ```
    (dmonomes @ P)[i, j]
        = ∑ₖ dmonomes[i, k]·P[k, j]
        = ∑ₖ P[k, j]·t2ᵢᵏ - P[k, j]·t2ᵢᵏ
        = pⱼ(t2ᵢ) - pⱼ(t1ᵢ)
    ```

    NOTE:

    Part of innerproduct ⟨x, qⱼ⟩ restricted to [t1ᵢ, t2ᵢ],
    assuming interpolation
    ```
    ∫ₜ₁ᵢ, ₜ₂ᵢ x(t)qⱼ(t)^* dt

        = c₀ᵢ∫ₜ₁ᵢ, ₜ₂ᵢ 1 · qⱼ^* dt + c₁ᵢ∫ₜ₁, ₜ₂ t · qⱼ^* dt

        = c₀ᵢ[q1ⱼ^*]ₜ₁ᵢ, ₜ₂ᵢ + c₁ᵢ·[t·q1ⱼ^* - q2ⱼ^*]ₜ₁ᵢ, ₜ₂ᵢ

        = c₀ᵢ(q1ⱼ(t2ᵢ) - q1ⱼ(t1ᵢ))^*
        + c₁ᵢ·(rⱼ(t1ᵢ) - rⱼ(t1ᵢ))^*

        = C0[i]·I0[i, j]^* + C1[i]·I1[i, j]^*
    ```
    Hence
    ```
    coeffⱼ := ∫ x(t)qⱼ(t)^* dt

        = ∑ᵢ ∫ₜ₁ᵢ, ₜ₂ᵢ x(t)qⱼ(t)^* dt

        = ∑ᵢ C0[i]·I0[i, j]^* + C1[i]·I1[i, j]^*

        = (I0^* · C0 + I1^* · C1)[j]
    ```
    '''
    # Step 1 - auxiliary computeations for polynomials in basis
    deg = Q.shape[0] - 1  # degree of polynomials in ONB
    m = Q.shape[1]  # number of elements in the ONB
    # stem functions (for 1st and 2nd order derivatives) for the q_i
    Q1 = np.column_stack([Poly(coeff=Q[:, j].tolist()).integral().coefficients for j in range(m)])
    Q2 = np.column_stack([Poly(coeff=Q1[:, j].tolist()).integral().coefficients for j in range(m)])
    # coefficients of t·q1ⱼ - q2ⱼ for each qⱼ:
    zeros = np.zeros((1, m))
    R = np.concatenate([zeros, Q1]) - Q2
    # pad coefficients of Q1 to match Q2
    Q1 = np.concatenate([Q1, zeros])

    # Loop over all intervals
    t, x = complete_time_series(t=t, x=x, T=T, cyclic=cyclic)
    alpha = np.zeros((m,))
    for t1, t2 in intervals:
        filt = (t1 <= t) & (t <= t2)
        t_ = t[filt]
        x_ = x[filt]
        # Step 2 - compute linear interpolations
        dt = np.diff(t_)
        dx = np.diff(x_)
        dt[dt == 0.0] = 1.0
        C1 = dx / dt
        C0 = np.asarray(x_[:-1]) - C1 * np.asarray(t_[:-1])

        # Step 3 - compute (contribution to) inner products
        monomes = np.asarray([np.concatenate([[1], np.cumprod([tt] * (deg + 2))]) for tt in t_])
        dmonomes = monomes[1:, :] - monomes[:-1, :]
        I0 = dmonomes @ Q1
        I1 = dmonomes @ R
        alpha += I0.conj().T @ C0 + I1.conj().T @ C1

    # convert to standard basis
    coeff = Q @ alpha

    offset = t[0]
    if T is None:
        _, T, _ = get_time_aspects(t)

    return Poly[float](
        coeff=coeff.tolist(),
        cyclic=cyclic,
        offset=offset,
        period=T,
    )


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def force_poly_conditions(
    deg: int,
    conds: list[PolyDerCondition | PolyIntCondition],
) -> NDArray[np.float64]:
    '''
    Linear condition on coefficients to determine if
    the `n`th derivate of a polynomial `p` of degree `deg` at point `t`
    satisfies `p⁽ⁿ⁾(t) = 0`.
    '''
    rows = []
    for cond in conds:
        match cond:
            # DEV-NOTE: yes, this actually works! This is how to match types!
            case PolyDerCondition():
                row = np.zeros(shape=(deg + 1,), dtype=float)
                match cond.derivative, cond.time:
                    case n, _ if n > deg:
                        pass
                    case _ as n, 0:
                        row[n] = math.factorial(n)
                    case _ as n, 1:
                        row[n:] = [nPr(k, n) for k in range(n, deg + 1)]
                    case _ as n, _ as t:
                        tpow = np.cumprod([1] + [t] * (deg - n))
                        row[n:] = [nPr(k, n) * tt for k, tt in zip(range(n, deg + 1), tpow)]
            # case PolyIntCondition():
            case _:
                for interval in cond.times:
                    t1 = interval.a
                    t2 = interval.b
                    t1_pow = np.cumprod([t1] * (deg + 1))
                    t2_pow = np.cumprod([t2] * (deg + 1))
                    p = np.asarray(range(deg + 1))
                    row = (t2_pow - t1_pow) / (p + 1)
        rows.append(row)

    return np.row_stack(rows)
