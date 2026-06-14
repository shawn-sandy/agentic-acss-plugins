#!/usr/bin/env python3
"""
Convert theme CSS files into a theme.tokens.json file.

Usage:
    python css_to_tokens.py <light.css> [dark.css] [brand-*.css ...]
    python css_to_tokens.py --dir=<dir>   (scans for light.css, dark.css, brand-*.css)
    python css_to_tokens.py --self-test

Output: JSON to stdout conforming to assets/theme.schema.json.

Exit codes: 0 = success, 2 = usage/IO error.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _tokens import (  # noqa: E402
    BRAND_ROLES,
    RADIUS_PREFIX,
    SPACE_PREFIX,
    extract_selector_blocks,
    parse_palette_from_block,
    parse_scale_from_block,
    parse_typography_from_block,
)

PALETTE_FILE_RE = re.compile(r"^(light|dark|brand-[\w-]+|space-radius|typography)\.css$")


def _process_file(path: Path) -> tuple[str, dict]:
    """Return (file_type, data). file_type is 'light', 'dark', or 'brand-<name>'."""
    text = path.read_text(encoding="utf-8")
    stem = path.stem  # e.g. 'light', 'dark', 'brand-forest'

    if stem in ("light", "dark"):
        blocks = extract_selector_blocks(text)
        if stem in blocks:
            return stem, parse_palette_from_block(blocks[stem])
        return stem, parse_palette_from_block(text)

    if stem.startswith("brand-"):
        name = stem[len("brand-"):]
        blocks = extract_selector_blocks(text)
        overrides: dict = {}
        for mode_key, block in blocks.items():
            palette = parse_palette_from_block(block)
            filtered = {k: v for k, v in palette.items() if k in BRAND_ROLES}
            if filtered:
                overrides[mode_key] = filtered
        return f"brand-{name}", overrides

    if stem == "space-radius":
        return "space-radius", {
            "spacing": parse_scale_from_block(text, SPACE_PREFIX),
            "rounded": parse_scale_from_block(text, RADIUS_PREFIX),
        }

    if stem == "typography":
        return "typography", parse_typography_from_block(text)

    return stem, parse_palette_from_block(text)


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict[str, str], checks: list[str],
            absent: list[str] | None = None) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_ = Path(tmpdir)
            for fname, content in files.items():
                (dir_ / fname).write_text(content, encoding="utf-8")
            old_argv = sys.argv
            sys.argv = ["css_to_tokens.py", f"--dir={tmpdir}"]
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = buf = StringIO()
            try:
                code = main()
            finally:
                sys.argv = old_argv
                sys.stdout = old_stdout
            output = buf.getvalue()
            ok = code == 0
            ok = ok and all(chk in output for chk in checks)
            if absent:
                ok = ok and all(a not in output for a in absent)
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                missing = [c for c in checks if c not in output]
                unexpected = [a for a in (absent or []) if a in output]
                print(f"FAIL: {name} — code={code} missing={missing} unexpected={unexpected}")
                if output:
                    print("  output:", output[:300])
                failed += 1

    # Round-trip: write light.css that tokens_to_css.py would produce, read back
    light_css = """\
:root {

  /* Backgrounds */
  --color-background: var(--color-background, #ffffff);
  --color-surface: var(--color-surface, #f8fafc);

  /* Brand + semantic */
  --color-primary: var(--color-primary, #4f46e5);
  --color-danger: var(--color-danger, #dc2626);
}
"""
    dark_css = """\
[data-theme="dark"] {

  /* Backgrounds */
  --color-background: var(--color-background, #0f172a);

  /* Brand + semantic */
  --color-primary: var(--color-primary, #7dd3fc);
}
"""
    run(
        "light.css — primary and background extracted",
        {"light.css": light_css},
        ['"--color-primary": "#4f46e5"', '"--color-background": "#ffffff"'],
    )
    run(
        "dark.css — dark mode primary extracted",
        {"dark.css": dark_css},
        ['"--color-primary": "#7dd3fc"', '"dark"'],
    )
    run(
        "both light and dark",
        {"light.css": light_css, "dark.css": dark_css},
        ['"light"', '"dark"', '"--color-primary"'],
    )
    run(
        "brand file — only BRAND_ROLES included",
        {"brand-forest.css": """\
:root {
  --color-primary: var(--color-primary, #2f7a4d);
  --color-danger: var(--color-danger, #dc2626);
}
"""},
        ['"forest"', '"--color-primary"'],
        absent=['"--color-danger"'],
    )
    run(
        "round-trip — light hex survives css→json",
        {"light.css": light_css},
        ['"#4f46e5"'],
    )
    space_radius_css = """\
:root {

  /* Spacing */
  --space-md: var(--space-md, 1rem);

  /* Radius */
  --radius-full: var(--radius-full, 9999px);
}
"""
    typography_css = """\
:root {

  /* body-md */
  --font-body-md-size: var(--font-body-md-size, 1rem);
  --font-body-md-weight: var(--font-body-md-weight, 400);
}
"""
    run(
        "space-radius.css — spacing and rounded extracted",
        {"space-radius.css": space_radius_css},
        ['"spacing"', '"md": "1rem"', '"rounded"', '"full": "9999px"'],
    )
    run(
        "typography.css — composite sub-props extracted",
        {"typography.css": typography_css},
        ['"typography"', '"body-md"', '"size": "1rem"', '"weight": "400"'],
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


def main() -> int:
    args = sys.argv[1:]

    if "--self-test" in args:
        return self_test()

    scan_dir: Path | None = None
    file_paths: list[Path] = []

    for a in args:
        if a.startswith("--dir="):
            scan_dir = Path(a.split("=", 1)[1])
        elif not a.startswith("--"):
            file_paths.append(Path(a))

    if scan_dir:
        for p in scan_dir.rglob("*.css"):
            if PALETTE_FILE_RE.match(p.name):
                file_paths.append(p)

    if not file_paths:
        print("usage: css_to_tokens.py <light.css> [dark.css] [brand-*.css ...] | --dir=<dir>",
              file=sys.stderr)
        return 2

    tokens: dict = {"modes": {}, "brands": {}}

    for path in file_paths:
        if not path.exists():
            print(f"not found: {path}", file=sys.stderr)
            return 2
        file_type, data = _process_file(path)
        if file_type in ("light", "dark"):
            tokens["modes"][file_type] = data
        elif file_type.startswith("brand-"):
            name = file_type[len("brand-"):]
            tokens["brands"][name] = data
        elif file_type == "space-radius":
            if data.get("spacing"):
                tokens["spacing"] = data["spacing"]
            if data.get("rounded"):
                tokens["rounded"] = data["rounded"]
        elif file_type == "typography":
            if data:
                tokens["typography"] = data

    if not tokens["brands"]:
        del tokens["brands"]

    print(json.dumps(tokens, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
