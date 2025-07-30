import unittest

from masslos.weight import Weight, WeightUnit


class TestWeightUnit(unittest.TestCase):
    def setUp(self):
        self.weight = WeightUnit()

    def test_convert_weight_kg_to_g(self):
        self.assertEqual(self.weight.convert(1, "kg", "g"), 1000)

    def test_convert_weight_g_to_kg(self):
        self.assertEqual(self.weight.convert(1000, "g", "kg"), 1)

    def test_convert_weight_lb_to_kg(self):
        self.assertAlmostEqual(self.weight.convert(2.20462, "lbs", "kg"), 1, places=3)

    def test_convert_weight_kg_to_lb(self):
        self.assertAlmostEqual(
            self.weight.convert(1, "kg", "lbs", 5),
            2.20462,
            places=3,
        )

    def test_convert_weight_oz_to_g(self):
        self.assertAlmostEqual(self.weight.convert(1, "oz", "g"), 28.34952, places=3)

    def test_convert_weight_tonne_to_kg(self):
        self.assertEqual(self.weight.convert(1, "t", "kg"), 1000)

    def test_convert_weight_invalid_unit(self):
        self.assertIsNone(self.weight.convert(1, "foo", "kg"))

    def test_convert_weight_invalid_value(self):
        self.assertIsNone(self.weight.convert("abc", "kg", "g"))

    def test_in_pound(self):
        self.assertAlmostEqual(self.weight.in_pound(1, "kg", 5), 2.20462, places=3)

    def test_in_ounce(self):
        self.assertAlmostEqual(self.weight.in_ounce(1, "kg", 5), 35.27396, places=3)

    def test_in_gram(self):
        self.assertEqual(self.weight.in_gram(1, "kg"), 1000)

    def test_in_kilogram(self):
        self.assertEqual(self.weight.in_kilogram(1000, "g"), 1)

    def test_in_tonne(self):
        self.assertEqual(self.weight.in_tonne(1000, "kg"), 1)

    def test_case_insensitivity_and_spaces(self):
        self.assertEqual(self.weight.convert(1, " KiloGram ", " g "), 1000)


class TestWeight(unittest.TestCase):
    def setUp(self):
        self.weight = Weight(1, "kg")
        self.weight2 = Weight(2000, "g")

    def test_initial_value_and_unit(self):
        self.assertEqual(self.weight.value, 1)
        self.assertEqual(self.weight.unit.lower().strip(), "kg")
        self.assertEqual(self.weight2.value, 2000)
        self.assertEqual(self.weight2.unit.lower().strip(), "g")

    def test_factor_and_normal(self):
        self.assertEqual(self.weight.factor, 1)
        self.assertEqual(self.weight.normal, 1)
        self.assertEqual(self.weight2.factor, 0.001)
        self.assertEqual(self.weight2.normal, 2)

    def test_equality_and_hashability(self):
        self.assertEqual(self.weight, Weight(1000, "g"))
        self.assertNotEqual(self.weight, self.weight2)
        self.assertNotEqual(self.weight.__hash__, self.weight2.__hash__)
        self.assertEqual(
            self.weight.__hash__(),
            hash(f"{self.weight.__class__}:1.0"),
            # hash("<class 'masslos.weight.Weight'>:1.0"),
        )
        self.assertEqual(
            self.weight2.__hash__(),
            hash(f"{self.weight2.__class__}:2.0"),
        )

    def test_calculating(self):
        self.assertEqual((self.weight + self.weight2).value, 3)
        self.assertEqual((self.weight - self.weight2).value, -1)
        self.assertEqual((self.weight2 * 3).value, 6_000)
        self.assertEqual((self.weight / 4).value, 0.25)
        self.assertEqual((2 * self.weight).value, 2)
        with self.assertRaises(TypeError):
            self.weight + 4
        with self.assertRaises(TypeError):
            self.weight - 4
        with self.assertRaises(TypeError):
            self.weight * self.weight2
        with self.assertRaises(TypeError):
            self.weight / self.weight2

    def test_invalid_value(self):
        # w = Weight("abc", "kg")
        # self.assertRaises(TypeError, Weight, "abc", "kg")
        with self.assertRaises(TypeError):
            Weight("abc", "kg")
        with self.assertRaises(TypeError):
            Weight("10", "lbs")

    def test_invalid_unit(self):
        with self.assertRaises(KeyError):
            Weight(1, "pfund")
        with self.assertRaises(KeyError):
            Weight(1, "kilo grams")

    def test_case_insensitivity_and_spaces(self):
        w = Weight(1, " Kilo gram ")
        x = Weight(1000, " gRaM     ")
        self.assertEqual(w.unit, "kilogram")
        self.assertEqual(x.unit, "gram")
        self.assertEqual(w, x)


if __name__ == "__main__":
    unittest.main()
