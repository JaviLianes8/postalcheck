"""Allow ``python -m postalcheck``."""

from __future__ import annotations

from ._cli import main

raise SystemExit(main())
