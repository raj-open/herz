#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.thirdparty.unit import *

from src.core.signal import *
from src.core.constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FIXTURES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def test_fourier_of_monomials(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
):
    # compute integral coefficients 'by hand':
    k_max = 5
    n_max = 10
    N = 10000
    one = np.ones(shape=(N,))
    t = np.linspace(start=0, stop=1, num=N, endpoint=False)
    f = np.asarray(range(n_max + 1))
    dt = 1 / N
    t_pow = np.cumprod([one] + [t] * k_max, axis=0)
    kernel = np.exp(1j * 2 * pi * (t[:, np.newaxis] * f))
    F_manual = (t_pow @ kernel) * dt

    # compute using method:
    F_monoms = list(fourier_of_monomials(k_max=k_max))
    F_method = np.asarray([[FF(n) for n in range(n_max + 1)] for FF in F_monoms])

    # verify correctness of method:
    for k, FF in enumerate(F_monoms):
        test.assertEquals(FF(0), 1 / (k + 1))
    assert_arrays_close(F_method, F_manual, eps=0.5e-3)
    return
