# class Measure:
#     """
#     Implements properties and methods for child classes that also must extend a extension of Unit.

#     Measure must not instantiated itself.
#     """

#     def __init__(self, value, unit):
#         self.__value = value
#         self.__unit = unit

#     @property
#     def value(self):
#         return self.__value

#     @property
#     def unit(self):
#         return self.__unit

#     @property
#     def factor(self):
#         return self.unit_dict.get(self.unit)

#     @property
#     def normal(self):
#         return self.value * self.factor

#     def __str__(self):
#         return f"{self.value} {self.unit} ({self.normal})"

#     def __repr__(self):
#         return f'{self.__class__.__name__}({self.value}, "{self.unit}")'

#     def __eq__(self, other: "Measure"):
#         if isinstance(other, self.__class__):
#             return self.normal == other.normal
#         return False

#     def __hash__(self):
#         return hash(f"{self.__class__}:{float(self.normal)}")

#     def __add__(self, other: "Measure"):
#         if not isinstance(other, self.__class__):
#             msg = f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
#             raise TypeError(msg)
#         return self.__class__((self.normal + other.normal) / self.factor, self.unit)

#     def __sub__(self, other: "Measure"):
#         if not isinstance(other, self.__class__):
#             msg = f"unsupported operand type(s) for -: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
#             raise TypeError(msg)
#         return self.__class__((self.normal - other.normal) / self.factor, self.unit)

#     def __mul__(self, multiplier: float):
#         if not isinstance(multiplier, int | float):
#             msg = f"unsupported operand type(s) for *: '{self.__class__.__name__}' and '{multiplier.__class__.__name__}'"
#             raise TypeError(msg)
#         return self.__class__(self.value * multiplier, self.unit)

#     def __rmul__(self, multiplier: float):
#         if not isinstance(multiplier, int | float):
#             msg = f"unsupported operand type(s) for *: '{multiplier.__class__.__name__}' and '{self.__class__.__name__}'"
#             raise TypeError(msg)
#         return self.__class__(self.value * multiplier, self.unit)

#     def __truediv__(self, divider: float):
#         if not isinstance(divider, int | float):
#             msg = f"unsupported operand type(s) for /: '{self.__class__.__name__}' and '{divider.__class__.__name__}'"
#             raise TypeError(msg)
#         return self.__class__(self.value / divider, self.unit)


class Measure:
    """
    Implements properties and methods for child classes that also must extend a extension of Unit.

    Measure must not instantiated itself.
    """

    def __init__(self, value, unit, unitclass):
        if not isinstance(value, int | float):
            msg = f"unsupported type for value. expected 'int' or 'float', got '{value.__class__.__name__}'"
            raise TypeError(msg)
        unit_trimmed = "".join(unit.lower().split())
        if unitclass.has_unit(unit_trimmed):
            self.__value = value
            self.__unit = unit_trimmed
            self.__unitclass = unitclass
        else:
            msg = f"'{unit}' not found in '{unitclass.__class__.__name__}'"
            raise KeyError(msg)

    @property
    def value(self):
        return self.__value

    @property
    def unit(self):
        return self.__unit

    @property
    def factor(self):
        # return self.unit_dict.get(self.unit)
        # return self.__unitclass.unit_dict.get(self.unit)
        return self.__unitclass.get_factor(self.unit)

    @property
    def normal(self):
        return self.value * self.factor

    def __str__(self):
        return f"{self.value} {self.unit} ({self.normal})"

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value}, "{self.unit}")'

    def __eq__(self, other: "Measure"):
        if isinstance(other, self.__class__):
            return self.normal == other.normal
        return False

    def __hash__(self):
        return hash(f"{self.__class__}:{float(self.normal)}")

    def __add__(self, other: "Measure"):
        if not isinstance(other, self.__class__):
            msg = f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
            raise TypeError(msg)
        return self.__class__((self.normal + other.normal) / self.factor, self.unit)

    def __sub__(self, other: "Measure"):
        if not isinstance(other, self.__class__):
            msg = f"unsupported operand type(s) for -: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
            raise TypeError(msg)
        return self.__class__((self.normal - other.normal) / self.factor, self.unit)

    def __mul__(self, multiplier: float):
        if not isinstance(multiplier, int | float):
            msg = f"unsupported operand type(s) for *: '{self.__class__.__name__}' and '{multiplier.__class__.__name__}'"
            raise TypeError(msg)
        return self.__class__(self.value * multiplier, self.unit)

    def __rmul__(self, multiplier: float):
        if not isinstance(multiplier, int | float):
            msg = f"unsupported operand type(s) for *: '{multiplier.__class__.__name__}' and '{self.__class__.__name__}'"
            raise TypeError(msg)
        return self.__class__(self.value * multiplier, self.unit)

    def __truediv__(self, divider: float):
        if not isinstance(divider, int | float):
            msg = f"unsupported operand type(s) for /: '{self.__class__.__name__}' and '{divider.__class__.__name__}'"
            raise TypeError(msg)
        return self.__class__(self.value / divider, self.unit)
