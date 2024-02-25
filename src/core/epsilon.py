#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from .utils import *
from ..models.enums import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'closest_index',
    'closest_indices',
    'closest_value',
    'closest_values',
    'eps_clean_boundaries',
    'eps_clean_duplicates',
    'eps_clean_zeroes',
    'is_epsilon_eq',
    'normalised_diff_matrix',
    'normalised_difference',
    'normalised_diffs',
    'sign_normalised_diff_matrix',
    'sign_normalised_difference',
    'sign_normalised_diffs',
    'duplicates_get_assignment_maps',
    'duplicates_get_assignment_dictionaries',
    'duplicates_get_assignment_counts',
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar('NUMBER', float, complex)

# ----------------------------------------------------------------
# METHODS - single values
# ----------------------------------------------------------------


def is_epsilon_eq(arg1: NUMBER, arg2: NUMBER, eps: float) -> bool:
    return sign_normalised_difference(x_from=arg1, x_to=arg2, eps=eps) == EnumSign.ZERO


def normalised_difference(x_from: NUMBER, x_to: NUMBER) -> NUMBER:
    '''
    Computes difference `x_to - x_from` relativised.

    NOTE:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.
    '''
    dx = x_to - x_from
    C = max(1.0, (abs(x_from) + abs(x_to)) / 2)
    return dx / C


def sign_normalised_difference(x_from: NUMBER, x_to: NUMBER, eps: float) -> EnumSign:
    r = normalised_difference(x_from, x_to)
    ## FIXME: this does not work in unit-tests!
    # match abs(r.imag) < eps, abs(r.real) < eps, int(np.sign(r.real / eps)):
    #     # if imaginary part is non-zero, then cannot classify in terms of real value position
    #     case (False, _, _):
    #         return EnumSign.NON_ZERO
    #     case (True, False, 1):
    #         return EnumSign.REAL_POSITIVE
    #     case (True, False, -1):
    #         return EnumSign.REAL_NEGATIVE
    #     # case True, True, _:
    #     case _:
    #         return EnumSign.ZERO
    if abs(r.imag) >= eps:
        return EnumSign.NON_ZERO
    elif abs(r.real) < eps:
        return EnumSign.ZERO
    elif np.sign(r.real / eps) == 1:
        return EnumSign.REAL_POSITIVE
    else:
        return EnumSign.REAL_NEGATIVE


# ----------------------------------------------------------------
# METHODS - aligned arrays
# ----------------------------------------------------------------


def normalised_diffs(x_from: Iterable[NUMBER], x_to: Iterable[NUMBER]) -> np.ndarray:
    '''
    Computes difference `x_to - x_from` relativised.

    NOTE:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.
    '''
    x_from = np.asarray(x_from)
    x_to = np.asarray(x_to)
    dx = x_to - x_from
    C = np.maximum(1.0, (abs(x_from) + abs(x_to)) / 2)
    return dx / C


def sign_normalised_diffs(
    x_from: Iterable[NUMBER], x_to: Iterable[NUMBER], eps: float
) -> np.ndarray:
    r = normalised_diffs(x_from=x_from, x_to=x_to)
    check = np.full(r.shape, fill_value=EnumSign.NON_ZERO, dtype=EnumSign)

    cond_is_real = abs(r.imag) < eps
    cond_is_real_zero = cond_is_real & (abs(r.real) < eps)
    cond_sign_real = np.sign(r.real / eps)
    cond_is_real_nonzero = cond_is_real & ~cond_is_real_zero

    check[cond_is_real_nonzero & (cond_sign_real == 1)] = EnumSign.REAL_POSITIVE
    check[cond_is_real_nonzero & (cond_sign_real == -1)] = EnumSign.REAL_NEGATIVE
    check[cond_is_real_zero] = EnumSign.ZERO
    return check


# ----------------------------------------------------------------
# METHODS - non-aligned arrays
# ----------------------------------------------------------------


def normalised_diff_matrix(x_from: Iterable[NUMBER], x_to: Iterable[NUMBER]) -> np.ndarray:
    '''
    Computes difference `x_to - x_from` relativised.

    NOTE:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.
    '''
    x_from = np.asarray(x_from)
    x_to = np.asarray(x_to)
    dx = x_to[:, np.newaxis] - x_from
    C = np.maximum(1.0, (abs(x_from) + abs(x_to[:, np.newaxis])) / 2)
    return dx / C


def sign_normalised_diff_matrix(
    x_from: Iterable[NUMBER], x_to: Iterable[NUMBER], eps: float
) -> np.ndarray:
    r = normalised_diff_matrix(x_from=x_from, x_to=x_to)
    check = np.full(r.shape, fill_value=EnumSign.NON_ZERO, dtype=EnumSign)

    cond_is_real = abs(r.imag) < eps
    cond_is_real_zero = cond_is_real & (abs(r.real) < eps)
    cond_sign_real = np.sign(r.real / eps)
    cond_is_real_nonzero = cond_is_real & ~cond_is_real_zero

    check[cond_is_real_nonzero & (cond_sign_real == 1)] = EnumSign.REAL_POSITIVE
    check[cond_is_real_nonzero & (cond_sign_real == -1)] = EnumSign.REAL_NEGATIVE
    check[cond_is_real_zero] = EnumSign.ZERO
    return check


# ----------------------------------------------------------------
# METHODS - search
# ----------------------------------------------------------------


def closest_index(x: NUMBER, points: Iterable[NUMBER], init: int = 0) -> int:
    try:
        dist = abs(np.asarray(points) - x)
        index = init + dist.argmin()
    except:
        raise ValueError('List of points must be non-empty!')
    return index


def closest_indices(
    X: Iterable[NUMBER],
    points: Iterable[NUMBER],
    init: int = 0,
) -> list[int]:
    indices = [closest_index(x, points, init=init) for x in X]
    return indices


def closest_value(x: NUMBER, points: Iterable[NUMBER]) -> NUMBER:
    i = closest_index(x, points)
    return points[i]


def closest_values(X: list[NUMBER], points: Iterable[NUMBER]) -> list[NUMBER]:
    indices = closest_indices(X, points)
    return [X[i] for i in indices]


# ----------------------------------------------------------------
# METHODS - cleanup
# ----------------------------------------------------------------


def duplicates_get_assignment_maps(
    *values_all: list[NUMBER],
    eps: float,
    boundaries_real: tuple[float, float] = (-np.inf, np.inf),
    boundaries_imag: tuple[float, float] = (-np.inf, np.inf),
    real_valued: bool = False,
) -> tuple[list[NUMBER], list[list[int]]]:
    '''
    Catalogues a list of up-to-ε unique values from multiple lists.
    Returns this information in the form of the catalogue and the index-assignments.

    @inputs
    - `*values_all` — one or more lists of values
    - `eps`
    - `boundaries_real` - used for cleanup purposes
    - `boundaries_imag` - used for cleanup purposes

    @returns
    `(catalogue, assignments)`

    where

    - `catalogue` is the catalogue of unique values.
    - `assignments[i][k] = j` says `values_all[i][k]` is ε-close to `values[j]`
    '''
    # consolidate all values into a single array
    catalogue = flatten(*values_all)

    if len(catalogue) == 0:
        return [], [[] for _ in values_all]

    # determine the unique values up to eps (and clean these up)
    catalogue = eps_clean_duplicates(catalogue, eps=eps)
    catalogue = eps_clean_zeroes(catalogue, eps=eps)
    catalogue = eps_clean_boundaries(catalogue, eps=eps, boundaries_real=boundaries_real, boundaries_imag=boundaries_imag)  # fmt: skip
    if real_valued:
        catalogue = [value.real for value in catalogue]

    # determine for each array which of the unique values is applicable
    assignments = [closest_indices(values, points=catalogue) for values in values_all]

    return catalogue, assignments


def duplicates_get_assignment_dictionaries(
    *values_all: list[NUMBER],
    eps: float,
    boundaries_real: tuple[float, float] = (-np.inf, np.inf),
    boundaries_imag: tuple[float, float] = (-np.inf, np.inf),
    real_valued: bool = False,
) -> tuple[list[NUMBER], list[dict[NUMBER, list[int]]]]:
    '''
    Catalogues a list of up-to-ε unique values from multiple lists.
    Returns this information in the form of the catalogue
    and a dictionary of index-assignments.

    @inputs
    - `*values_all` — one or more lists of values
    - `eps`
    - `boundaries_real` - used for cleanup purposes
    - `boundaries_imag` - used for cleanup purposes

    @returns
    `(catalogue, assignments)`

    where

    - `catalogue` is the catalogue of unique values.
    - `assignments[i]` is a dictionary where
        `assignments[i][value]` is the list of
        those indices of values in `values_all[i]` which are ε-close to `value`.
    '''
    catalogue, assignments = duplicates_get_assignment_maps(
        *values_all,
        eps=eps,
        boundaries_real=boundaries_real,
        boundaries_imag=boundaries_imag,
        real_valued=real_valued,
    )
    assignments_gathered = [
        {
            value: [k for k, ii in enumerate(indices) if ii == i]
            for i, value in enumerate(catalogue)
        }
        for indices in assignments
    ]
    assignments_gathered = [
        {value: indices for value, indices in infos.items() if len(indices) > 0}
        for infos in assignments_gathered
    ]
    return catalogue, assignments_gathered


def duplicates_get_assignment_counts(
    *values_all: list[NUMBER],
    eps: float,
    boundaries_real: tuple[float, float] = (-np.inf, np.inf),
    boundaries_imag: tuple[float, float] = (-np.inf, np.inf),
    real_valued: bool,
) -> list[dict[NUMBER, int]]:
    '''
    Catalogues a list of up-to-ε unique values from multiple lists.
    Returns this information in the form of the catalogue
    and a dictionary of index-assignments.

    @inputs
    - `*values_all` — one or more lists of values
    - `eps`
    - `boundaries_real` - used for cleanup purposes
    - `boundaries_imag` - used for cleanup purposes

    @returns
    `(catalogue, counts)`

    where

    - `catalogue` is the catalogue of unique values.
    - `counts[i]` is a dictionary where
        `counts[i][value]` is the number of values in `values_all[i]`
        which are ε-close to `value`.
    '''
    catalogue, assignments = duplicates_get_assignment_dictionaries(
        *values_all,
        eps=eps,
        boundaries_real=boundaries_real,
        boundaries_imag=boundaries_imag,
        real_valued=real_valued,
    )
    counts = [
        {value: len(indices) for value, indices in assignment.items()}
        for assignment in assignments
    ]
    return catalogue, counts


def eps_clean_duplicates(
    values: list[NUMBER],
    eps: float,
) -> list[NUMBER]:
    if len(values) == 0:
        return []

    # --------------------------------
    # NOTE:
    # 1) Sort based on real part.
    # 2) Sorting of the imaginary part is not important.
    #    Just do this for efficiency.
    # --------------------------------
    values = sorted(values, key=lambda x: (x.real, x.imag))
    D = sign_normalised_diff_matrix(x_from=values, x_to=values, eps=eps)
    values_unique = []
    indices_ignore = []
    for i, value in enumerate(values):
        if i in indices_ignore:
            continue
        indices_ignore += characteristic_to_where(D[i, :] == EnumSign.ZERO)
        values_unique.append(value)

    return values_unique


def eps_clean_zeroes(
    values: Iterable[NUMBER],
    eps: float,
) -> list[NUMBER]:
    '''
    Cleans up values that are ε-close to being real-/imag-valued
    '''
    values = eps_clean_real(values, x=0, eps=eps)
    values = eps_clean_imag(values, x=0, eps=eps)
    return values


def eps_clean_boundaries(
    values: Iterable[NUMBER],
    eps: float,
    boundaries_real: tuple[float, float] = (-np.inf, np.inf),
    boundaries_imag: tuple[float, float] = (-np.inf, np.inf),
) -> list[NUMBER]:
    '''
    Clean up values that are ε-close to boundaries (treated box-like)
    '''
    for u in boundaries_real:
        if abs(u) < np.inf:
            values = eps_clean_real(values, x=u, eps=eps)

    for u in boundaries_imag:
        if abs(u) < np.inf:
            values = eps_clean_imag(values, x=u, eps=eps)

    return values


def eps_clean_real(
    values: Iterable[NUMBER],
    x: float,
    eps: float,
) -> list[complex]:
    '''
    Forces the real-part of values that are ε-close to a certain value, `x`, to be `x`.
    '''
    values = np.asarray(values, dtype=complex)
    d = sign_normalised_diff_matrix(x_from=[x], x_to=values.real, eps=eps)
    d = d.reshape(values.shape)
    values[d == EnumSign.ZERO] = x + 1j * values[d == EnumSign.ZERO].imag
    return values.tolist()


def eps_clean_imag(
    values: Iterable[NUMBER],
    x: float,
    eps: float,
) -> list[complex]:
    '''
    Forces the imag-part of values that are ε-close to a certain value, `x`, to be `x`.
    '''
    values = np.asarray(values, dtype=complex)
    d = sign_normalised_diff_matrix(x_from=[x], x_to=values.imag, eps=eps)
    d = d.reshape(values.shape)
    values[d == EnumSign.ZERO] = values[d == EnumSign.ZERO].real + 1j * x
    return values.tolist()
