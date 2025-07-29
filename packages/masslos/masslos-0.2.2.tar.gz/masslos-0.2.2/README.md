# ***Maßlos*** unit conversion library

![coverage](https://img.shields.io/badge/coverage-20%25-yellowgreen)
![version](https://img.shields.io/badge/version-0.2.0-blue)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Set of functions to convert between different units including metric and imperial

< Add an optional screenshot of your project below >

![]()

**Table of Contents**

- [Installation](#installation)
- [Execution / Usage](#execution--usage)
- [Technologies](#technologies)
- [Features](#features)
- [Author](#author)
- [Change log](#change-log)
- [License](#license)

## Installation

On macOS and Linux:

```sh
$ python -m pip install masslos
```

On Windows:

```sh
PS> python -m pip install masslos
```

## Execution / Usage

Here are a few examples of using the **`masslos`** library in your code:

```python
from masslos import Distance, Speed, Weight
...
```

```python
# without specifying the decimal digits (default = 2)
w = Weight()
s = Speed()
d = Distance()

dist_in_meter = d.convert(10, "yd", "m")
weight_in_kg = w.convert(11, "lbs", "kg")

print("Speed units:")
print(s.list_units())
```

```python
# with specifying the decimal digits
w = Weight()
s = Speed()
d = Distance()

dist_in_meter = d.convert(value=10, from_unit="yd", to_unit="m", ndigits=3)
weight_in_kg = w.convert(value=11, from_unit="lbs", to_unit="kg", ndigits=3)
```

For more examples, please refer to the project's [Wiki](wiki) or [documentation page](docs).

## Technologies

**`masslos`** uses the following technologies and tools:

- [Python](https://www.python.org/): ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Features

**`masslos`** currently has the following set of features:

- Converting **distances** including
    - metric
    - imperial
    - astronomical
- Converting **weights** including
    - metric
    - imperial
- Converting **speeds**

## Author

Andreas Haberl – # – develop@haberl-info.de

## Change log

- 0.2.2
    - fix: packaging
- 0.2.1
    - feat: add Speed class
    - feat: changing to class based API<br>
            BREAKING CHANGE: use instance methods instead of function calls
    - feat: add function "list_units"
    - test: updates
    - docs: update README.md
- 0.2.0
    - feat: argument for precision of conversion
- 0.1.0
    - First working version

## License

**`masslos`** is distributed under the MIT license. See [`LICENSE`](LICENSE.md) for more details.
