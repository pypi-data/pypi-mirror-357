# 🧪 autotestify

`autotestify` is a lightweight Python CLI tool that **automatically generates pytest test functions** for any function decorated with `@autotest`.

Save time. Avoid boilerplate. Focus on your logic — we'll write the tests.

---

## 🚀 Features

- 🔍 Detects only functions decorated with `@autotest`
- 🧠 Adds sensible dummy values for parameters
- 🛠 Generates test stubs using `pytest`
- ⚡ Instantly creates a `test_<filename>.py` file
- 🐍 Pure Python, no dependencies

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/autotestify/):

```bash
pip install autotestify
```
## ⚙️ Usage
```bash
autotestify your_file.py
```
This will generate a new file named test_your_file.py in the same directory.

## ✅ Example
Original file: calculator.py
```
from autotestify import autotest


def add(a, b):
    return a + b

@autotest
def greet(name):
    return f"Hello, {name}"
```

## Generated: test_calculator.py
```
import pytest
from calculator import *

def test_greet():
    result = greet("example")
    assert result is not None
```

## 📌 @autotest Decorator
This is a no-op decorator used for marking which functions should be tested automatically.
```
from autotestify import autotest

@autotest
def my_function(...):
    ...
```
Functions without @autotest will be ignored.

## 🧩 How It Works
Parses your Python file using the ast module

Identifies functions with @autotest

Analyzes their arguments and generates dummy values

Writes pytest test functions with assert result is not None

## 🛠 Requirements
Python 3.7+

pytest (to run the tests, not required to generate)

## 📄 License
MIT © 2025 Sardor Safarov