# autotestify

🧪 Auto-generate pytest tests for your Python functions using the `@autotest` decorator.

## Install
```bash
pip install autotestify
```

##Usage
```bash
autotestify your_file.py
```

##Example
```
from autotestify import autotest

@autotest
def add(a, b):
    return a + b
```
