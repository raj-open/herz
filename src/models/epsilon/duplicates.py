#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.utils import *
from ..enums import *
from .clean import *
from .search import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'duplicates_get_assignment_maps',
    'duplicates_get_assignment_dictionaries',
    'duplicates_get_assignment_counts',
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar('NUMBER', float, complex)

# ----------------------------------------------------------------
# METHODS
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
        {value: [k for k, ii in enumerate(indices) if ii == i] for i, value in enumerate(catalogue)}
        for indices in assignments
    ]
    assignments_gathered = [
        {value: indices for value, indices in infos.items() if len(indices) > 0} for infos in assignments_gathered
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
    counts = [{value: len(indices) for value, indices in assignment.items()} for assignment in assignments]
    return catalogue, counts
