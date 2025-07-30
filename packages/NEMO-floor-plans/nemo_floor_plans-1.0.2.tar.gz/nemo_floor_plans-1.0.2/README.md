[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/NEMO-floor-plans?label=python)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/nemo-floor-plans?label=pypi%20version)](https://pypi.org/project/NEMO-floor-plans/)

# NEMO Floor plans

This plugin for NEMO adds the ability to create floor plans and assign locations for sensors.

# Compatibility:

NEMO/NEMO-CE >= 7.0.0 & NEMO-Sensors >= 0.9.2 ----> NEMO-floor-plans >= 1.0.0

NEMO >= 4.7.0 / NEMO-CE >= 1.7.0 ----> NEMO-floor-plans >= 0.1.0

# Installation

`pip install NEMO-floor-plans`

# Add NEMO Floor Plans

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_floor_plans',
    '...'
]
```

