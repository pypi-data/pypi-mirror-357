"""
Module weight to convert weights.

The module supports
    - metric
    - imperial
"""

from .measure import Measure
from .unit import Unit


class WeightUnit(Unit):
    """Converts between metric, imperial and other weights."""

    def __init__(self):
        super().__init__(
            {
                "kilogram": 1,
                "kg": 1,
                "gram": 0.001,
                "g": 0.001,
                "tonne": 1000,
                "t": 1000,
                "metricton": 1000,
                "pound": 0.45359237,
                "lbs": 0.45359237,
                "ounce": 0.02834952,
                "oz": 0.02834952,
            },
        )

    # imperial
    def in_pound(self, value, unit, ndigits=Unit.NDIGIT):
        """
        Converts a unit to pound.

        Returns a float rounded to ndigits (default=2)
        """
        return self.convert(value, unit, "lbs", ndigits)

    def in_ounce(self, value, unit, ndigits=Unit.NDIGIT):
        """
        Converts a unit to ounce.

        Returns a float rounded to ndigits (default=2)
        """
        return self.convert(value, unit, "oz", ndigits)

    # metric
    def in_gram(self, value, unit, ndigits=Unit.NDIGIT):
        """
        Converts a unit to gram.

        Returns a float rounded to ndigits (default=2)
        """
        return self.convert(value, unit, "g", ndigits)

    def in_kilogram(self, value, unit, ndigits=Unit.NDIGIT):
        """
        Converts a unit to kg.

        Returns a float rounded to ndigits (default=2)
        """
        return self.convert(value, unit, "kg", ndigits)

    def in_tonne(self, value, unit, ndigits=Unit.NDIGIT):
        """
        Converts a unit to metric ton (tonne).

        Returns a float rounded to ndigits (default=2)
        """
        return self.convert(value, unit, "t", ndigits)


# class Weight(WeightUnit, Measure):
#     def __init__(self, value, unit):
#         WeightUnit.__init__(self)
#         Measure.__init__(self, value, unit)


class Weight(Measure):
    def __init__(self, value, unit):
        super().__init__(value, unit, WeightUnit())
