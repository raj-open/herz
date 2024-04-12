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
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar('NUMBER', float, complex)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def duplicates_get_assignment_maps(
    *values_all: list[float],
    eps: float,
    bounds: tuple[float, float] = (-np.inf, np.inf),
) -> tuple[list[float], list[list[int]]]:
    '''
    Catalogues a list of up-to-ε unique values from multiple lists.
    Returns this information in the form of the catalogue and the index-assignments.

    @inputs
    - `*values_all` — one or more lists of values
    - `eps`
    - `bounds` - used for cleanup purposes

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
    catalogue = eps_clean_boundaries(catalogue, eps=eps, bounds=bounds)  # fmt: skip
    catalogue = [value.real for value in catalogue]

    # determine for each array which of the unique values is applicable
    assignments = [closest_indices(values, points=catalogue) for values in values_all]

    return catalogue, assignments


def duplicates_get_assignment_dictionaries(
    *values_all: list[NUMBER],
    eps: float,
    bounds: tuple[float, float] = (-np.inf, np.inf),
) -> tuple[list[NUMBER], list[dict[NUMBER, list[int]]]]:
    '''
    Catalogues a list of up-to-ε unique values from multiple lists.
    Returns this information in the form of the catalogue
    and a dictionary of index-assignments.

    @inputs
    - `*values_all` — one or more lists of values
    - `eps`
    - `bounds` - used for cleanup purposes

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
        bounds=bounds,
    )
    assignments_gathered = [
        {value: [k for k, ii in enumerate(indices) if ii == i] for i, value in enumerate(catalogue)}
        for indices in assignments
    ]
    assignments_gathered = [
        {value: indices for value, indices in infos.items() if len(indices) > 0} for infos in assignments_gathered
    ]
    return catalogue, assignments_gathered
