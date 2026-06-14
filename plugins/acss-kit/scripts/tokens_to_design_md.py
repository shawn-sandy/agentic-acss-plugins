#!/usr/bin/env python3
"""
Export the acss-kit theme tokens JSON to a DESIGN.md (Workstream A PR 5).

The inverse of `design_md_to_tokens.py`, and the import-*into*-DESIGN.md path the
upstream CLI lacks (it is export-only). Pipeline:

    css_to_tokens.py <dir>           (our light.css + space-radius.css +
      → theme.tokens.json             typography.css → tokens JSON)
      → tokens_to_design_md.py        (apply the inverse of Appendix A — our 18
         roles → DESIGN.md token names — and emit YAML front-matter + a prose
         skeleton with the canonical ## sections)
      → DESIGN.md

Usage:
    python tokens_to_design_md.py <tokens.json> [--name=<Brand>]
    python tokens_to_design_md.py --stdin [--name=<Brand>]   # tokens JSON on stdin
    python tokens_to_design_md.py --dir=<dir> [--name=<Brand>]  # shells css_to_tokens
    python tokens_to_design_md.py --self-test

Output: DESIGN.md text to stdout. Exit 0 ok, 1 logical failure (nothing to
emit), 2 usage / IO error.

Semantic round-trip (value-preserving, not byte-identical): we emit the 18
`--color-*` roles under DESIGN.md token names; on re-import the adapter collapses
M3 ladders and re-synthesizes the roles M3 omits, so `surface-tint`, the
`*-container` accent pairs, and `*-fixed*` variants are not reproduced. The
roles our theme does not source from M3 (`success`, `warning`, `focus-ring`,
`text-subtle`) keep our own names and are re-synthesized rather than read back.

⚠️ FORMAT BOUNDARY — the exact DESIGN.md front-matter group/sub-keys
(`colors`/`spacing`/`rounded`/`typography`; `fontFamily`/`fontSize`/`fontWeight`/
`lineHeight`/`letterSpacing`) could not be verified against the upstream spec in
this build environment. Every name assumption lives in the tables below
(ROLE_TO_DMD / DMD_GROUPS / TYPO_KEYS) — the single place to reconcile against the
real spec. The map → emit → re-parse round-trip is exercised by --self-test.
See docs/plans/design-md-spec-alignment.md (§Round-trip & export, Appendix A).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# Name-adapter tables (the format boundary — reconcile here against the spec).
# Inverse of Appendix A / design_md_to_tokens.COLOR_SOURCES. Each of our 18
# roles maps to ONE DESIGN.md color token name. Where M3 has a unique slot we
# use its name (so the value round-trips through the adapter); where it has none
# we keep our own name (the value is preserved but re-synthesized on import).
# Order is the emission order.
# ---------------------------------------------------------------------------
ROLE_TO_DMD: list[tuple[str, str]] = [
    ("--color-background",     "background"),
    ("--color-surface",        "surface"),
    ("--color-surface-raised", "surface-container-high"),
    ("--color-surface-subtle", "surface-container-low"),   # optional
    ("--color-text",           "on-surface"),
    ("--color-text-muted",     "on-surface-variant"),
    ("--color-text-subtle",    "on-surface-subtle"),        # optional, no M3 slot
    ("--color-text-inverse",   "on-primary"),
    ("--color-border",         "outline-variant"),
    ("--color-border-strong",  "outline"),
    ("--color-primary",        "primary"),
    ("--color-primary-hover",  "primary-container"),
    ("--color-brand-accent",   "secondary"),                # optional
    ("--color-info",           "tertiary"),
    ("--color-danger",         "error"),
    ("--color-success",        "success"),                  # no M3 slot → our name
    ("--color-warning",        "warning"),                  # no M3 slot → our name
    ("--color-focus-ring",     "focus-ring"),               # no M3 slot → our name
]

# DESIGN.md front-matter scale group keys ← our tokens JSON keys.
DMD_GROUPS = {"spacing": "spacing", "rounded": "rounded"}

# DESIGN.md typography sub-keys ← our composite sub-keys.
TYPO_KEYS: list[tuple[str, str]] = [
    ("family",   "fontFamily"),
    ("size",     "fontSize"),
    ("weight",   "fontWeight"),
    ("line",     "lineHeight"),
    ("tracking", "letterSpacing"),
]

_NUM_RE = re.compile(r"^-?\d*\.?\d+$")


def _yaml_scalar(value, *, force_quote: bool = False) -> str:
    """Render a YAML scalar. Quote strings (hex starts with '#', a YAML comment),
    leave bare numbers (and integer font-weights) unquoted."""
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if not force_quote and _NUM_RE.match(s):
        return s                       # unitless number (e.g. lineHeight 1.5)
    return "'" + s.replace("'", "''") + "'"


def build_design_md(tokens: dict, name: str) -> tuple[str, list[str]]:
    """Return (design_md_text, reasons). reasons is empty on success."""
    reasons: list[str] = []
    modes = tokens.get("modes", {})
    light = modes.get("light", {})
    if not light:
        reasons.append("no light-mode colors in tokens JSON — nothing to export")
        return "", reasons

    # --- front-matter ---------------------------------------------------
    fm: list[str] = ["---", f"name: {_yaml_scalar(name, force_quote=True)}"]

    fm.append("colors:")
    color_rows: list[tuple[str, str, str]] = []   # (role, dmd_name, hex) for prose
    for role, dmd in ROLE_TO_DMD:
        hexv = light.get(role)
        if not hexv:
            continue
        fm.append(f"  {dmd}: {_yaml_scalar(hexv, force_quote=True)}")
        color_rows.append((role, dmd, hexv))

    scale_rows: dict[str, list[tuple[str, str]]] = {}
    for dmd_group, our_key in DMD_GROUPS.items():
        scale = tokens.get(our_key) or {}
        if not scale:
            continue
        fm.append(f"{dmd_group}:")
        rows = []
        for k, v in scale.items():
            fm.append(f"  {k}: {_yaml_scalar(v, force_quote=True)}")
            rows.append((k, v))
        scale_rows[dmd_group] = rows

    typo = tokens.get("typography") or {}
    if typo:
        fm.append("typography:")
        for style, sub in typo.items():
            fm.append(f"  {style}:")
            for our_sub, dmd_sub in TYPO_KEYS:
                if our_sub not in sub:
                    continue
                val = sub[our_sub]
                quote = our_sub == "family"          # families are strings
                if our_sub == "weight" and _NUM_RE.match(str(val)):
                    val = int(float(val))
                fm.append(f"    {dmd_sub}: {_yaml_scalar(val, force_quote=quote)}")
    fm.append("---")

    # --- prose skeleton -------------------------------------------------
    body: list[str] = [
        "",
        f"# {name}",
        "",
        "> Generated by acss-kit `/design-export` from the project theme tokens.",
        "> **Semantic round-trip** (value-preserving, not byte-identical): the 18",
        "> `--color-*` roles are emitted under DESIGN.md token names. M3 ladder",
        "> tokens our theme does not model (`surface-tint`, the `*-container` pairs,",
        "> `*-fixed*`) are not reproduced; roles with no M3 slot (`success`,",
        "> `warning`, `focus-ring`, `on-surface-subtle`) keep our names.",
        "",
        "## Overview",
        "",
        "TODO: describe the brand, tone, and intended use.",
        "",
        "## Colors",
        "",
        "| DESIGN.md token | acss-kit role | Value |",
        "|---|---|---|",
    ]
    for role, dmd, hexv in color_rows:
        body.append(f"| `{dmd}` | `{role}` | `{hexv}` |")

    if typo:
        body += ["", "## Typography", "", "| Style | Family | Size | Weight | Line |",
                 "|---|---|---|---|---|"]
        for style, sub in typo.items():
            body.append(
                f"| `{style}` | {sub.get('family', '—')} | {sub.get('size', '—')} "
                f"| {sub.get('weight', '—')} | {sub.get('line', '—')} |"
            )

    if scale_rows:
        body += ["", "## Spacing & Radius", ""]
        for group, rows in scale_rows.items():
            body.append(f"**{group}** — " + ", ".join(f"`{k}` {v}" for k, v in rows))
            body.append("")

    body += [
        "## Components",
        "",
        "TODO: bind component tokens to the roles above, e.g.",
        "`button-primary.background: {colors.primary}`. Component-level vars are",
        "not present in the exported theme tokens; add them here by hand or feed",
        "per-component CSS to a future `--components-dir` flag.",
        "",
    ]

    return "\n".join(fm) + "\n" + "\n".join(body), reasons


# ---------------------------------------------------------------------------
# Minimal re-parser for the emitter's own front-matter (round-trip checks).
# Not a general YAML parser — only handles the regular output of build_design_md.
# ---------------------------------------------------------------------------
def parse_front_matter_scalars(text: str) -> dict[str, dict[str, str]]:
    """Extract the flat `colors`/`spacing`/`rounded` maps from our DESIGN.md.
    Returns {group: {name: value}} with quotes/whitespace stripped."""
    out: dict[str, dict[str, str]] = {}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text
    group = None
    for line in fm.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^(\w[\w-]*):\s*$", line)
        if m and not line.startswith(" "):
            group = m.group(1)
            out.setdefault(group, {})
            continue
        m = re.match(r"^  ([\w-]+):\s*(.+?)\s*$", line)
        if m and group in ("colors", "spacing", "rounded"):
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] == "'":
                v = v[1:-1].replace("''", "'")
            out[group][m.group(1)] = v
    return out


def _tokens_from_dir(path: str) -> dict:
    """Shell css_to_tokens.py to assemble a tokens JSON from a theme dir."""
    here = os.path.dirname(__file__)
    proc = subprocess.run(
        [sys.executable, os.path.join(here, "css_to_tokens.py"), f"--dir={path}"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "css_to_tokens.py failed")
    return json.loads(proc.stdout)


_FIXTURE = {
    "modes": {
        "light": {
            "--color-background": "#ffffff",
            "--color-surface": "#f7f7f7",
            "--color-surface-raised": "#e2e8f8",
            "--color-text": "#151c27",
            "--color-text-muted": "#534434",
            "--color-text-inverse": "#ffffff",
            "--color-border": "#d8c3ad",
            "--color-border-strong": "#867461",
            "--color-primary": "#855300",
            "--color-primary-hover": "#6a4200",
            "--color-success": "#2e7d32",
            "--color-warning": "#9a6700",
            "--color-danger": "#ba1a1a",
            "--color-info": "#1565c0",
            "--color-focus-ring": "#855300",
        },
        "dark": {"--color-primary": "#ffb868"},
    },
    "spacing": {"xs": "0.25rem", "md": "1rem", "xl": "2rem"},
    "rounded": {"none": "0", "md": "0.5rem", "full": "9999px"},
    "typography": {
        "body-md": {"family": "Public Sans", "size": "1rem", "weight": "400", "line": "1.5"},
    },
}


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            print(f"PASS: {name}"); passed += 1
        else:
            print(f"FAIL: {name} {detail}"); failed += 1

    text, reasons = build_design_md(_FIXTURE, "Paws and Paths")
    check("no reasons on success", reasons == [], str(reasons))
    check("front-matter opens", text.startswith("---\nname: 'Paws and Paths'"))
    check("primary mapped to M3 name", "\n  primary: '#855300'" in text)
    check("text → on-surface", "\n  on-surface: '#151c27'" in text)
    check("border-strong → outline", "\n  outline: '#867461'" in text)
    check("hex values are quoted (YAML # safety)", "'#855300'" in text and "background: '#ffffff'" in text)
    check("spacing emitted", "\nspacing:\n  xs: '0.25rem'" in text)
    check("rounded full sentinel", "\n  full: '9999px'" in text)
    check("typography camelCase keys", "fontFamily: 'Public Sans'" in text and "fontSize: '1rem'" in text)
    check("font-weight unquoted int", "fontWeight: 400" in text)
    check("lineHeight unquoted number", "lineHeight: 1.5" in text)
    check("prose has canonical sections",
          all(s in text for s in ("## Overview", "## Colors", "## Typography",
                                  "## Spacing & Radius", "## Components")))
    check("success kept under our name (no M3 slot)", "\n  success: '#2e7d32'" in text)

    # round-trip: parse our own front-matter back, assert values preserved
    parsed = parse_front_matter_scalars(text)
    check("round-trip primary value", parsed.get("colors", {}).get("primary") == "#855300")
    check("round-trip on-surface value", parsed.get("colors", {}).get("on-surface") == "#151c27")
    check("round-trip spacing md", parsed.get("spacing", {}).get("md") == "1rem")
    check("round-trip rounded full", parsed.get("rounded", {}).get("full") == "9999px")
    n_colors = len([1 for r, _ in ROLE_TO_DMD if r in _FIXTURE["modes"]["light"]])
    check("round-trip color count preserved", len(parsed.get("colors", {})) == n_colors,
          f"{len(parsed.get('colors', {}))} vs {n_colors}")

    # empty-input path
    empty, reasons2 = build_design_md({"modes": {}}, "X")
    check("empty light → reason + no text", empty == "" and any("nothing" in r for r in reasons2))

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED"); return 1
    print(f"\nAll {total} self-tests PASSED"); return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()

    name = "Project"
    for a in args:
        if a.startswith("--name="):
            name = a.split("=", 1)[1]

    dir_arg = next((a.split("=", 1)[1] for a in args if a.startswith("--dir=")), None)
    use_stdin = "--stdin" in args
    path = next((a for a in args if not a.startswith("--")), None)

    try:
        if dir_arg:
            tokens = _tokens_from_dir(dir_arg)
        elif use_stdin:
            tokens = json.loads(sys.stdin.read())
        elif path:
            with open(path, encoding="utf-8") as f:
                tokens = json.load(f)
        else:
            print("usage: tokens_to_design_md.py <tokens.json> | --stdin | --dir=<dir> [--name=<Brand>]",
                  file=sys.stderr)
            return 2
    except Exception as e:
        print(f"error reading tokens: {e}", file=sys.stderr)
        return 2

    text, reasons = build_design_md(tokens, name)
    for r in reasons:
        print(f"note: {r}", file=sys.stderr)
    if not text:
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
