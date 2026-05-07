#!/usr/bin/env python3
"""
Wrap a compiled foundation CSS file in @layer foundation and append P3.

Usage:
    python3 wrap_foundation_layer.py <raw_css_in> <foundation_css_out>

This is the second step of the foundation.css refresh pipeline.  Run after:
    npx sass --style=expanded --no-source-map \\
        plugins/acss-kit/assets/foundation/sass/_index.scss:<raw_css_in>

Exit codes:
    0 = success
    1 = usage / IO error
"""
from __future__ import annotations

import sys
from pathlib import Path

HEADER = """\
/* foundation.css
 * Compiled from @fpkit/acss@6.5.0 (SHA 9063512fa822963d8151c972bed9f5b0e531df0f)
 * with project patches P1-P4 -- see assets/foundation/SOURCE.md for details.
 *
 * DO NOT EDIT DIRECTLY. To refresh:
 *   npx sass --style=expanded --no-source-map \\\\
 *     plugins/acss-kit/assets/foundation/sass/_index.scss:_foundation_raw.css
 *   python3 plugins/acss-kit/scripts/wrap_foundation_layer.py \\\\
 *     _foundation_raw.css plugins/acss-kit/assets/foundation/foundation.css
 */
@layer foundation, components, utilities, theme;

"""

P3 = """
/* P3: Collapse transition tokens for prefers-reduced-motion.
   Zeroes the named transition custom properties so components that
   reference --transition or --tran-all also honour the user preference. */
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition: none;
    --tran-all: none;
  }
}
"""


def wrap(raw: str) -> str:
    layered = "@layer foundation {\n"
    for line in raw.splitlines():
        # @charset is only valid at the top of a stylesheet; strip it so it
        # doesn't appear nested inside @layer foundation after wrapping.
        if line.strip().lower().startswith("@charset"):
            continue
        layered += ("  " + line).rstrip() + "\n"
    layered += "}\n"
    return HEADER + layered + P3


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: wrap_foundation_layer.py <raw_css_in> <foundation_css_out>",
            file=sys.stderr,
        )
        return 1
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 1
    dst.write_text(wrap(src.read_text()))
    print(f"Written {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
