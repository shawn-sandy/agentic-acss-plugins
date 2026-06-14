#!/usr/bin/env python3
"""
Convert a DESIGN.md into the acss-kit theme tokens JSON (Workstream A PR 4).

Route 1 (decided 2026-06-14): consume the upstream CLI's `css-tailwind` export
rather than parse YAML in Python stdlib. Pipeline:

    npx @google/design.md export --format css-tailwind DESIGN.md
      → design_md_to_tokens.py   (parse @theme custom properties; map the
         Tailwind/Material-3 names to our 18 roles + spacing/rounded/typography
         scales; synthesize the color roles M3 omits via OKLCH)
      → theme.tokens.json        (consumed by tokens_to_css.py)

Usage:
    python design_md_to_tokens.py <DESIGN.md>    # shells `npx … export css-tailwind`
    python design_md_to_tokens.py --stdin        # reads a css-tailwind block from stdin
    python design_md_to_tokens.py --self-test

Output: theme tokens JSON to stdout. Exit 0 ok, 1 logical failure (reasons to
stderr), 2 usage / IO error.

⚠️ FORMAT BOUNDARY — the exact Tailwind v4 `@theme` prefixes emitted by
`@google/design.md export --format css-tailwind` are `alpha` and could not be
verified in this build environment. Every name-mapping assumption lives in the
adapter tables below (COLOR_SOURCES / TW_SPACE / TW_RADIUS / TW_TYPO_*) — that is
the single place to reconcile against the real CLI output. The parse → map →
synthesize → emit pipeline is exercised by --self-test against a fixture.
See docs/plans/design-md-token-parity.md (PR 4).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _tokens import ALL_ROLES, parse_vars  # noqa: E402
from _oklch import hex_to_oklch  # noqa: E402
from generate_palette import _generate_dark, _generate_light  # noqa: E402

# ---------------------------------------------------------------------------
# Name-adapter tables (the format boundary — reconcile here against real CLI).
# Tailwind v4 @theme namespaces differ from ours: TW uses --spacing-*, --text-*,
# --font-weight-*, --leading-*, --tracking-*; only --radius-* matches. DESIGN.md
# colors follow Material-3 names. We map both onto our roles/scales.
# ---------------------------------------------------------------------------

# our role  →  ordered candidate Tailwind/M3 color custom-property names.
# First candidate present (resolving to a hex) wins; absent roles are synthesized.
COLOR_SOURCES: dict[str, list[str]] = {
    "--color-background":     ["--color-background", "--color-surface"],
    "--color-surface":        ["--color-surface", "--color-surface-container-lowest"],
    "--color-surface-raised": ["--color-surface-container-high", "--color-surface-container-highest", "--color-surface-container"],
    "--color-surface-subtle": ["--color-surface-container-low", "--color-surface-dim"],
    "--color-text":           ["--color-on-surface", "--color-on-background"],
    "--color-text-muted":     ["--color-on-surface-variant"],
    "--color-text-inverse":   ["--color-on-primary"],
    "--color-border":         ["--color-outline-variant"],
    "--color-border-strong":  ["--color-outline"],
    "--color-primary":        ["--color-primary"],
    "--color-primary-hover":  ["--color-primary-container", "--color-inverse-primary"],
    "--color-danger":         ["--color-error"],
    "--color-brand-accent":   ["--color-secondary"],
    "--color-info":           ["--color-tertiary"],
    # --color-success / --color-warning / --color-focus-ring: no M3 source → OKLCH-synthesized.
}

TW_SPACE = "--spacing-"     # → our spacing.<name>
TW_RADIUS = "--radius-"     # → our rounded.<name>  (matches our prefix)
# typography is split across these TW namespaces, recomposed into one composite:
TW_TYPO = {
    "size":     "--text-",
    "weight":   "--font-weight-",
    "line":     "--leading-",
    "tracking": "--tracking-",
    "family":   "--font-",          # checked AFTER --font-weight- to avoid overlap
}

_HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")
_DIM_RE = re.compile(r"^\s*(-?\d*\.?\d+)(px|rem|em)?\s*$")


def _hex(value: str) -> str | None:
    m = _HEX_RE.search(value or "")
    if not m:
        return None
    h = m.group(1)
    return "#" + (h if len(h) == 6 else "".join(c * 2 for c in h))


def _norm_dim(value: str) -> str:
    """Normalize a dimension to rem where sensible (px ÷ 16). Large pixel values
    (≥ 256px, e.g. the `9999px` pill-radius sentinel) pass through unchanged."""
    m = _DIM_RE.match(value or "")
    if not m:
        return value.strip()
    num, unit = m.group(1), m.group(2)
    if unit == "px":
        v = float(num)
        if v >= 256:                      # pill / sentinel (9999px, 999px) — keep px
            return value.strip()
        return f"{v / 16:g}rem"
    if unit is None:
        return "0" if float(num) == 0 else value.strip()
    return value.strip()


def map_colors(tw: dict[str, str]) -> dict[str, str]:
    """Resolve our color roles from the Tailwind/M3 custom properties present."""
    out: dict[str, str] = {}
    for role, candidates in COLOR_SOURCES.items():
        for cand in candidates:
            if cand in tw:
                h = _hex(tw[cand])
                if h:
                    out[role] = h
                    break
    return out


def map_scale(tw: dict[str, str], prefix: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for name, value in tw.items():
        if name.startswith(prefix):
            out[name[len(prefix):]] = _norm_dim(value)
    return out


def map_typography(tw: dict[str, str]) -> dict[str, dict[str, str]]:
    """Recompose split TW typography namespaces into {role: {sub: value}}."""
    out: dict[str, dict[str, str]] = {}
    for sub, prefix in TW_TYPO.items():
        for name, value in tw.items():
            if not name.startswith(prefix):
                continue
            if sub == "family" and name.startswith(TW_TYPO["weight"]):
                continue  # --font-weight-* is not --font-* family
            role = name[len(prefix):]
            v = _norm_dim(value) if sub in ("size", "tracking") else value.strip()
            out.setdefault(role, {})[sub] = v
    return out


def build_tokens(css: str) -> tuple[dict, list[str]]:
    """css-tailwind @theme block → (theme tokens JSON, reasons)."""
    reasons: list[str] = []
    tw = parse_vars(css)

    provided = map_colors(tw)
    primary = provided.get("--color-primary")
    if not primary:
        reasons.append("DESIGN.md has no resolvable primary color (--color-primary); cannot seed the palette.")
        return {}, reasons

    # Base full light/dark palettes from the primary (guarantees all 18 roles +
    # contrast), then overlay the DESIGN.md-provided roles. DESIGN.md is
    # mode-thin, so dark stays OKLCH-synthesized.
    L, C, H = hex_to_oklch(primary)
    light, lr = _generate_light(L, C, H)
    dark, dr = _generate_dark(L, C, H)
    reasons += lr + dr

    overlay = {k: v for k, v in provided.items() if k in ALL_ROLES}
    light = {**light, **overlay}

    synthesized = [r for r in ("--color-success", "--color-warning", "--color-info", "--color-focus-ring")
                   if r not in overlay]
    if synthesized:
        reasons.append("Synthesized via OKLCH (no Material-3 source): " + ", ".join(synthesized))

    tokens: dict = {"modes": {"light": light, "dark": dark}}
    spacing = map_scale(tw, TW_SPACE)
    rounded = map_scale(tw, TW_RADIUS)
    typography = map_typography(tw)
    if spacing:
        tokens["spacing"] = spacing
    if rounded:
        tokens["rounded"] = rounded
    if typography:
        tokens["typography"] = typography
    return tokens, reasons


def _export_via_npx(design_md_path: str) -> str:
    """Shell `npx @google/design.md export --format css-tailwind <path>`."""
    proc = subprocess.run(
        ["npx", "@google/design.md", "export", "--format", "css-tailwind", design_md_path],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"`npx @google/design.md export` failed (exit {proc.returncode}). "
            f"Is Node/npx available? stderr: {proc.stderr.strip()[:300]}"
        )
    return proc.stdout


# Representative css-tailwind fixture (Material-3 colors + scales) for --self-test.
# Mirrors the format documented in docs/proposals/design-md-spec-alignment.md
# Appendix F; values from the paws-and-paths example (Appendix D).
_FIXTURE = """\
@theme {
  --color-primary: #855300;
  --color-on-primary: #ffffff;
  --color-primary-container: #f59e0b;
  --color-background: #f9f9ff;
  --color-surface: #f9f9ff;
  --color-surface-container-high: #e2e8f8;
  --color-surface-container-low: #f0f3ff;
  --color-on-surface: #151c27;
  --color-on-surface-variant: #534434;
  --color-outline: #867461;
  --color-outline-variant: #d8c3ad;
  --color-error: #ba1a1a;
  --color-secondary: #0058be;
  --color-tertiary: #00658b;
  --spacing-xs: 4px;
  --spacing-md: 24px;
  --radius-md: 0.75rem;
  --radius-full: 9999px;
  --text-body-md: 16px;
  --font-weight-body-md: 400;
  --leading-body-md: 24px;
  --font-body-md: Public Sans;
}
"""


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            print(f"PASS: {name}"); passed += 1
        else:
            print(f"FAIL: {name} {detail}"); failed += 1

    tokens, reasons = build_tokens(_FIXTURE)
    light = tokens.get("modes", {}).get("light", {})

    check("primary mapped", light.get("--color-primary") == "#855300")
    check("on-primary → text-inverse", light.get("--color-text-inverse") == "#ffffff")
    check("on-surface → text", light.get("--color-text") == "#151c27")
    check("outline → border-strong", light.get("--color-border-strong") == "#867461")
    check("outline-variant → border", light.get("--color-border") == "#d8c3ad")
    check("surface-container-high → surface-raised", light.get("--color-surface-raised") == "#e2e8f8")
    check("error → danger", light.get("--color-danger") == "#ba1a1a")
    check("all 15 required roles present", {
        "--color-background", "--color-surface", "--color-surface-raised", "--color-text",
        "--color-text-muted", "--color-text-inverse", "--color-border", "--color-border-strong",
        "--color-primary", "--color-primary-hover", "--color-success", "--color-warning",
        "--color-danger", "--color-info", "--color-focus-ring",
    } <= set(light), str(sorted(set(light))))
    check("success synthesized (not from M3)", "--color-success" in light)
    check("dark mode synthesized", bool(tokens.get("modes", {}).get("dark")))
    check("spacing px→rem (24px→1.5rem)", tokens.get("spacing", {}).get("md") == "1.5rem")
    check("spacing xs (4px→0.25rem)", tokens.get("spacing", {}).get("xs") == "0.25rem")
    check("radius mapped", tokens.get("rounded", {}).get("md") == "0.75rem")
    check("radius full", tokens.get("rounded", {}).get("full") == "9999px")
    typo = tokens.get("typography", {}).get("body-md", {})
    check("typography recomposed", typo.get("size") == "1rem" and typo.get("weight") == "400"
          and typo.get("family") == "Public Sans", str(typo))
    check("typography family not polluted by font-weight", typo.get("family") == "Public Sans")

    # missing-primary path
    empty, reasons2 = build_tokens("@theme { --color-on-surface: #111111; }")
    check("missing primary → empty + reason", empty == {} and any("primary" in r for r in reasons2))

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
        print("usage: design_md_to_tokens.py <DESIGN.md> | --stdin", file=sys.stderr)
        return 2
    try:
        css = sys.stdin.read() if use_stdin else _export_via_npx(path)
    except Exception as e:
        print(f"error obtaining css-tailwind: {e}", file=sys.stderr)
        return 2

    tokens, reasons = build_tokens(css)
    for r in reasons:
        print(f"note: {r}", file=sys.stderr)
    if not tokens:
        return 1
    print(json.dumps(tokens, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
