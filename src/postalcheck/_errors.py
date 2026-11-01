"""Exceptions raised by postalcheck; both are ``ValueError`` and keep their inputs."""

from __future__ import annotations


class UnknownCountryError(ValueError):
    """The country has no postal code rule.

    ``has_postal_codes`` is ``False`` for a real country or territory that does not use
    postal codes (such as ``"HK"``), and ``None`` when the code is not a known country.
    ``country`` retains the original input; messages never include input values.

    >>> from postalcheck import UnknownCountryError
    >>> error = UnknownCountryError("HK", False)
    >>> error.country, error.has_postal_codes
    ('HK', False)
    """

    __module__ = "postalcheck"

    def __init__(self, country: str, has_postal_codes: bool | None = None) -> None:
        if has_postal_codes is False:
            message = "country does not use postal codes"
        else:
            message = "unsupported country code"
        super().__init__(message)
        self.country = country
        self.has_postal_codes = has_postal_codes

    def __reduce__(self) -> tuple[type[UnknownCountryError], tuple[str, bool | None]]:
        return (type(self), (self.country, self.has_postal_codes))


class InvalidPostalCodeError(ValueError):
    """The code does not match its country's format. Keeps ``country`` and ``code``.

    Messages never include input values. Both attributes survive pickling.

    >>> from postalcheck import InvalidPostalCodeError
    >>> error = InvalidPostalCodeError("US", "bad")
    >>> error.country, error.code
    ('US', 'bad')
    """

    __module__ = "postalcheck"

    def __init__(self, country: str, code: str) -> None:
        super().__init__("invalid postal code format")
        self.country = country
        self.code = code

    def __reduce__(self) -> tuple[type[InvalidPostalCodeError], tuple[str, str]]:
        return (type(self), (self.country, self.code))
