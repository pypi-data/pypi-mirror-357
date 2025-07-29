"""Tests for utils module"""

import unittest

import numpy as np

from gpkit import Model, NomialArray, Variable, parse_variables, units
from gpkit.util.repr_conventions import unitstr
from gpkit.util.small_classes import HashVector


class OnlyVectorParse(Model):
    """
    Variables of length 3
    ---------------------
    x    [-]    just another variable
    """

    @parse_variables(__doc__, globals())
    def setup(self):
        pass


class Fuselage(Model):
    """The thing that carries the fuel, engine, and payload

    Variables
    ---------
    f                [-]             Fineness
    g          9.81  [m/s^2]         Standard gravity
    k                [-]             Form factor
    l                [ft]            Length
    mfac       2.0   [-]             Weight margin factor
    R                [ft]            Radius
    rhocfrp    1.6   [g/cm^3]        Density of CFRP
    rhofuel    6.01  [lbf/gallon]    Density of 100LL fuel
    S                [ft^2]          Wetted area
    t          0.024 [in]            Minimum skin thickness
    Vol              [ft^3]          Volume
    W                [lbf]           Weight

    Upper Unbounded
    ---------------
    k, W

    """

    # pylint: disable=undefined-variable, invalid-name
    @parse_variables(__doc__, globals())
    def setup(self, Wfueltot):
        return [
            f == l / R / 2,
            k >= 1 + 60 / f**3 + f / 400,
            3 * (S / np.pi) ** 1.6075
            >= 2 * (l * R * 2) ** 1.6075 + (2 * R) ** (2 * 1.6075),
            Vol <= 4 * np.pi / 3 * (l / 2) * R**2,
            Vol >= Wfueltot / rhofuel,
            W / mfac >= S * rhocfrp * t * g,
        ]


class TestDocstring(unittest.TestCase):
    """TestCase for docstring utilities"""

    def test_vector_only_parse(self):
        # pylint: disable=no-member
        m = OnlyVectorParse()
        self.assertTrue(hasattr(m, "x"))
        self.assertIsInstance(m.x, NomialArray)
        self.assertEqual(len(m.x), 3)

    def test_parse_variables(self):
        Fuselage(Variable("Wfueltot", 5, "lbf"))


class TestHashVector(unittest.TestCase):
    """TestCase for the HashVector class"""

    def test_init(self):
        """Make sure HashVector acts like a dict"""
        # args and kwargs
        hv = HashVector([(2, 3), (1, 10)], dog="woof")
        self.assertTrue(isinstance(hv, dict))
        self.assertEqual(hv, {2: 3, 1: 10, "dog": "woof"})
        # no args
        self.assertEqual(HashVector(), {})
        # creation from dict
        self.assertEqual(HashVector({"x": 7}), {"x": 7})

    def test_neg(self):
        """Test negation"""
        hv = HashVector(x=7, y=0, z=-1)
        self.assertEqual(-hv, {"x": -7, "y": 0, "z": 1})

    def test_pow(self):
        """Test exponentiation"""
        hv = HashVector(x=4, y=0, z=1)
        self.assertEqual(hv**0.5, {"x": 2, "y": 0, "z": 1})
        with self.assertRaises(TypeError):
            _ = hv**hv
        with self.assertRaises(TypeError):
            _ = hv ** "a"

    def test_mul_add(self):
        """Test multiplication and addition"""
        a = HashVector(x=1, y=7)
        b = HashVector()
        c = HashVector(x=3, z=4)
        # nonsense multiplication
        with self.assertRaises(TypeError):
            _ = a * set()
        # multiplication and addition by scalars
        r = a * 0
        self.assertEqual(r, HashVector(x=0, y=0))
        self.assertTrue(isinstance(r, HashVector))
        r = a - 2
        self.assertEqual(r, HashVector(x=-1, y=5))
        self.assertTrue(isinstance(r, HashVector))
        with self.assertRaises(TypeError):
            _ = r + "a"
        # multiplication and addition by dicts
        self.assertEqual(a + b, a)
        self.assertEqual(a + b + c, HashVector(x=4, y=7, z=4))


class TestSmallScripts(unittest.TestCase):
    """TestCase for gpkit.small_scripts"""

    def test_unitstr(self):
        x = Variable("x", "ft")
        # pint issue 356
        footstrings = ("ft", "foot")  # backwards compatibility with pint 0.6
        self.assertEqual(unitstr(Variable("n", "count")), "count")
        self.assertIn(unitstr(x), footstrings)
        self.assertIn(unitstr(x.key), footstrings)
        self.assertEqual(unitstr(Variable("y"), dimless="---"), "---")
        self.assertEqual(unitstr(None, dimless="--"), "--")

    def test_pint_366(self):
        # test for https://github.com/hgrecco/pint/issues/366
        self.assertIn(unitstr(units("nautical_mile")), ("nmi", "nautical_mile"))
        self.assertEqual(units("nautical_mile"), units("nmi"))


TESTS = [TestDocstring, TestHashVector, TestSmallScripts]


if __name__ == "__main__":  # pragma: no cover
    # pylint: disable=wrong-import-position
    from gpkit.tests.helpers import run_tests

    run_tests(TESTS)
