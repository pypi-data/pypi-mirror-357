import unittest

from masslos.measure import Measure
from masslos.unit import Unit


class DummyUnit(Unit):
    """Converts between metric, imperial and other distances."""

    def __init__(self):
        super().__init__(
            {
                "m": 1,
                "cm": 0.01,
                "mm": 0.001,
            },
        )


class DummyMeasure(Measure):
    def __init__(self, value, unit):
        super().__init__(value, unit, DummyUnit())


class TestMeasure(unittest.TestCase):
    def setUp(self):
        self.m1 = DummyMeasure(10, "m")
        self.m2 = DummyMeasure(1000, "cm")
        self.m3 = DummyMeasure(10000, "mm")

    def test_value_property(self):
        self.assertEqual(self.m1.value, 10)
        self.assertEqual(self.m2.value, 1000)
        self.assertEqual(self.m3.value, 10000)

    def test_unit_property(self):
        self.assertEqual(self.m1.unit, "m")
        self.assertEqual(self.m2.unit, "cm")
        self.assertEqual(self.m3.unit, "mm")

    def test_factor_property(self):
        self.assertEqual(self.m1.factor, 1.0)
        self.assertEqual(self.m2.factor, 0.01)
        self.assertEqual(self.m3.factor, 0.001)

    def test_normal_property(self):
        self.assertEqual(self.m1.normal, 10.0)
        self.assertEqual(self.m2.normal, 10.0)
        self.assertEqual(self.m3.normal, 10.0)

    def test_str_repr(self):
        self.assertIn("10 m", str(self.m1))
        self.assertIn("10", str(self.m1))
        self.assertEqual(repr(self.m1), 'DummyMeasure(10, "m")')

    def test_add(self):
        result = self.m1 + self.m2
        self.assertIsInstance(result, DummyMeasure)
        self.assertAlmostEqual(result.value, 20)
        self.assertEqual(result.unit, "m")

    def test_sub(self):
        result = self.m1 - self.m2
        self.assertIsInstance(result, DummyMeasure)
        self.assertAlmostEqual(result.value, 0)
        self.assertEqual(result.unit, "m")

    def test_mul(self):
        result = self.m1 * 2
        self.assertIsInstance(result, DummyMeasure)
        self.assertEqual(result.value, 20)
        self.assertEqual(result.unit, "m")

    def test_truediv(self):
        result = self.m1 / 2
        self.assertIsInstance(result, DummyMeasure)
        self.assertEqual(result.value, 5)
        self.assertEqual(result.unit, "m")

    def test_add_different_units(self):
        # Adding m1 (10 m) and m3 (10000 mm), both normal=10.0
        result = self.m1 + self.m3
        self.assertAlmostEqual(result.value, 20)
        self.assertEqual(result.unit, "m")

    def test_sub_different_units(self):
        # Subtracting m2 (1000 cm, normal=10) from m3 (10000 mm, normal=10)
        result = self.m3 - self.m2
        self.assertAlmostEqual(result.value, 0)
        self.assertEqual(result.unit, "mm")


if __name__ == "__main__":
    unittest.main()
