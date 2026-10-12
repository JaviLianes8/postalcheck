"""Validate and normalize postal and ZIP codes by ISO country code."""

from __future__ import annotations

from ._core import example, is_valid, normalize, supported_countries
from ._errors import InvalidPostalCodeError, UnknownCountryError

__version__ = "0.2.0"

__all__ = [
    "InvalidPostalCodeError",
    "UnknownCountryError",
    "example",
    "is_valid",
    "normalize",
    "supported_countries",
]
