"""Validate and normalize postal and ZIP codes by ISO country code."""

from __future__ import annotations

from ._core import (
    InvalidPostalCodeError,
    UnknownCountryError,
    is_valid,
    normalize,
    supported_countries,
)

__version__ = "0.1.0"

__all__ = [
    "InvalidPostalCodeError",
    "UnknownCountryError",
    "is_valid",
    "normalize",
    "supported_countries",
]
