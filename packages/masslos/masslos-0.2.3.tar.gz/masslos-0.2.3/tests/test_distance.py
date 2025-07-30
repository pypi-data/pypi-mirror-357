import unittest

from masslos.distance import Distance, DistanceUnit


class TestDistanceUnit(unittest.TestCase):
    def setUp(self):
        self.distance = DistanceUnit()

    def test_metric(self):
        self.assertEqual(self.distance.convert(1, "m", "dm"), 10)
        self.assertEqual(self.distance.convert(0, "m", "dm"), 0)
        self.assertEqual(self.distance.convert(-5, "m", "dm"), -50)

    def test_imperial(self):
        self.assertAlmostEqual(self.distance.convert(1, "FEET", "INCH"), 12)

    def test_non_value(self):
        self.assertIsNone(self.distance.convert("foo", "m", "cm"))

    def test_key_tolerance(self):
        self.assertIsNotNone(self.distance.convert(1, "m", "dm"))
        self.assertIsNotNone(self.distance.convert(1, "m", "DM"))
        self.assertIsNotNone(self.distance.convert(1, "M", "dm"))
        self.assertIsNotNone(self.distance.convert(1, "M", "DM"))
        self.assertIsNotNone(self.distance.convert(1, "m", "dM"))
        self.assertIsNotNone(self.distance.convert(1, "m", "Dm"))
        self.assertIsNotNone(self.distance.convert(1, "Light Year", "Km"))

    def test_key_unknwon(self):
        self.assertIsNone(self.distance.convert(1, "foo", "m"))
        self.assertIsNone(self.distance.convert(1, "m", "foo"))
        self.assertIsNone(self.distance.convert(1, "foo", "foo"))


class TestDistance(unittest.TestCase):
    def setUp(self):
        self.distance = Distance(1, "km")
        self.distance2 = Distance(2000, "m")

    def test_initial_value_and_unit(self):
        self.assertEqual(self.distance.value, 1)
        self.assertEqual(self.distance.unit.lower().strip(), "km")
        self.assertEqual(self.distance2.value, 2000)
        self.assertEqual(self.distance2.unit.lower().strip(), "m")

    def test_factor_and_normal(self):
        self.assertEqual(self.distance.factor, 1000)
        self.assertEqual(self.distance.normal, 1000)
        self.assertEqual(self.distance2.factor, 1)
        self.assertEqual(self.distance2.normal, 2000)

    def test_equality_and_hashability(self):
        self.assertEqual(self.distance, Distance(1000, "m"))
        self.assertNotEqual(self.distance, self.distance2)
        self.assertNotEqual(self.distance.__hash__, self.distance2.__hash__)
        self.assertEqual(
            self.distance.__hash__(),
            hash(f"{self.distance.__class__}:1000.0"),
            # hash("<class 'masslos.distance.Distance'>:1.0"),
        )
        self.assertEqual(
            self.distance2.__hash__(),
            hash(f"{self.distance2.__class__}:2000.0"),
        )

    def test_calculating(self):
        self.assertEqual((self.distance + self.distance2).value, 3)
        self.assertEqual((self.distance - self.distance2).value, -1)
        self.assertEqual((self.distance2 * 3).value, 6_000)
        self.assertEqual((self.distance / 4).value, 0.25)
        self.assertEqual((2 * self.distance).value, 2)
        with self.assertRaises(TypeError):
            self.distance + 4
        with self.assertRaises(TypeError):
            self.distance - 4
        with self.assertRaises(TypeError):
            self.distance * self.distance2
        with self.assertRaises(TypeError):
            self.distance / self.distance2

    def test_invalid_value(self):
        # w = Distance("abc", "kg")
        # self.assertRaises(TypeError, Distance, "abc", "kg")
        with self.assertRaises(TypeError):
            Distance("abc", "km")
        with self.assertRaises(TypeError):
            Distance("10", "mi")

    def test_invalid_unit(self):
        with self.assertRaises(KeyError):
            Distance(1, "pfund")
        with self.assertRaises(KeyError):
            Distance(1, "kilo grams")

    def test_case_insensitivity_and_spaces(self):
        w = Distance(1, " Kilo meTer ")
        x = Distance(1000, " m E t E r     ")
        self.assertEqual(w.unit, "kilometer")
        self.assertEqual(x.unit, "meter")
        self.assertEqual(w, x)


if __name__ == "__main__":
    unittest.main()
