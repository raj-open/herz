#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from tests.unit.__paths__ import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

_module = get_module(__file__)

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_trig_ALGEBRA(test: TestCase, omega: float, C: float, C2: float):
    f = PolyTrig(omega=omega, coeff=[0, -8, 5, 3], lead=C * C2)
    p = Poly[float](coeff=[-1, 1], lead=C)
    xi = PolyTrig(omega=omega, lead=C2, coeff=[0, 8, 3])
    g = xi * p
    test.assertIsInstance(g, PolyTrig)
    test.assertEqual(g.omega, f.omega)
    assert np.isclose(g.coefficients, f.coefficients, rtol=1e-7).all()

    # poly multiplication dominates
    g = PolyTrig.cast(p * xi)
    test.assertEqual(g.omega, f.omega)
    assert np.isclose(g.coefficients, f.coefficients, rtol=1e-7).all()
    return


def test_cos_ALGEBRA(
    test: TestCase,
    omega: float,
    C: float,
):
    f = PolyTrig(omega=omega, coeff=[-1, 3, 0.8], lead=C)
    p = Poly(coeff=[-1, 3, 0.8])
    osc = Cos(omega=omega, lead=C)

    g = osc * p
    test.assertIsInstance(g, PolyTrig)
    test.assertEqual(g.omega, f.omega)
    assert np.isclose(g.coefficients, f.coefficients, rtol=1e-7).all()

    # poly multiplication dominates
    g = PolyTrig.cast(p * osc)
    test.assertEqual(g.omega, f.omega)
    assert np.isclose(g.coefficients, f.coefficients, rtol=1e-7).all()
    return


def test_polytrig_DERIVATIVES(
    test: TestCase,
    omega: float,
):
    f = PolyTrig(omega=omega, coeff=[-1, 3, 0.8])
    f = f.derivative()
    test.assertEqual(f.omega, omega)
    test.assertEqual(f.coefficients, [1j * omega * -1 + 3, 1j * omega * 3 + 2 * 0.8, 1j * omega * 0.8])
    return


def test_polytrig_INTEGRALS(
    test: TestCase,
    omega: float,
    C_complex: complex,
):
    f = PolyTrig(omega=omega, coeff=[-1, 3, 0.8], lead=C_complex)
    F = f.integral()
    f_ = F.derivative()
    test.assertEqual(f.omega, f_.omega)
    assert np.isclose(f.coefficients, f_.coefficients, rtol=1e-7).all()
    return


def test_cos_VALUES(
    test: TestCase,
    omega: float,
    C: float,
    time_values: np.ndarray,
):
    f = Cos(omega=omega, lead=C)
    result = f.values(time_values)
    expected = C * np.cos(omega * time_values)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


def test_cos_DERIVATIVES(
    test: TestCase,
    omega: float,
    C: float,
):
    f = Cos(omega=omega, lead=C)
    f = f.derivative()
    test.assertIsInstance(f, Sin)
    test.assertEqual(f.omega, omega)
    test.assertEqual(f.amplitude, -omega * C)
    return


def test_cos_INTEGRALS(
    test: TestCase,
    omega: float,
    C: float,
):
    f = Cos(omega=omega, lead=C)
    f = f.integral()
    test.assertIsInstance(f, Sin)
    test.assertEqual(f.omega, omega)
    test.assertEqual(f.amplitude, C / omega)
    return


def test_sin_VALUES(
    test: TestCase,
    omega: float,
    C: float,
    time_values: np.ndarray,
):
    f = Sin(omega=omega, lead=C)
    result = f.values(time_values)
    expected = C * np.sin(omega * time_values)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


def test_sin_DERIVATIVES(
    test: TestCase,
    omega: float,
    C: float,
):
    f = Sin(omega=omega, lead=C)
    f = f.derivative()
    test.assertIsInstance(f, Cos)
    test.assertEqual(f.omega, omega)
    test.assertEqual(f.amplitude, omega * C)
    return


def test_sin_INTEGRALS(
    test: TestCase,
    omega: float,
    C: float,
):
    f = Sin(omega=omega, lead=C)
    f = f.integral()
    test.assertIsInstance(f, Cos)
    test.assertEqual(f.omega, omega)
    test.assertEqual(f.amplitude, -C / omega)
    return
