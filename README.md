# postalcheck

Validate and normalize postal and ZIP codes by ISO country code against a bundled per-country table.

## Install

```
pip install postalcheck
```

## Usage

```python
from postalcheck import is_valid, normalize, supported_countries

is_valid("GB", "sw1a1aa")      # True
is_valid("DE", "1011")         # False

normalize("GB", "sw1a1aa")     # "SW1A 1AA"
normalize("BR", "01310100")    # "01310-100"
normalize("US", "123456789")   # "12345-6789"
normalize("NL", "1234ab")      # "1234 AB"

supported_countries()          # ("AR", "AT", "AU", ...)
```

Country codes are ISO 3166-1 alpha-2 and case-insensitive. Spaces and hyphens in
the input are ignored, so `"K1A 0B1"`, `"k1a0b1"` and `"K1A-0B1"` all validate and
normalize the same way. `normalize` uppercases the code and applies the canonical
separators for the country.

An unsupported country raises `UnknownCountryError`; `normalize` raises
`InvalidPostalCodeError` when the code does not match the country format. Both
subclass `ValueError`.

### Supported countries

AR, AT, AU, BE, BG, BR, CA, CH, CN, CZ, DE, DK, EE, ES, FI, FR, GB, GR, HR, HU,
ID, IE, IL, IN, IS, IT, JP, KR, LT, LU, LV, MX, MY, NL, NO, NZ, PH, PL, PT, RO,
RU, SE, SG, SI, SK, TH, TR, UA, US, VN, ZA.

## Why

Validating and normalizing postal codes without pulling in a heavy dependency has
no good pure-Python option. `pyap` and `libpostal` bindings target full street
addresses and need native libraries; `google-i18n-address` carries address
metadata and runtime dependencies. There is no maintained, typed, zero-dependency
package that does validation *and* canonical normalization from a bundled table.
`postalcheck` fills that gap: one table, two functions, no dependencies.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
