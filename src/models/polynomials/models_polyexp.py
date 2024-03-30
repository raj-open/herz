#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.utils import *
from ..intervals import *
from .models_base import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'PolyExp',
    'pre_compare',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', float, complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class PolyExp(PolyExpBase[T]):
    '''
    A class to model functions of the form
    ```
    t ⟼ p(t)·exp(αt)
    ```
    where `p` is a (possibly periodic) polynomial
    and `α` some growth constant.

    NOTE: Only the polynomial part may be periodic.
    '''

    @staticmethod
    def load_from_zeroes(
        zeroes: dict[complex, int] | list[complex],
        lead: complex = 1.0,
        alpha: complex = 0,
        **__,
    ) -> PolyExp[complex]:
        p = PolyExp(coeff=[lead], alpha=alpha, **__)
        if isinstance(zeroes, list):
            for z in zeroes:
                p *= PolyExp(coeff=[-z, 1], **__)
            p.roots = zeroes
        else:
            for z, n in zeroes.items():
                assert n >= 0, 'Cannot multiply by negative powers!'
                if n == 0:
                    continue
                z_pow = np.cumprod([1] + [-z] * n)
                p *= PolyExp(
                    coeff=[math.comb(n, k) * zz for k, zz in zip(range(n + 1), z_pow[::-1])],
                    **__,
                )
            p.roots = flatten(*[[z] * n for z, n in zeroes.items()])
        return p

    def __copy__(self) -> PolyExp[T]:
        return PolyExp[T](**self.serialise())

    def __deepcopy__(self) -> PolyExp[T]:
        return self.__copy__()

    def __eq__(self, o: Any) -> bool:
        coeff_p = self.coeff
        if isinstance(o, (int, float, complex)):
            return self.__eq__(PolyExp(coeff=[o]))
        if isinstance(o, PolyExp):
            coeff_p, coeff_q = pre_compare(self, o)
            return all(c == cc for c, cc in zip(coeff_p, coeff_q))
        return False

    def __mul__(self, q: Any) -> PolyExp:
        if isinstance(q, (int, float, complex)):
            if self.lead == 0 or q == 0:
                return PolyExp(coeff=[1], lead=0, **self.params)
            else:
                result = self * PolyExp(coeff=[1], lead=q, **self.params)
                result.roots = self.roots[:]
                return result

        if isinstance(q, PolyExp):
            params = self.params
            match self.cyclic, q.cyclic:
                case True, True:
                    assert self.offset == q.offset, 'Models must have compatible offset-value!'
                    assert self.period == q.period, 'Models must have compatible period-value!'
                case False, True:
                    params = q.params

            if self.lead == 0 or q.lead == 0:
                return PolyExp(coeff=[1], lead=0, alpha=0, **params)

            coeff_p = np.asarray(self.coeff)
            coeff_q = np.asarray(q.coeff)
            coeff = np.sum(
                [[0] * k + (c * coeff_p).tolist() + [0] * (q.degree - k) for k, c in enumerate(coeff_q)],
                axis=0,
            ).tolist()
            params = params | {'accuracy': max(self.accuracy, q.accuracy)}
            result = PolyExp(
                alpha=self.alpha + q.alpha,
                lead=self.lead * q.lead,
                coeff=coeff,
                **params,
            )
            result.roots = self.roots[:] + q.roots[:]
            return result

        raise TypeError(f'No multiplication method for Poly x {type(q)}!')

    def __rmul__(self, q: Any) -> PolyExp:
        return self * q

    def __call__(self, t: float) -> complex:
        # NOTE: only polynomial part is periodic
        exp_value = np.exp(self.alpha * t)
        # compute polynomial part
        coeff = self.lead * np.asarray(self.coeff)
        if self.cyclic and t != self.offset + self.period:
            t = self.offset + (t - self.offset) % self.period
        # t_pow[j] = t ^ j
        t_pow = np.cumprod([1] + [t] * self.degree)
        poly_value = sum(coeff * t_pow)
        return poly_value * exp_value

    def values(self, t: Iterable[float]) -> NDArray[np.complex]:
        if not isinstance(t, np.ndarray):
            t = np.asarray(t)
        t = t.copy()
        # NOTE: only polynomial part is periodic
        exp_values = np.exp(self.alpha * t)
        # compute polynomial part
        if self.cyclic:
            filt = t != self.offset + self.period
            t[filt] = self.offset + (t[filt] - self.offset) % self.period
        coeff = self.lead * np.asarray(self.coeff)
        # tpow[i, j] = t[i] ^ j
        one = np.ones(t.shape)
        t_pow = np.cumprod([one] + [t] * self.degree, axis=0).T
        poly_values = t_pow @ coeff
        return poly_values * exp_values

    def conjugate(self) -> PolyExp[T]:
        return PolyExp(
            alpha=self.alpha.conjugate(),
            lead=self.lead.conjugate(),
            coeff=self.coeff,
            **self.params,
        )

    def derivative(self, n: int = 1) -> PolyExp:
        if n == 0:
            return self.__copy__()

        match self.alpha:
            case 0:
                coeff = self.coeff
                coeff = [nPr(k, n) * c for k, c in enumerate(coeff) if k >= n]
                return PolyExp(coeff=coeff, lead=self.lead, alpha=self.alpha, **self.params)

            case _ as s:
                deg = self.degree
                O = np.zeros((deg + 1, 1))
                E = np.row_stack([np.column_stack([O[:-1], np.diag(range(1, deg + 1))]), O.T])
                # DEV-NOTE: canot use += due to possible dtype-clash (float + complex)
                E = E + s * np.eye(deg + 1)
                u = np.asarray(self.coeff)
                coeff = (E**n) @ u
                return PolyExp(coeff=coeff, lead=self.lead, alpha=s, **self.params)

    def integral(self, n: int = 1) -> PolyExp:
        '''
        Computes a stem function for the model
        ```
        f(t) = p(t)e^{st}
        ```

        ## Case `s = 0` ##

        Polynomial integral.

        ## Case `s ≠ 0` ##

        - For `x ∈ ℂ`

            ```
            exp_{n}(x) = 0
            ```

            for `n < 0` and

            ```
            exp_{n}(x) := ∑ₖ xᵏ / k! for k=0 ... n
            ```

            for `n ≥ 0`.

        - Then for all `n ∈ ℤ`, `s ∈ ℂ`, `t ∈ ℝ`

            ```
            d/dt exp_{n}(-st) = -s·exp_{n-1}(-st).
            ```

            and thus

            ```
            ∫ s·exp_{n}(-st)·e^{st} dt
            = ∫ exp_{n}(-st) (d/dt e^{st}) dt
            = exp_{n}(-st) e^{st} - ∫ (d/dt exp_{n}(-st)) e^{st} dt
            = exp_{n}(-st) e^{st} + ∫ s·exp_{n-1}(-st) e^{st} dt
            ```

        - It follows that

            ```
            ∫ s·(-st)ⁿ/n! · e^{st} dt
            = ∫ s·(exp_{n}(-st)–exp_{n-1}(-st))·e^{st} dt
            = exp_{n}(-st) e^{st}
            ```

        - Hence

            ```
            ∫ tⁿ · e^{st} dt
            = ∫ s·(-st)ⁿ/n! · e^{st} dt / (s·(-s)ⁿ/n!)
            = exp_{n}(-st)/(s·(-s)ⁿ/n!) e^{st}
            ```

            for all `n ∈ ℕ₀`, `s ∈ ℂ \\ {0}`.
        '''
        if n == 0:
            return self.__copy__()

        match self.alpha:
            case 0:
                coeff = [0] * n + [c / nPr(k + n, n) for k, c in enumerate(self.coeff)]
                return PolyExp[T](coeff=coeff, lead=self.lead, alpha=0, **self.params)

            case _ as s:
                deg = self.degree
                indices = np.asarray(range(1, deg + 1))
                zeroes = np.zeros((deg + 1,))

                coeffs_exp = np.concatenate([[1], np.cumprod(-s / indices)])
                E1 = np.asarray(
                    [
                        np.concatenate(
                            [
                                coeffs_exp[: (k + 1)],
                                zeroes[: deg - k],
                            ]
                        )
                        for k in range(deg + 1)
                    ]
                ).T
                E2 = np.diag(1 / (s * coeffs_exp))
                E = E1 @ E2
                u = np.asarray(self.coeff)
                coeff = (E**n) @ u
                return PolyExp(coeff=coeff, lead=self.lead, alpha=s, **self.params)

    def evaluate(self, *intervals: tuple[float, float]) -> complex:
        '''
        For a model `f(t)` computes `∑ₖ f(bₖ) - f(aₖ)`.

        ## Application ##

        This is particularly useful in combinatio with `self.integral()`,
        ```py
        f.integral((a, b))
        ```
        computes
        ```text
        ∫ f(t) dt from t=a to b
        ```
        and
        ```py
        f.integral((a, b), (c, d))
        ```
        computes
        ```text
        ∫ f(t) dt over t in (a, b) ∪ (c, d),
        ```
        assuming `(a, b) ∪ (c, d)` are disjoint,
        etc.
        '''
        N = len(intervals)
        if N == 0:
            return 0
        times = [a for a, _ in intervals] + [b for _, b in intervals]
        values = self.values(times)
        return sum(values[N:] - values[:N])

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> PolyExp[T]:
        '''
        Let `p` be a `d`-degree polynomial of the form
        ```
        p(t) = exp(bt) ∑ₖ cₖ·tᵏ
        ```
        Computes coeffients of
        ```
        q(t) = p(a·(t + t₀)) = exp(b't) ∑ₖ cₖ·(a·(t + t₀))ᵏ
        ```

        ## Application ##

        The use of this is that we then have
        ```
        p(t) = q((t-t₀)/a) = exp(b'(t-t₀)/a) ∑ₖ c'ₖ·((t - t₀)/a)ᵏ
        ```
        where `c'ₖ =` `k`-th coeff of `q`.

        ## Computing the new coefficients ##

        To compute the coefficients of the polynomial part of `q`,
        observe that
        ```
        ∑ₖ cₖ·(a·(t + t₀))ᵏ
            = ∑ⱼ cⱼaʲ·∑ₖ (j choose k) t₀ʲ⁻ᵏtᵏ
            = ∑ⱼ cⱼ·∑ₖ (j choose k) t₀ʲ⁻ᵏtᵏ
            = ∑ₖ (∑ⱼ (j choose k) cⱼaʲ·t₀ʲ⁻ᵏ) tᵏ
            = ∑ₖ (∑ⱼ (k+j choose k) cₖ₊ⱼaᵏ⁺ʲ·t₀ʲ) tᵏ
        ```
        Let `A` be the `(d+1) x (d+1)` top-left-diagonal matrix with
        ```
        A[k, j] = (k+j choose k) cₖ₊ⱼaᵏ⁺ʲ for 0 ≤ j ≤ d - k
        A[k, j] = 0 for d-k < j ≤ d
        ```
        and let `u` be the `d+1`-dim vector
        ```
        u[j] = t₀ʲ
        ```
        Then
        ```
        (A·u)[k] = ∑ⱼ A[k, j] u[j] from j = 0 to d-k
            = ∑ⱼ (k+j choose k) cⱼ₊ₖaᵏ⁺ʲ·t₀ʲ
            = k-th coeff of polynomial part of q
        ```
        for each k.

        ## Updating the cycle-parameters ##

        If `a > 0`, then for `t = offset'`
        ```
        a·(t + t₀) == offset
        <==> a·(offset' + t₀) == offset
        <==> offset' = offset / a - t₀
        ```
        and for `t = offset' + T`
        ```
        a·(t + t₀) == offset + T
        <==> a·(offset' + t₀ + T) == offset + T
        <==> offset + a·T == offset + T
        <==> T' = T / a.
        ```

        Otherwise, if a < 0, then for `t = offset'`
        ```
        a·(t + t₀) == offset + T
        <==> a·(offset' + t₀) == offset + T
        <==> offset' = (offset + T) / a - t₀
        ```
        and for `t = offset' + T'`
        ```
        a·(t + t₀) == offset
        <==> a·((offset' + T') + t₀) == offset
        <==> offset + T + a·T' == offset
        <==> T' = -T / a
        ```
        '''
        assert a != 0, 'Cannot rescale using 0-values!'

        deg = self.degree

        # compute polynomial part
        a_pow = np.cumprod([1] + [a] * deg)
        coeff = a_pow * self.coeff
        A = np.asarray([[nCr(k + j, k) * x for j, x in enumerate(coeff[k:])] + [0] * k for k in range(deg + 1)])

        t_pow = np.cumprod([1] + [t0] * deg)
        coeff = (A @ t_pow).tolist()

        # update growth + leading const
        lead = self.lead * np.exp(self.alpha * a * t0)
        alpha = self.alpha * a
        params = self.params
        match self.cyclic, a < 0:
            case True, True:
                params = params | {
                    'offset': (self.offset + self.period) / a - t0,
                    'period': self.period / -a,
                }
            case True, _:
                params = params | {
                    'offset': self.offset / a - t0,
                    'period': self.period / a,
                }
            case _:
                pass

        return PolyExp(alpha=alpha, lead=lead, coeff=coeff, **params)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[PolyExp[T], float, float]]:
        '''
        Resolves cyclic models into pieceweise non-cyclic parts.
        This is necessary e.g. as a precursor

        - before algebraically combining current model with non-cyclic models
        - before computing integral / stem functions
        '''
        intervals = merge_intervals(intervals)
        if not self.cyclic:
            for a, b in intervals:
                yield self.__copy__(), a, b
            return

        offset = self.offset
        period = self.period
        safeintervals = list(resolve_intervals(offset=offset, period=period, intervals=intervals))
        for k, a, b in safeintervals:
            '''
            NOTE: We are given a "safe" interval,
            i.e. I = [a, b], where
            t0 + k·T ≤ a < b < t0 + (k+1)·T.
            Given the cyclic nature of the (polynomial part of the) model,
            it holds that

            f(t) = exp(a·t) · ∑ⱼ cⱼ (t – k·T)ʲ

            for t ∈ I.
            '''
            # create a copy of the model, as it will be modified
            f = self.__copy__()
            # remove cyclic aspects
            f.cyclic = False
            f.offset = 0
            f.period = 1
            # temporarily remove non-polynomial aspects
            alpha, f.alpha = f.alpha, 0
            # shift polynomial part
            f = f.rescale(t0=-k * period)
            # add in non-polynomial aspects
            f.alpha = alpha
            yield f, a, b


# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def pre_compare(p: PolyExp, q: PolyExp) -> tuple[list[float], list[float]]:
    m = p.degree
    n = q.degree
    N = max(m, n)
    coeff_p = p.coefficients + [0] * (N - m)
    coeff_q = q.coefficients + [0] * (N - n)
    return coeff_p, coeff_q
