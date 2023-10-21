#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.thirdparty.unit import *

from src.core.poly import *
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


@mark.parametrize(
    ('p',),
    [
        ([1],),
        ([0, 1],),
        ([0, 0, 1],),
        ([1, -2, 1],),
        ([3, 0.5, -0.8, 1.7],),
    ],
)
def test_fourier_of_polynomial_rote(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    p: list[float],
):
    # compute integral coefficients 'by hand':
    deg = len(p) - 1
    n_max = 3
    N = 10000
    one = np.ones(shape=(N,))
    t = np.linspace(start=0, stop=1, num=N, endpoint=False)
    dt = 1 / N
    f = np.asarray(range(n_max + 1))
    kernel = np.exp(-1j * 2 * pi * (f[:, np.newaxis] * t))
    func_values = np.cumprod([one] + [t] * deg, axis=0).T @ np.asarray(p)
    F_manual = (kernel @ func_values) * dt

    # compute using method:
    F0, coeff_top, coeff_bot = fourier_of_polynomial(p)
    F = lambda n: poly_single(n, *coeff_top) / poly_single(n, *coeff_bot)
    F_method = [F0] + list(map(F, range(1, n_max + 1)))

    # verify correctness of method:
    assert_arrays_close(F_method, F_manual, eps=0.5e-3)
    return
