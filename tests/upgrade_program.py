"""External-consumer programs used before and after installing the built wheel."""

from __future__ import annotations

SNAPSHOT = r"""
import hashlib, json, pickle, random
from pathlib import Path
import postalcheck as p

assert "site-packages" in p.__file__, p.__file__
rng = random.Random(20261101)
results = []
for country in p.supported_countries():
    sample = p.example(country)
    codes = [sample, sample.lower(), sample.replace(" ", "").replace("-", "")]
    codes += ["".join(rng.choices("01AZaz -\t\u0661\uff11", k=rng.randrange(15)))
              for _ in range(100)]
    for code in codes:
        valid = p.is_valid(country, code)
        try:
            result = p.normalize(country, code)
        except p.InvalidPostalCodeError as error:
            result = [type(error).__name__, error.country, error.code]
        results.append([country, code, valid, result])
print(hashlib.sha256(json.dumps(results, ensure_ascii=True).encode()).hexdigest())
errors = [p.UnknownCountryError("HK", False), p.InvalidPostalCodeError("US", "bad")]
Path("errors-" + p.__version__ + ".pickle").write_bytes(pickle.dumps(errors))
"""

CHECK_OLD_PICKLES = r"""
import pickle
from pathlib import Path
import postalcheck as p
errors = pickle.loads(Path("errors-0.2.1.pickle").read_bytes())
assert isinstance(errors[0], p.UnknownCountryError)
assert (errors[0].country, errors[0].has_postal_codes) == ("HK", False)
assert isinstance(errors[1], p.InvalidPostalCodeError)
assert (errors[1].country, errors[1].code) == ("US", "bad")
assert str(errors[0]) == "country does not use postal codes"
assert str(errors[1]) == "invalid postal code format"
"""

CHECK_NEW_PICKLES = r"""
import pickle
from pathlib import Path
import postalcheck as p
errors = pickle.loads(Path("errors-1.0.0.pickle").read_bytes())
assert isinstance(errors[0], p.UnknownCountryError)
assert (errors[0].country, errors[0].has_postal_codes) == ("HK", False)
assert isinstance(errors[1], p.InvalidPostalCodeError)
assert (errors[1].country, errors[1].code) == ("US", "bad")
"""

DIFFERENCES = r"""
import postalcheck as p
class Misleading(str):
    def strip(self, chars=None):
        return "12345"
if p.__version__ == "0.2.1":
    assert str(p.InvalidPostalCodeError("US", "bad")) == "'bad' is not a valid US postal code"
    assert str(p.UnknownCountryError("ZZ")) == "'ZZ' is not a supported country code"
    assert p.InvalidPostalCodeError.__module__ == "postalcheck._errors"
    assert p.normalize("US", Misleading("95014")) == "12345"
else:
    assert p.__version__ == "1.0.0"
    assert str(p.InvalidPostalCodeError("US", "bad")) == "invalid postal code format"
    assert str(p.UnknownCountryError("ZZ")) == "unsupported country code"
    assert p.InvalidPostalCodeError.__module__ == "postalcheck"
    assert p.normalize("US", Misleading("95014")) == "95014"
try:
    p.normalize("US", 1)
except TypeError as error:
    expected = "code must be a str" + (", not int" if p.__version__ == "0.2.1" else "")
    assert str(error) == expected
else:
    raise AssertionError("non-string accepted")
"""
