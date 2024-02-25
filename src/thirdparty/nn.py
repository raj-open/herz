#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from sklearn.neighbors import KDTree
from sklearn.neighbors import NearestNeighbors

import numpy as np

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def nearest_neighbours(
    X: np.ndarray,
    k: int = 1,
) -> np.ndarray:
    kdt = KDTree(X, leaf_size=30, metric='euclidean')
    indices = kdt.query(X, k=k, return_distance=False)
    # nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree')
    # nbrs = nbrs.fit(X)
    # _, indices = nbrs.kneighbors(X)
    return indices


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'nearest_neighbours',
]
