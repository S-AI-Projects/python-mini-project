# 🔄 Unit Converter

Unit Converter is a beginner-friendly, dependency-free utility for converting
length, weight (mass), and temperature values.

## Run

From the repository root:

```bash
python3 utilities/Unit-Converter/main.py
```

## Exact CLI example

The prompts and output use this format:

```text
Choose a conversion type:
1. Length
2. Weight
3. Temperature
4. Exit
➡️  Enter your choice (1-4): 1
📝 Enter the value: 100
➡️  From unit (m, km, cm, mm, mi, yd, ft, in): cm
➡️  To unit (m, km, cm, mm, mi, yd, ft, in): m

✨ Result: 100.0 cm = 1.0 m
```

Temperature example:

```text
Choose a conversion type:
1. Length
2. Weight
3. Temperature
4. Exit
➡️  Enter your choice (1-4): 3
📝 Enter the value: 32
➡️  From unit (C, F, K): F
➡️  To unit (C, F, K): C

✨ Result: 32.0 F = 0.0 C
```

Enter `4` at the main menu to exit. Invalid menu choices, values, and units
print a clear error and return to the menu.

## Supported units

Length: `meter/m`, `kilometer/km`, `centimeter/cm`,
`millimeter/mm`, `mile/mi`, `yard/yd`, `foot/ft`, and `inch/in`.

Weight/mass: `kilogram/kg`, `gram/g`, `milligram/mg`, `metric ton/t`,
`pound/lb/lbs`, and `ounce/oz`.

Temperature: `Celsius/C`, `Fahrenheit/F`, and `Kelvin/K`. The converter
accepts full unit names and common abbreviations.

## Supported limits

- Input values must be finite real numbers; strings that `float()` can parse
  are accepted by the CLI.
- Unit names are case-insensitive and surrounding whitespace is ignored.
- Length and weight conversions support positive and negative values.
- Temperature supports Celsius, Fahrenheit, and Kelvin; Kelvin input below
  absolute zero is not represented by the implementation.
- There is no fixed maximum input magnitude. Extremely large finite values
  may overflow to infinity during conversion and are not guaranteed to be
  usable.
- Importable core functions: `convert_length`, `convert_weight`,
  `convert_temperature`, `convert_units`, and `convert`.
