"""Random strings drawn from the upstream patterns and from ours must agree both ways."""

from __future__ import annotations

import itertools
import random
import re

import pytest
from upstream import sample, upstream_pattern

from postalcheck import is_valid, normalize, supported_countries
from postalcheck._countries import RULES

ROUNDS = 400
# Ireland is stricter than libaddressinput (routing key letters, no letter O).
STRICTER = {"IE"}
# Argentina also accepts the four-digit code that the CPA extends.
LOOSER = {"AR"}
MUTATION_ALPHABET = "0123456789AZOIW -"


def _mutate(code: str, rng: random.Random) -> str:
    at = rng.randrange(len(code) + 1)
    char = rng.choice(MUTATION_ALPHABET)
    kind = rng.randrange(3)
    if kind == 0:
        return code[:at] + char + code[at:]
    if kind == 1:
        return code[:at] + char + code[at + 1 :]
    return code[:at] + code[at + 1 :]


@pytest.mark.parametrize("country", supported_countries())
def test_whatever_upstream_accepts_is_accepted(country: str) -> None:
    rng = random.Random(country)
    upstream = upstream_pattern(country).pattern
    if country in STRICTER:
        pytest.skip("stricter on purpose, see test_eircode.py")
    for _ in range(ROUNDS):
        code = sample(upstream, rng)
        assert is_valid(country, code), (country, code)
        assert is_valid(country, code.lower()), (country, code)


@pytest.mark.parametrize("country", supported_countries())
def test_every_normal_form_is_accepted_upstream(country: str) -> None:
    rng = random.Random(country)
    upstream = upstream_pattern(country)
    for _ in range(ROUNDS):
        compact = sample(RULES[country].pattern.pattern, rng)
        normal = normalize(country, compact)
        assert normalize(country, normal) == normal, (country, compact)
        if country in LOOSER and upstream.fullmatch(normal) is None:
            assert compact.isdigit() and len(compact) == 4
            continue
        assert upstream.fullmatch(normal), (country, compact, normal)


def _spellings(code: str) -> set[str]:
    """Every way to write ``code`` with each run of separators as one space or one dash."""
    parts = re.split(r"[ -]+", code.strip().upper())
    return {
        "".join(p + s for p, s in zip(parts, (*seps, ""), strict=True))
        for seps in itertools.product(" -", repeat=len(parts) - 1)
    }


@pytest.mark.parametrize("country", supported_countries())
def test_near_misses_agree_with_upstream(country: str) -> None:
    rng = random.Random(country)
    upstream = upstream_pattern(country)
    for _ in range(ROUNDS):
        code = _mutate(sample(upstream.pattern, rng), rng)
        if is_valid(country, code):
            normal = normalize(country, code)
            legacy = country in LOOSER and normal.isdigit() and len(normal) == 4
            assert legacy or upstream.fullmatch(normal), (country, code)
            # Separators may be left out, but those given sit where upstream writes one.
            if re.search(r"[ -]", code.strip()):
                spelled = any(upstream.fullmatch(s) for s in _spellings(code))
                assert legacy or spelled, (country, code)
        if upstream.fullmatch(code) and country not in STRICTER:
            assert is_valid(country, code), (country, code)
