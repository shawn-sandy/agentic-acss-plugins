#!/usr/bin/env python3
"""
Convert Figma `get_variable_defs` output → our theme tokens JSON (Workstream C PR 6).

Figma's MCP `get_variable_defs` returns a flat map of variable name → value:

    { "color/primary": "#855300", "color/on-surface": "#151c27",
      "spacing/md": "24px", "radius/md": "8px",
      "fontFamily/body": "Public Sans", "fontSize/body-md": "16px" }

Figma variable names are freeform `category/name`, like Material-3 — the same
translation problem Appendix A already solves. So we **normalize** Figma's
`category/name` into the css-tailwind `--category-name` form and hand the whole
`@theme { }` block to `design_md_to_tokens.build_tokens`, reusing its M3→roles
mapping, OKLCH gap synthesis, and scale/typography lifting. No second mapping
table, no drift.

Pipeline (the `/theme-from-figma` flow):

    Figma MCP get_variable_defs   (in-session, against a live file)
      → figma_to_tokens.py         (this script — normalize names → tokens JSON)
      → tokens_to_css.py           (→ light/dark + space-radius + typography CSS)
      → validate_theme.py          (WCAG gate)

    For a DESIGN.md artifact instead of a theme, pipe the tokens JSON through
    tokens_to_design_md.py (Figma → DESIGN.md, per the Appendix B bridge).

Usage:
    python figma_to_tokens.py <vars.json>     # a get_variable_defs JSON map
    python figma_to_tokens.py --stdin
    python figma_to_tokens.py --self-test

Output: theme tokens JSON to stdout. Exit 0 ok, 1 logical failure (e.g. no
resolvable primary; reasons to stderr), 2 usage / IO error.

The only Figma-specific assumption is the category → css-tailwind prefix table
(FIGMA_CATEGORIES) below — the single reconciliation point against real
`get_variable_defs` output. Everything downstream is the shared adapter.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from design_md_to_tokens import build_tokens  # noqa: E402

# Figma variable *category* (the part before the first "/") → css-tailwind prefix
# that design_md_to_tokens already understands. Multiple Figma spellings collapse
# to one prefix; unknown categories pass through as `--<category>-<name>`.
FIGMA_CATEGORIES: dict[str, str] = {
    "color": "--color-",
    "colors": "--color-",
    "spacing": "--spacing-",
    "space": "--spacing-",
    "radius": "--radius-",
    "rounded": "--radius-",
    "borderradius": "--radius-",
    "cornerradius": "--radius-",
    "fontsize": "--text-",
    "textsize": "--text-",
    "fontweight": "--font-weight-",
    "weight": "--font-weight-",
    "lineheight": "--leading-",
    "leading": "--leading-",
    "letterspacing": "--tracking-",
    "tracking": "--tracking-",
    "fontfamily": "--font-",
    "font": "--font-",
    "family": "--font-",
}

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    return _SLUG_RE.sub("-", text.strip().lower()).strip("-")


def _coerce_value(value) -> str:
    """Figma values may be numbers (e.g. spacing 24) or strings ('24px', '#855300')."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value:g}px"            # bare numeric dimensions are px in Figma
    return str(value).strip()


def figma_to_css_tailwind(figma: dict) -> str:
    """Normalize a flat get_variable_defs map into a css-tailwind `@theme` block."""
    lines: list[str] = []
    for raw_name, raw_value in figma.items():
        name = str(raw_name)
        if "/" in name:
            category, rest = name.split("/", 1)
        else:
            category, rest = name, ""
        prefix = FIGMA_CATEGORIES.get(_slug(category), f"--{_slug(category)}-")
        suffix = _slug(rest) if rest else _slug(category)
        prop = prefix + suffix
        value = _coerce_value(raw_value)
        if not value:
            continue
        lines.append(f"  {prop}: {value};")
    return "@theme {\n" + "\n".join(lines) + "\n}\n"


def figma_to_tokens(figma: dict) -> tuple[dict, list[str]]:
    """Figma variable map → our theme tokens JSON (reusing the shared adapter)."""
    css = figma_to_css_tailwind(figma)
    return build_tokens(css)


_FIXTURE = {
    "color/primary": "#855300",
    "color/on-primary": "#ffffff",
    "color/primary-container": "#f59e0b",
    "color/background": "#f9f9ff",
    "color/surface": "#f9f9ff",
    "color/surface-container-high": "#e2e8f8",
    "color/on-surface": "#151c27",
    "color/on-surface-variant": "#534434",
    "color/outline": "#867461",
    "color/outline-variant": "#d8c3ad",
    "color/error": "#ba1a1a",
    "color/secondary": "#6750a4",
    "color/tertiary": "#1565c0",
    "spacing/xs": "4px",
    "spacing/md": "24px",          # → 1.5rem
    "spacing/xl": 32,              # bare number → 32px → 2rem
    "radius/md": "8px",            # → 0.5rem
    "radius/full": "9999px",       # pill sentinel preserved
    "fontFamily/body-md": "Public Sans",
    "fontSize/body-md": "16px",    # → 1rem
    "fontWeight/body-md": "400",
}


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            print(f"PASS: {name}"); passed += 1
        else:
            print(f"FAIL: {name} {detail}"); failed += 1

    css = figma_to_css_tailwind(_FIXTURE)
    check("color/primary → --color-primary", "  --color-primary: #855300;" in css)
    check("color/on-surface → --color-on-surface", "  --color-on-surface: #151c27;" in css)
    check("spacing/md → --spacing-md", "  --spacing-md: 24px;" in css)
    check("radius/md → --radius-md", "  --radius-md: 8px;" in css)
    check("bare numeric spacing coerced to px", "  --spacing-xl: 32px;" in css)
    check("fontSize → --text-", "  --text-body-md: 16px;" in css)
    check("fontWeight → --font-weight-", "  --font-weight-body-md: 400;" in css)
    check("fontFamily → --font-", "  --font-body-md: Public Sans;" in css)

    tokens, reasons = figma_to_tokens(_FIXTURE)
    light = tokens.get("modes", {}).get("light", {})
    check("primary mapped through adapter", light.get("--color-primary") == "#855300")
    check("on-surface → text", light.get("--color-text") == "#151c27")
    check("outline → border-strong", light.get("--color-border-strong") == "#867461")
    check("error → danger", light.get("--color-danger") == "#ba1a1a")
    check("all 15 required roles present", {
        "--color-background", "--color-surface", "--color-surface-raised", "--color-text",
        "--color-text-muted", "--color-text-inverse", "--color-border", "--color-border-strong",
        "--color-primary", "--color-primary-hover", "--color-success", "--color-warning",
        "--color-danger", "--color-info", "--color-focus-ring",
    } <= set(light), str(sorted(set(light))))
    check("success synthesized (no Figma source)", "--color-success" in light)
    check("spacing px→rem (24px→1.5rem)", tokens.get("spacing", {}).get("md") == "1.5rem")
    check("radius full sentinel preserved", tokens.get("rounded", {}).get("full") == "9999px")
    typo = tokens.get("typography", {}).get("body-md", {})
    check("typography recomposed", typo.get("size") == "1rem" and typo.get("family") == "Public Sans",
          str(typo))

    # no-primary → hard fail (inherited from build_tokens)
    empty, reasons2 = figma_to_tokens({"color/on-surface": "#111111"})
    check("no primary → empty + reason", empty == {} and any("primary" in r for r in reasons2))

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED"); return 1
    print(f"\nAll {total} self-tests PASSED"); return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()

    use_stdin = "--stdin" in args
    path = next((a for a in args if not a.startswith("--")), None)
    if not use_stdin and path is None:
        print("usage: figma_to_tokens.py <vars.json> | --stdin", file=sys.stderr)
        return 2
    try:
        figma = json.loads(sys.stdin.read()) if use_stdin else json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"error reading Figma variables: {e}", file=sys.stderr)
        return 2
    if not isinstance(figma, dict):
        print("error: expected a flat JSON object of variable name → value", file=sys.stderr)
        return 2

    tokens, reasons = figma_to_tokens(figma)
    for r in reasons:
        print(f"note: {r}", file=sys.stderr)
    if not tokens:
        return 1
    print(json.dumps(tokens, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
