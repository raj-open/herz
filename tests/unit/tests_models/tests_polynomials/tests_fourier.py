#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.__paths__ import *
from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from src.thirdparty.maths import *
from src.thirdparty.types import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

_module = get_module(__file__)

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("coeff",),
    [
        ([3, 0.5, -0.8, 1.7],),
        ([1],),
        ([0, 1],),
        ([0, 0, 1],),
        ([1, -2, 1],),
    ],
)
def test_fourier_of_polynomial_CASES(
    test: TestCase,
    # test parameters
    coeff: list[float],
):
    n_max = 3
    p = Poly(coeff=coeff)

    # n-values for which to compute Fourier transform
    n_values = np.asarray(range(n_max + 1))

    # compute integral coefficients 'by hand':
    N = 10000
    t = np.linspace(start=0, stop=1, num=N, endpoint=False)
    func_values = p.values(t)
    kernel = np.exp(-1j * 2 * pi * (n_values[:, np.newaxis] * t))
    dt = 1 / N
    F_manual = (kernel @ func_values) * dt

    # compute using method:
    F0, F = fourier_of_polynomial(p)
    F_method = [F0, *F.values(1 / n_values[1:]).tolist()]

    # verify correctness of method:
    np.testing.assert_array_almost_equal(F_method, F_manual, decimal=4)
    return
