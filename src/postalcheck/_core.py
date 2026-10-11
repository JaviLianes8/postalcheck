"""Validate and normalize postal codes against the bundled per-country table."""

from __future__ import annotations

import re

from ._table import RULES, Rule

_SEPARATORS = re.compile(r"[\s\-]+")


class UnknownCountryError(ValueError):
    """Raised when the country code has no entry in the bundled table."""


class InvalidPostalCodeError(ValueError):
    """Raised when a code does not match its country's format."""


def _rule(country: str) -> Rule:
    key = country.strip().upper()
    try:
        return RULES[key]
    except KeyError:
        raise UnknownCountryError(f"{country!r} is not a supported country code") from None


def _compact(code: str) -> str:
    return _SEPARATORS.sub("", code).upper()


def is_valid(country: str, code: str) -> bool:
    """Return whether ``code`` is a valid postal code for ``country``.

    ``country`` is an ISO 3166-1 alpha-2 code and is case-insensitive. Spaces and
    hyphens in ``code`` are ignored. An unsupported country raises
    :class:`UnknownCountryError`.
    """
    return _rule(country).pattern.fullmatch(_compact(code)) is not None


def normalize(country: str, code: str) -> str:
    """Return ``code`` in its canonical form for ``country``.

    Uppercases the code and applies the country's canonical spacing (for example
    ``"sw1a1aa"`` to ``"SW1A 1AA"`` for GB, ``"01310100"`` to ``"01310-100"`` for BR).
    Raises :class:`UnknownCountryError` for an unsupported country and
    :class:`InvalidPostalCodeError` when the code does not match the country format.
    """
    rule = _rule(country)
    compact = _compact(code)
    if rule.pattern.fullmatch(compact) is None:
        raise InvalidPostalCodeError(
            f"{code!r} is not a valid {country.strip().upper()} postal code"
        )
    return rule.fmt(compact)


def supported_countries() -> tuple[str, ...]:
    """Return the ISO country codes with a rule in the bundled table, sorted."""
    return tuple(sorted(RULES))
