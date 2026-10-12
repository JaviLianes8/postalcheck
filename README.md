# postalcheck

Validate and normalize postal and ZIP codes for the 182 countries and territories that use
them. Every rule is checked against the address data that Chrome and Android use for their
address forms (Google libaddressinput). Zero dependencies, fully typed.

## Install

```
pip install postalcheck
```

## Usage

```python
from postalcheck import is_valid, normalize

print(is_valid("GB", "sw1a1aa"))  # True
print(is_valid("GB", "QQ1 1AA"))  # False
print(is_valid("DE", "1011"))  # False
print(normalize("GB", "sw1a1aa"))  # SW1A 1AA
print(normalize("BR", "01310100"))  # 01310-100
print(normalize("US", "123456789"))  # 12345-6789
print(normalize("NL", "1234ab"))  # 1234 AB
print(normalize("LV", "1073"))  # LV-1073
print(normalize("UK", "m1 1aa"))  # M1 1AA
```

`normalize` returns the code in the layout the national postal operator prints, and raises
`InvalidPostalCodeError` when `is_valid` would return `False`.

### What the input may look like

Case does not matter. Full-width forms (what Japanese and Chinese keyboards type), decimal
digits of any script, Unicode dashes and non-breaking spaces are folded to plain ASCII.
Spaces and dashes are optional and interchangeable, but only where the country writes a
separator, so a typo does not slip through:

```python
from postalcheck import is_valid, normalize

print(normalize("JP", "\uff11\uff15\uff14\uff0d\uff10\uff10\uff12\uff13"))  # 154-0023
print(normalize("DE", "\u0661\u0660\u0661\u0661\u0665"))  # 10115
print(normalize("PL", "00\u2013950"))  # 00-950
print(normalize("GB", "SW1A-1AA"))  # SW1A 1AA
print(is_valid("US", "9-0-2-1-0"))  # False
print(is_valid("GB", "SW 1A1AA"))  # False
print(is_valid("DE", "10115."))  # False
```

### Countries, examples and errors

```python
from postalcheck import UnknownCountryError, example, normalize, supported_countries

print(len(supported_countries()))  # 182
print(example("IE"))  # A65 F4E2
print(example("se"))  # 114 55
try:
    normalize("HK", "999077")
except UnknownCountryError as error:
    print(error.has_postal_codes)  # False
try:
    normalize("ZZ", "12345")
except UnknownCountryError as error:
    print(error)  # 'ZZ' is not a supported country code
```

`example` returns a real code in canonical layout, handy as a form placeholder.
`UnknownCountryError.has_postal_codes` is `False` for the 70 countries and territories that
do not use postal codes (Hong Kong, Qatar, Panama, ...), so a form can hide the field, and
`None` for a code that is not a country. Both errors subclass `ValueError`, keep their
inputs as attributes (`country`, `code`) and survive pickling.

### Command line

```
$ postalcheck gb "sw1a1aa" "m1 1aa" "QQ1 1AA"
SW1A 1AA
M1 1AA
invalid: QQ1 1AA
```

With no code after the country, codes are read from standard input, one per line. The exit
status is 1 when any code is invalid and 2 for an unknown country. `python -m postalcheck`
does the same.

## API

| Name | Promise |
| --- | --- |
| `is_valid(country, code)` | `True` when `code` is a valid postal code of `country` |
| `normalize(country, code)` | The canonical layout, or `InvalidPostalCodeError` |
| `example(country)` | A real code of `country` in canonical layout |
| `supported_countries()` | The 182 ISO codes with a rule, sorted |
| `UnknownCountryError` | No rule for the country; `has_postal_codes` says why |
| `InvalidPostalCodeError` | The code does not match; keeps `country` and `code` |

All functions raise `UnknownCountryError` for a country without a rule and `TypeError` for
an argument that is not a `str`. Country codes are ISO 3166-1 alpha-2, case-insensitive;
`UK` is read as `GB`.

## Where the rules come from

Each rule transcribes the `zip` pattern of the country in Google libaddressinput
(https://chromium-i18n.appspot.com/ssl-address/data), fetched on 2026-10-12. The test suite
carries that data unchanged and proves, for every country, that each published example
validates and keeps its layout, that every string the upstream pattern accepts is accepted
here, and that every canonical form produced here is accepted upstream.

Four deliberate differences:

- **Ireland** is stricter. The routing key starts with one of the letters used by the 139
  published routing keys (or is `D6W`), and the letter O never appears, as the Eircode FAQ
  states (https://www.eircode.ie/faqs).
- **Argentina** also accepts the four-digit code that the eight-character CPA extends.
- **Latvia** accepts the bare digits and normalizes them to the `LV-` form.
- **Sweden** normalizes to `114 55`, the PostNord layout, where libaddressinput lists
  `11455`.

This checks the format, not whether a code is assigned: that needs the national address
files, which are large, licensed and change every month.

### Countries

| Country | Example | Country | Example | Country | Example |
| --- | --- | --- | --- | --- | --- |
| AC | `ASCN 1ZZ` | AD | `AD100` | AF | `1001` |
| AI | `2640` | AL | `1001` | AM | `375010` |
| AR | `C1070AAM` | AS | `96799` | AT | `1010` |
| AU | `2060` | AX | `22150` | AZ | `1000` |
| BA | `71000` | BB | `BB23026` | BD | `1340` |
| BE | `4000` | BG | `1000` | BH | `317` |
| BL | `97100` | BM | `FL 07` | BN | `BT2328` |
| BR | `40301-110` | BT | `11001` | BY | `223016` |
| CA | `H3Z 2Y7` | CC | `6799` | CH | `2544` |
| CL | `8340457` | CN | `266033` | CO | `111221` |
| CR | `1000` | CU | `10700` | CV | `7600` |
| CX | `6798` | CY | `2008` | CZ | `100 00` |
| DE | `26133` | DK | `8660` | DO | `11903` |
| DZ | `40304` | EC | `090105` | EE | `69501` |
| EG | `4460232` | EH | `70000` | ES | `28039` |
| ET | `1000` | FI | `00550` | FK | `FIQQ 1ZZ` |
| FM | `96941` | FO | `100` | FR | `33380` |
| GB | `EC1Y 8SY` | GE | `0101` | GF | `97300` |
| GG | `GY1 1AA` | GI | `GX11 1AA` | GL | `3900` |
| GN | `001` | GP | `97100` | GR | `151 24` |
| GS | `SIQQ 1ZZ` | GT | `09001` | GU | `96910` |
| GW | `1000` | HM | `7050` | HN | `31301` |
| HR | `10000` | HT | `6120` | HU | `1037` |
| ID | `40115` | IE | `A65 F4E2` | IL | `9614303` |
| IM | `IM2 1AA` | IN | `110034` | IO | `BBND 1ZZ` |
| IQ | `31001` | IR | `11936-12345` | IS | `320` |
| IT | `00144` | JE | `JE1 1AA` | JO | `11937` |
| JP | `154-0023` | KE | `20100` | KG | `720001` |
| KH | `120101` | KR | `03051` | KW | `54541` |
| KY | `KY1-1100` | KZ | `040900` | LA | `01160` |
| LB | `2038 3054` | LI | `9496` | LK | `20000` |
| LR | `1000` | LS | `100` | LT | `04340` |
| LU | `4750` | LV | `LV-1073` | MA | `53000` |
| MC | `98000` | MD | `2012` | ME | `81257` |
| MF | `97100` | MG | `501` | MH | `96960` |
| MK | `1314` | MM | `11181` | MN | `65030` |
| MP | `96950` | MQ | `97220` | MT | `NXR 01` |
| MU | `42602` | MV | `20026` | MX | `02860` |
| MY | `43000` | MZ | `1102` | NA | `10001` |
| NC | `98814` | NE | `8001` | NF | `2899` |
| NG | `930283` | NI | `52000` | NL | `1234 AB` |
| NO | `0025` | NP | `44601` | NZ | `6001` |
| OM | `133` | PE | `LIMA 23` | PF | `98709` |
| PG | `111` | PH | `1008` | PK | `44000` |
| PL | `00-950` | PM | `97500` | PN | `PCRN 1ZZ` |
| PR | `00930` | PT | `2725-079` | PW | `96940` |
| PY | `001001` | RE | `97400` | RO | `060274` |
| RS | `106314` | RU | `247112` | SA | `11564` |
| SD | `11042` | SE | `114 55` | SG | `546080` |
| SH | `STHL 1ZZ` | SI | `4000` | SJ | `9170` |
| SK | `010 01` | SM | `47890` | SN | `12500` |
| SO | `JH 09010` | SV | `1101` | SZ | `H100` |
| TA | `TDCU 1ZZ` | TC | `TKCA 1ZZ` | TH | `10150` |
| TJ | `735450` | TM | `744000` | TN | `1002` |
| TR | `01960` | TT | `500234` | TW | `104` |
| TZ | `6090` | UA | `15432` | UM | `96898` |
| US | `95014` | UY | `11600` | UZ | `702100` |
| VA | `00120` | VC | `VC0100` | VE | `1010` |
| VG | `VG1110` | VI | `00802-1222` | VN | `70010` |
| WF | `98600` | XK | `10000` | YT | `97600` |
| ZA | `0083` | ZM | `50100` |  |  |

## Why

Most validators carry a short list of countries written from memory. They accept codes
that cannot exist and refuse real ones (the 0.1.0 table of this package refused every
Latvian and new Vietnamese code). Address libraries that get it right pull in native
libraries or runtime dependencies. `postalcheck` is one small typed package with every
country that uses postal codes, proven against the data that browsers use.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
