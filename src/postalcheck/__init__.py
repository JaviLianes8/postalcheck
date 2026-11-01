"""Validate and normalize postal code formats by country key.

>>> import postalcheck
>>> postalcheck.__version__
'1.0.0'
"""

from __future__ import annotations

from ._core import example, is_valid, normalize, supported_countries
from ._errors import InvalidPostalCodeError, UnknownCountryError

del annotations

__version__ = "1.0.0"

__all__ = [
    "InvalidPostalCodeError",
    "UnknownCountryError",
    "example",
    "is_valid",
    "normalize",
    "supported_countries",
]
