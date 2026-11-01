# postalcheck 1.0.0 certification report

Progress:
- [x] Read certification requirements; no previous release branch or certification entry.
- [x] API stability, typed errors, docstrings and contract expansion (items 1-6).
- [x] Live ground truth refreshed on 2026-11-01 (item 7).
- [x] Seeded Unicode and normalization properties (item 9).
- [x] README, guide, dated changelog and release metadata (items 11-13).
- [ ] Built-wheel consumers and upgrade from PyPI 0.2.1 (item 8).
- [ ] Every available supported interpreter (item 10).
- [ ] Archive inspection and final four gates (items 14-15).
- [ ] Deliberate mutation round (item 18).
- [ ] Independent reviewer (item 16).
- [ ] Five independent QA lenses (item 19).
- [ ] Pull request ready for merge and publication (item 17).

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
  Re-fetched bytes exactly match the 0.2.1 manifest. All source examples are checked;
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

## Independent stages

No independent QA lens or reviewer has run on this branch. Items 16 and 19 remain pending.
Merge and publication are outside this preparation stage.
