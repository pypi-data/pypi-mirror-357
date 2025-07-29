<a name="readme-top"></a>

# ⚒️ Object Mother Pattern

<p align="center">
    <a href="https://github.com/adriamontoto/object-mother-pattern/actions/workflows/ci.yaml?event=push&branch=master" target="_blank">
        <img src="https://github.com/adriamontoto/object-mother-pattern/actions/workflows/ci.yaml/badge.svg?event=push&branch=master" alt="CI Pipeline">
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/adriamontoto/object-mother-pattern" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/adriamontoto/object-mother-pattern.svg" alt="Coverage Pipeline">
    </a>
    <a href="https://pypi.org/project/object-mother-pattern" target="_blank">
        <img src="https://img.shields.io/pypi/v/object-mother-pattern?color=%2334D058&label=pypi%20package" alt="Package Version">
    </a>
    <a href="https://pypi.org/project/object-mother-pattern/" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/object-mother-pattern.svg?color=%2334D058" alt="Supported Python Versions">
    </a>
</p>

The **Object Mother Pattern** is a Python 🐍 package that simplifies and standardizes the creation of test 🧪 objects. This pattern is especially helpful in testing scenarios where you need to generate multiple instances of complex objects quickly and consistently. By providing a set of prebuilt 🛠️ object mothers, you can drop these into your existing test suite and skip the boilerplate setup yourself.

Easy to install and integrate, the **Object Mother Pattern** is a must-have for any Python developer looking to simplify their testing workflow, ensure design uniformity, and leverage the full potential of reusable test objects in their projects 🚀.
<br><br>

## Table of Contents

- [📥 Installation](#installation)
- [💻 Utilization](#utilization)
  - [🎄 Real-Life Case: Christmas Detector Service](#real-life-case-christmas-detector-service)
- [🤝 Contributing](#contributing)
- [🔑 License](#license)

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="installation"></a>

## 📥 Installation

You can install **Object Mother Pattern** using `pip`:

```bash
pip install object-mother-pattern
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="utilization"></a>

## 💻 Utilization

Here is how you can utilize the **Object Mother** library to generate various types of test data:

```python
from object_mother_pattern.mothers import (
    IntegerMother,
    FloatMother,
    BooleanMother,
    StringMother,
    UuidMother,
    StringDateMother,
)

# Generate a random integer between -4 and 15
number = IntegerMother.create(min=-4, max=15)
print(number)
# >>> 8

# Generate a random float between -4 and 15 with 5 Decimal Places
number = FloatMother.create(min=-4, max=15, decimals=5)
print(number)
# >>> 0.83396

# Generate a random boolean
boolean = BooleanMother.create()
print(boolean)
# >>> True

# Generate a random string
string = StringMother.create()
print(string)
# >>> 'zFUmlsODZqzwyGjrOOqBtYzNwlJdOETalkXbuSegoQpgEnYQTCDeoifWrTQXMm'

# Generate a random string of specific length
string = StringMother.of_length(length=10)
print(string)
# >>> 'TfkrYRxUFT'

# Generate a random UUID
uuid = UuidMother.create()
print(uuid)
# >>> '3e9e0f3a-64a3-474f-9127-368e723f389f'

# Generate a random date
date = StringDateMother.create()
print(date)
# >>> '2015-09-15'
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p>

<a name="real-life-case-christmas-detector-service"></a>

### 🎄 Real-Life Case: Christmas Detector Service

Below is an example of a real-life scenario where **Object Mother Pattern** can help simplify test date creation. We have a `ChristmasDetectorService` that checks if a given date falls within a specific Christmas holiday range. Using the [`DateMother`](https://github.com/adriamontoto/object-mother-pattern/blob/master/object_mother_pattern/mothers/dates/date/date_mother.py) class, we can easily generate dates both within and outside of this range for our tests, this ensuring that every possible scenario is covered.

```python
from datetime import date
from object_mother_pattern.mothers import DateMother


class ChristmasDetectorService:
    def __init__(self) -> None:
        self.christmas_start = date(year=2024, month=12, day=24)
        self.christmas_end = date(year=2025, month=1, day=6)

    def is_christmas(self, today: date) -> bool:
        return self.christmas_start <= today <= self.christmas_end


christmas_detector_service = ChristmasDetectorService()


def test_christmas_detector_is_christmas() -> None:
    date_mother = DateMother.create(
        start_date=date(year=2024, month=12, day=25),
        end_date=date(year=2025, month=1, day=6),
    )

    assert christmas_detector_service.is_christmas(today=date_mother)


def test_christmas_detector_is_not_christmas() -> None:
    date_mother = DateMother.out_of_range(
        start_date=date(year=2024, month=12, day=24),
        end_date=date(year=2025, month=1, day=6),
    )

    assert not christmas_detector_service.is_christmas(today=date_mother)
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="contributing"></a>

## 🤝 Contributing

We love community help! Before you open an issue or pull request, please read:

- [`🤝 How to Contribute`](https://github.com/adriamontoto/object-mother-pattern/blob/master/.github/CONTRIBUTING.md)
- [`🧭 Code of Conduct`](https://github.com/adriamontoto/object-mother-pattern/blob/master/.github/CODE_OF_CONDUCT.md)
- [`🔐 Security Policy`](https://github.com/adriamontoto/object-mother-pattern/blob/master/.github/SECURITY.md)

_Thank you for helping make **⚒️ Object Mother Pattern** package awesome! 🌟_

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="license"></a>

## 🔑 License

This project is licensed under the terms of the [`MIT license`](https://github.com/adriamontoto/object-mother-pattern/blob/master/LICENSE.md).

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p>
