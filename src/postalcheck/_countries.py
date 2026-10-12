"""Country keys: the full rule table, countries without postal codes, and aliases."""

from __future__ import annotations

from ._rules import Rule
from ._table_a_lu import RULES_A_LU
from ._table_lv_z import RULES_LV_Z

RULES: dict[str, Rule] = {**RULES_A_LU, **RULES_LV_Z}

# Countries and territories that libaddressinput lists without a postal code format.
_WITHOUT = (
    "AE AG AO AQ AW BF BI BJ BO BQ BS BV BW BZ CD CF CG CI CK CM CW DJ DM ER FJ GA GD GH GM "
    "GQ GY HK JM KI KM KN KP LC LY ML MO MR MS MW NR NU PA PS QA RW SB SC SL SR SS ST SX SY "
    "TD TF TG TK TL TO TV UG VU WS YE ZW"
)
NO_POSTAL_CODES = frozenset(_WITHOUT.split())

# UK is exceptionally reserved in ISO 3166-1 for the United Kingdom, whose code is GB.
ALIASES = {"UK": "GB"}


def country_key(country: str) -> str:
    """The ISO key for ``country``; non-ASCII input gives a key that matches nothing."""
    key = country.strip()
    # str.upper() turns some non-ASCII letters into ASCII ones (dotless i, long s, sharp s).
    if not key.isascii():
        return ""
    key = key.upper()
    return ALIASES.get(key, key)
