# postalcheck 1.0.0 certification report

Progress:
- [x] Read certification requirements; no previous release branch or certification entry.
- [x] API stability, typed errors, docstrings and contract expansion (items 1-6).
- [x] Live ground truth refreshed on 2026-11-01 (item 7).
- [x] Seeded Unicode and normalization properties (item 9).
- [x] README, guide, dated changelog and release metadata (items 11-13).
- [x] Built-wheel consumers and upgrade from PyPI 0.2.1 (item 8).
- [x] Every available supported interpreter (item 10).
- [x] Archive inspection and final four gates (items 14-15).
- [x] Deliberate mutation round (item 18).
- [x] QA round 1 fixes and regression contracts; independent re-review pending.
- [ ] Independent reviewer (item 16).
- [ ] Five independent QA lenses (item 19).
- [ ] Merge and publication (item 17).

## Baseline and API

Started at main `b98e3749412a554be75d3b1b0df5e8605721e450`, version 0.2.1.
The live PyPI JSON endpoint returned only release 0.2.1 on 2026-11-01.
Baseline gates passed: 532 tests passed, 918 skipped without external data or wheel e2e;
`mypy --strict src tests`, `ruff check .` and `ruff format --check .` exited 0.

The six exported names, positional/keyword signatures and defaults remain stable.
The 182 format patterns and canonical layouts are unchanged. `__version__` is 1.0.0.
Errors keep their attributes and `ValueError` inheritance; messages and CLI diagnostics
now omit input values. Public error module names stabilize new pickles. String subclasses
are read through their underlying string values. Every behavior change is in CHANGELOG.

## Ground truth

All sources below were fetched in this session on 2026-11-01. Raw external material stays
outside the repository. `tests/upstream/MANIFEST.json` records URL, date, revision, size,
SHA-256 and licensing; `scripts/fetch_upstream.py` re-fetches it. Data-dependent tests skip
if files are absent and verify their size and digest if present.

- Google Address Data Service: https://chromium-i18n.appspot.com/ssl-address/data and
  each country endpoint. 252 records, 182 formats, 70 without a format; 94,508 bytes,
  SHA-256 `f2417db82d928fe0b19c557ca97fd321f6498dfc775d6338e990f1b1981bc112`.
  Re-fetched bytes exactly match the 0.2.1 manifest. All 433 source examples are checked;
  three seeded 400-case comparisons per country check acceptance and canonical forms
  against the independent source regex. Ireland's stricter rule and Argentina's legacy
  four-digit form are explicit exceptions.
- https://en.wikipedia.org/w/index.php?oldid=1348214965&action=raw : 139 routing keys,
  12,010 bytes, hash matches the existing manifest; every key and initial letter checked.
- https://www.eircode.ie/faqs : confirms exclusion of O; it also recommends forgiving O
  as zero in integrations. This library intentionally rejects O and documents that choice.
- https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/sweEn.pdf :
  revision 11/2024, specifies Sweden's 3+2 spacing. Five short code examples copied from
  this fetched source are tested, with the URL and fetch date beside them.
- https://raw.githubusercontent.com/google/libaddressinput/master/README.md : verified
  the README comparison's C++ and Java implementations and broader address-input scope.

## QA round 1 (2026-11-01)

All five lenses reported FAIL on `ce67801aacf88dd1f9da9c3645d054a1e8e6575d`.
Fix commit: `88f4d43709f9fbcc72e5631cc52270e9b7c9e7c1`.
All 17 findings are addressed locally; independent re-review of each lens remains pending.
The public API, country formats and canonical layouts are unchanged.

| Findings | Changes and contract evidence |
| --- | --- |
| A-001, C-002, D1, E-CLI-STREAM | Flush each result inside output-error handling. Real pipes require two results before stdin EOF for both entry points, installed from wheel and sdist. |
| B-01, C-001 | Reject multi-character width folds. U+FFE3 returns False or InvalidPostalCodeError in all 182 countries; argv and stdin batches continue after rejection. |
| C-003 | Check actual types without invoking instance hooks. All country/code arguments reject hostile non-strings with safe TypeError messages; string subclasses still work. |
| A-002 | Correct the historical changelog: Irish routing-key initials and D6W are checked, not membership in the 139-key list. |
| A-003 | README and changelog apply the ASCII country restriction after Unicode whitespace trimming. |
| B-02 | Document runtime Unicode database coverage, including Kawi's version dependence; exercise that policy across supported Python versions. |
| D2 | Hash deterministic FAQ answer text, excluding dynamic HTML fields. Extraction tests accept session changes but reject changed or missing answers. |
| E-M09 | Exercise all 29 surrounding Unicode whitespace characters across all three country-taking functions, aliases and error metadata. |
| E-M21, E-M22 | Exercise every documented dash, width variant, tab and Unicode Zs character at every position in ten representative formats, including separator runs. |
| E-M30, E-M62 | Assert None, False and True metadata, original country, args and messages through construction, copy, deepcopy and pickle protocols 0-5. |
| E-M56 | Real CLI subprocesses reject malformed UTF-8 embedded inside an otherwise valid code, with no successful output or traceback. |

New contracts ran before production fixes: **203 failed, 408 passed** against the reviewed
code, including wheel/sdist streaming failures. After fixes, all **609 focused contracts**
passed. Each of the six reported survivors was injected separately and caught: M09, M21
and M22 by `test_unicode_contracts.py`, M30 and M62 by `test_error_contracts.py`, and M56
by `test_cli_contracts.py`. No behavior finding is disputed.

Two fresh complete source fetches passed; a further fetch after validation also passed.
The FAQ extraction is 29,785 bytes, SHA-256
`f0880a6395c4f67c9c714613fd7a7ef9e097178227f3bae5b8d6e56560198545`.
All seven runtime configurations listed below passed **2,100 tests, 4 skipped** each.
The skips are three opt-in build/upgrade cases and the intentional Ireland oracle case.
The full suite enabled fetched sources, wheel/sdist installs and the live 0.2.1 upgrade:
**2,103 passed, 1 skipped in 66.13 seconds**. Each required gate exited 0 independently:
`ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`.
`mypy --strict src tests` also passed. Each test had a 300-second timeout.
The 609 new contracts also passed from the extracted sdist against the installed wheel,
with the source package excluded from the extracted tree.
Evidence is retained outside the repository in certification scratch folders `fix-r1`
and `fix-r1-complete`: red/green contracts, six mutation logs, fetches, matrix and gates.
Items 16 and 19 require independent approval; merge and publication remain pending.

## Preparation packaging and upgrade (items 8, 10, 13, 14)

The build produced an sdist and a wheel built from that sdist. `twine check --strict`
passed both. Wheel inspection: 16 entries, only the package (including `py.typed`),
metadata, entry point, record and MIT license. Sdist inspection: 38 files with source,
tests, guide, README, changelog, license, metadata and fetch manifest/script. No fetched
third-party corpus, bytecode, scratch files, release report or progress files are shipped.
The README and manifest document the source of transcribed format facts and examples.

The external-consumer tests create throwaway venvs, install the wheel, run API calls from
an empty directory with isolated imports, and invoke the console script and module CLI.
They install actual PyPI 0.2.1, compare 18,746 seeded inputs across all 182 countries before
and after an in-place upgrade, verify documented message and string-subclass differences,
and check error pickles in both upgrade and downgrade directions. Both tests passed.

The sdist tests ran against the installed wheel with the source package excluded from the
extracted tree. Each configuration used a new venv, fetched external data and a 300-second
per-test timeout. All seven available runtime configurations passed:

| CPython | Result |
| --- | --- |
| 3.10.22 | 1,491 passed, 3 skipped |
| 3.11.18 | 1,491 passed, 3 skipped |
| 3.12.16 | 1,491 passed, 3 skipped |
| 3.13.18 | 1,491 passed, 3 skipped |
| 3.14.6 | 1,491 passed, 3 skipped |
| 3.14.10 | 1,491 passed, 3 skipped |
| 3.14.10 free-threaded | 1,491 passed, 3 skipped |

The skips are the two separately run build/upgrade tests and upstream acceptance for
Ireland, whose intentionally stricter format has separate tests. Interpreter discovery
checked the launcher, installation directories and installed standalone runtimes; stale
launcher entries pointed to deleted installations. No supported minor version was missing.

## Mutation round (item 18)

Runtime source: `40f250b`. Each mutation was injected alone into a scratch copy with
bytecode disabled, then restored before the next. The 1,111-test contract/property suite
passed before and after (one intentional Ireland upstream skip). All 24 mutations failed
with a behavioral assertion or expected-exception failure; none survived. No formatting,
typing or packaging failure was counted as a kill. Tests ran with `-x` and a 300-second
per-test limit. The table names the first failing test (parameter details
are omitted for readability).

| ID | Mutation | File | First failing test |
| --- | --- | --- | --- |
| M01 | invert validity | `_core.py` | `tests/test_validate.py::test_normalize_writes_the_canonical_layout` |
| M02 | ignore separator positions | `_core.py` | `tests/test_input.py::test_other_characters_are_refused` |
| M03 | wrong invalid-code exception type | `_core.py` | `tests/test_api.py::test_normalize_raises_with_the_inputs_attached` |
| M04 | replace source example | `_core.py` | `tests/test_api.py::test_a_country_without_postal_codes_says_so` |
| M05 | reverse supported-country order | `_core.py` | `tests/test_api.py::test_supported_countries_is_sorted_and_unique` |
| M06 | remove UK alias | `_countries.py` | `tests/test_api.py::test_example_returns_a_valid_canonical_code` |
| M07 | accept non-ASCII country folding | `_countries.py` | `tests/test_validate.py::test_non_ascii_country_codes_are_unknown` |
| M08 | lose known-country flag | `_core.py` | `tests/test_api.py::test_a_country_without_postal_codes_says_so` |
| M09 | stop native-digit folding | `_input.py` | `tests/test_input.py::test_input_is_folded_to_ascii` |
| M10 | stop width folding | `_input.py` | `tests/test_input.py::test_input_is_folded_to_ascii` |
| M11 | stop uppercase conversion | `_input.py` | `tests/test_validate.py::test_normalize_writes_the_canonical_layout` |
| M12 | accept trailing dashes | `_input.py` | `tests/test_input.py::test_other_characters_are_refused` |
| M13 | shift separator position | `_input.py` | `tests/test_api.py::test_example_returns_a_valid_canonical_code` |
| M14 | accept trailing unmatched text | `_rules.py` | `tests/test_validate.py::test_impossible_codes_are_refused` |
| M15 | drop ZIP+4 separator | `_rules.py` | `tests/test_api.py::test_example_returns_a_valid_canonical_code` |
| M16 | drop mandatory Latvia prefix | `_rules.py` | `tests/test_api.py::test_example_returns_a_valid_canonical_code` |
| M17 | retain optional prefix | `_rules.py` | `tests/test_input.py::test_separators_are_optional_and_interchangeable` |
| M18 | accept Netherlands leading zero | `_table_lv_z.py` | `tests/test_validate.py::test_impossible_codes_are_refused` |
| M19 | accept O in Eircode | `_table_a_lu.py` | `tests/test_eircode.py::test_the_letter_o_is_never_used` |
| M20 | swap invalid-code attribute | `_errors.py` | `tests/test_api.py::test_normalize_raises_with_the_inputs_attached` |
| M21 | leak input in error message | `_errors.py` | `tests/test_api.py::test_normalize_raises_with_the_inputs_attached` |
| M22 | return success after invalid CLI code | `_cli.py` | `tests/test_cli.py::test_invalid_codes_go_to_stderr_and_set_status_one` |
| M23 | wrong CLI unknown-country status | `_cli.py` | `tests/test_cli.py::test_an_unknown_country_is_a_usage_error_even_without_codes` |
| M24 | echo argparse input | `_cli.py` | `tests/test_cli.py::test_usage_errors_and_help_go_to_the_given_streams` |

## Robustness (item 9)

The source-regex oracle runs 218,000 seeded cases (400 per country and direction, with
Ireland excluded only from upstream-to-library permissiveness). Additional generators
run 15,000 hostile Unicode strings on three seeds and 7,280 alternate spellings of source
examples on two seeds. Six million-character malformed shapes have bounded diagnostics;
300,000 separator characters in a valid ZIP+4 code preserve the layout.

Five timed shapes were measured at 50,000, 200,000 and 800,000 characters (median of five
runs). The largest size took at most 1.27 seconds; growth was consistent with a single
scan. These are session measurements, not a promised throughput threshold.

| Shape | 50k seconds | 200k seconds | 800k seconds |
| --- | --- | --- | --- |
| digits | 0.035277 | 0.200132 | 0.528505 |
| spaces | 0.020796 | 0.099318 | 0.416739 |
| dashes | 0.008318 | 0.059908 | 0.220282 |
| unicode | 0.097752 | 0.335177 | 1.267446 |
| countries | 0.000083 | 0.000328 | 0.001111 |

## Preparation gates (item 15)

On 2026-11-01, each command exited 0 independently: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest`.
The final suite enabled fetched sources, built-wheel e2e and the live PyPI upgrade:
**1,493 passed, 1 skipped in 57.92 seconds**. The only skip is the intentional Ireland
upstream-permissiveness comparison. All public doctests, README and GUIDE Python blocks,
CLI transcript and strict consumer typing checks passed. Source/test files remain under
200 lines. These preparation results predate QA round 1; updated evidence appears above.
