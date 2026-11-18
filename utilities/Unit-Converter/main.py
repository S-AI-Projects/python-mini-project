"""A small, dependency-free unit converter."""

import math
from numbers import Real


_LENGTH_UNITS = {
    "meter": 1.0,
    "meters": 1.0,
    "m": 1.0,
    "kilometer": 1000.0,
    "kilometers": 1000.0,
    "km": 1000.0,
    "centimeter": 0.01,
    "centimeters": 0.01,
    "cm": 0.01,
    "millimeter": 0.001,
    "millimeters": 0.001,
    "mm": 0.001,
    "mile": 1609.344,
    "miles": 1609.344,
    "mi": 1609.344,
    "yard": 0.9144,
    "yards": 0.9144,
    "yd": 0.9144,
    "foot": 0.3048,
    "feet": 0.3048,
    "ft": 0.3048,
    "inch": 0.0254,
    "inches": 0.0254,
    "in": 0.0254,
}

_WEIGHT_UNITS = {
    "kilogram": 1.0,
    "kilograms": 1.0,
    "kg": 1.0,
    "gram": 0.001,
    "grams": 0.001,
    "g": 0.001,
    "milligram": 0.000001,
    "milligrams": 0.000001,
    "mg": 0.000001,
    "metric ton": 1000.0,
    "metric tons": 1000.0,
    "tonne": 1000.0,
    "tonnes": 1000.0,
    "t": 1000.0,
    "pound": 0.45359237,
    "pounds": 0.45359237,
    "lb": 0.45359237,
    "lbs": 0.45359237,
    "ounce": 0.028349523125,
    "ounces": 0.028349523125,
    "oz": 0.028349523125,
}

_TEMPERATURE_UNITS = {
    "celsius": "c",
    "c": "c",
    "centigrade": "c",
    "fahrenheit": "f",
    "f": "f",
    "kelvin": "k",
    "k": "k",
}


def _number(value):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("value must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("value must be finite")
    return number


def _normalize_unit(unit):
    if not isinstance(unit, str):
        raise TypeError("unit must be a string")
    return unit.strip().lower().replace("-", " ").replace("_", " ")


def convert_length(value, from_unit, to_unit):
    """Convert a length value between supported length units."""
    value = _number(value)
    from_unit = _normalize_unit(from_unit)
    to_unit = _normalize_unit(to_unit)
    if from_unit not in _LENGTH_UNITS:
        raise ValueError("unsupported length unit: " + from_unit)
    if to_unit not in _LENGTH_UNITS:
        raise ValueError("unsupported length unit: " + to_unit)
    return value * _LENGTH_UNITS[from_unit] / _LENGTH_UNITS[to_unit]


def convert_weight(value, from_unit, to_unit):
    """Convert a weight/mass value between supported units."""
    value = _number(value)
    from_unit = _normalize_unit(from_unit)
    to_unit = _normalize_unit(to_unit)
    if from_unit not in _WEIGHT_UNITS:
        raise ValueError("unsupported weight unit: " + from_unit)
    if to_unit not in _WEIGHT_UNITS:
        raise ValueError("unsupported weight unit: " + to_unit)
    return value * _WEIGHT_UNITS[from_unit] / _WEIGHT_UNITS[to_unit]


def convert_temperature(value, from_unit, to_unit):
    """Convert a temperature value between Celsius, Fahrenheit, and Kelvin."""
    value = _number(value)
    from_unit = _normalize_unit(from_unit)
    to_unit = _normalize_unit(to_unit)
    if from_unit not in _TEMPERATURE_UNITS:
        raise ValueError("unsupported temperature unit: " + from_unit)
    if to_unit not in _TEMPERATURE_UNITS:
        raise ValueError("unsupported temperature unit: " + to_unit)

    source = _TEMPERATURE_UNITS[from_unit]
    target = _TEMPERATURE_UNITS[to_unit]
    if source == "c":
        celsius = value
    elif source == "f":
        celsius = (value - 32.0) * 5.0 / 9.0
    else:
        celsius = value - 273.15

    if celsius < -273.15:
        raise ValueError("temperature cannot be below absolute zero")

    if target == "c":
        return celsius
    if target == "f":
        return celsius * 9.0 / 5.0 + 32.0
    return celsius + 273.15


def convert_units(value, from_unit, to_unit):
    """Convert a value, selecting the category from the supplied units."""
    from_unit = _normalize_unit(from_unit)
    to_unit = _normalize_unit(to_unit)

    if from_unit in _LENGTH_UNITS and to_unit in _LENGTH_UNITS:
        return convert_length(value, from_unit, to_unit)
    if from_unit in _WEIGHT_UNITS and to_unit in _WEIGHT_UNITS:
        return convert_weight(value, from_unit, to_unit)
    if from_unit in _TEMPERATURE_UNITS and to_unit in _TEMPERATURE_UNITS:
        return convert_temperature(value, from_unit, to_unit)
    raise ValueError("unsupported or incompatible units")


def convert(value, from_unit, to_unit):
    """Alias for convert_units."""
    return convert_units(value, from_unit, to_unit)


def main():
    print("🔄 Unit Converter 🔄")
    print("Convert length, weight, and temperature values.\n")

    while True:
        print("Choose a conversion type:")
        print("1. Length")
        print("2. Weight")
        print("3. Temperature")
        print("4. Exit")

        choice = input("➡️  Enter your choice (1-4): ").strip()
        if choice == "4":
            print("\n👋 Thanks for using Unit Converter!\n")
            return
        if choice not in ("1", "2", "3"):
            print("\n❌ Invalid choice. Please enter 1-4.\n")
            continue

        if choice == "1":
            converter = convert_length
            unit_hint = "m, km, cm, mm, mi, yd, ft, in"
        elif choice == "2":
            converter = convert_weight
            unit_hint = "kg, g, mg, lb, oz"
        else:
            converter = convert_temperature
            unit_hint = "C, F, K"

        try:
            raw_value = input("📝 Enter the value: ").strip()
            value = float(raw_value)
            from_unit = input("➡️  From unit (" + unit_hint + "): ").strip()
            to_unit = input("➡️  To unit (" + unit_hint + "): ").strip()
            result = converter(value, from_unit, to_unit)
            print("\n✨ Result: {} {} = {} {}\n".format(
                value, from_unit, result, to_unit
            ))
        except ValueError as error:
            print("\n❌ " + str(error) + "\n")
        except (TypeError, OverflowError):
            print("\n❌ Please enter a valid number and supported unit.\n")


if __name__ == "__main__":
    main()
