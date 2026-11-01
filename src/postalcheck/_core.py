"""Validate and normalize postal codes against the bundled per-country rules."""

from __future__ import annotations

from ._countries import NO_POSTAL_CODES, RULES, country_key
from ._errors import InvalidPostalCodeError, UnknownCountryError
from ._input import split
from ._rules import Rule


def _rule(country: str) -> tuple[str, Rule]:
    if not isinstance(country, str):
        raise TypeError("country must be a str")
    key = country_key(country)
    rule = RULES.get(key)
    if rule is None:
        raise UnknownCountryError(country, False if key in NO_POSTAL_CODES else None)
    return key, rule


def _canonical(rule: Rule, code: str) -> str | None:
    if not isinstance(code, str):
        raise TypeError("code must be a str")
    parts = split(code)
    if parts is None:
        return None
    compact, cuts = parts
    if not rule.matches(compact):
        return None
    canonical = rule.layout(compact)
    if not set(cuts) <= rule.allowed_cuts(compact, canonical):
        return None
    return canonical


def is_valid(country: str, code: str) -> bool:
    """Return whether ``code`` matches the postal code format for ``country``.

    ``country`` is an ISO 3166-1 alpha-2 code, case-insensitive (``"UK"`` reads as
    ``"GB"``). Case, full-width forms and native digits in ``code`` are folded; spaces and
    dashes are optional but allowed only where the country writes a separator. Raises
    :class:`UnknownCountryError` for a country without a rule.
    Non-string arguments raise :class:`TypeError`. Assignment is not checked.

    >>> from postalcheck import is_valid
    >>> is_valid("GB", "sw1a1aa")
    True
    >>> is_valid("US", "9-0-2-1-0")
    False
    """
    _, rule = _rule(country)
    return _canonical(rule, code) is not None


def normalize(country: str, code: str) -> str:
    """Return ``code`` in the canonical layout for ``country``.

    For example ``"sw1a1aa"`` becomes ``"SW1A 1AA"`` for GB and ``"01310100"`` becomes
    ``"01310-100"`` for BR. Raises :class:`UnknownCountryError` for a country without a
    rule and :class:`InvalidPostalCodeError` when ``is_valid`` would return ``False``.
    Non-string arguments raise :class:`TypeError`.

    >>> from postalcheck import normalize
    >>> normalize("GB", "sw1a1aa")
    'SW1A 1AA'
    """
    key, rule = _rule(country)
    canonical = _canonical(rule, code)
    if canonical is None:
        raise InvalidPostalCodeError(key, code)
    return canonical


def example(country: str) -> str:
    """Return a source example in canonical layout, suitable for a placeholder.

    Raises :class:`UnknownCountryError` without a rule, :class:`TypeError` for non-text.
    The example is not a current assignment or deliverability guarantee.

    >>> from postalcheck import example
    >>> example("US")
    '95014'
    """
    return _rule(country)[1].example


def supported_countries() -> tuple[str, ...]:
    """Return the sorted country/territory keys with a rule, excluding aliases.

    Keys follow libaddressinput, including exceptional keys such as AC and XK.

    >>> from postalcheck import supported_countries
    >>> supported_countries()[:3]
    ('AC', 'AD', 'AF')
    """
    return tuple(sorted(RULES))
