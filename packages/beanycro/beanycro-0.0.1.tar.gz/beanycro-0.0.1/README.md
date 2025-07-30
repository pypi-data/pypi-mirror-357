# Benny Bean Utils Package

## Description
This package targets to offer basic utilities for my personal projects.

## Installation

### To build the package : 
```bash
py -m pip install --upgrade build
py -m build
```

### To upload the package to PyPI:
```bash
py -m pip install --upgrade twine
py -m twine upload dist/*
```

## Utilities
### Test
This is a simple utility to test if the package works

```python
from benny_bean_utils.test import ping

ping()  # Output: Pong!
```