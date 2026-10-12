"""Exceptions raised by postalcheck; both are ``ValueError`` and keep their inputs."""

from __future__ import annotations


class UnknownCountryError(ValueError):
    """The country has no postal code rule.

    ``has_postal_codes`` is ``False`` for a real country or territory that does not use
    postal codes (such as ``"HK"``), and ``None`` when the code is not a known country.
    """

    def __init__(self, country: str, has_postal_codes: bool | None = None) -> None:
        if has_postal_codes is False:
            message = f"{country!r} does not use postal codes"
        else:
            message = f"{country!r} is not a supported country code"
        super().__init__(message)
        self.country = country
        self.has_postal_codes = has_postal_codes

    def __reduce__(self) -> tuple[type[UnknownCountryError], tuple[str, bool | None]]:
        return (type(self), (self.country, self.has_postal_codes))


class InvalidPostalCodeError(ValueError):
    """The code does not match its country's format. Keeps ``country`` and ``code``."""

    def __init__(self, country: str, code: str) -> None:
        super().__init__(f"{code!r} is not a valid {country} postal code")
        self.country = country
        self.code = code

    def __reduce__(self) -> tuple[type[InvalidPostalCodeError], tuple[str, str]]:
        return (type(self), (self.country, self.code))
