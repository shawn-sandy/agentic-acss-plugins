#!/usr/bin/env python3
"""
generate_color_scale.py — Generate a 10-step OKLCH color scale from a seed hex color.

Contract: generator/validator
  - Data to stdout (JSON, CSS, or both); errors to stderr; exit 0/1/2.

Usage:
  python generate_color_scale.py <hex-color> [--name=<name>] [--format=css|json|both]

Arguments:
  <hex-color>           Seed color as #rrggbb or #rgb
  --name=<name>         CSS variable prefix, kebab-case  (default: "scale")
  --format=css|json|both  Output format                  (default: both)

Output JSON shape:
  {
    "name": "primary",
    "seed": "#4f46e5",
    "seed_oklch": {"L": 0.4823, "C": 0.2108, "H": 264.05},
    "steps": [
      {"step": 50,  "hex": "#f5f3ff", "oklch": "oklch(0.965 0.0213 264.1)", "css_var": "--color-primary-50"},
      ...
      {"step": 900, "hex": "#1e1b4b", "oklch": "oklch(0.141 0.0812 264.1)", "css_var": "--color-primary-900"}
    ]
  }

CSS output uses the ``var(--x, <fallback>)`` convention required by acss-kit.
"""
from __future__ import annotations

import json
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from _oklch import hex_to_oklch, in_gamut, oklch_to_hex  # noqa: E402

# 10 perceptually-distributed lightness steps: near-white (50) → near-black (900).
# Chroma and hue are preserved from the seed; oklch_to_hex clamps to sRGB gamut.
_STEPS = [
    (50,  0.970),
    (100, 0.935),
    (200, 0.875),
    (300, 0.785),
    (400, 0.670),
    (500, 0.550),
    (600, 0.435),
    (700, 0.335),
    (800, 0.235),
    (900, 0.135),
]

_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_USAGE = "Usage: generate_color_scale.py <hex-color> [--name=<name>] [--format=css|json|both]"


def _parse_args(argv: list[str]) -> tuple[str, str, str]:
    positional: list[str] = []
    name = "scale"
    format_ = "both"
    unknown: list[str] = []
    for arg in argv[1:]:
        if arg.startswith("--name="):
            name = arg[7:].strip()
        elif arg.startswith("--format="):
            format_ = arg[9:].strip()
        elif arg.startswith("--"):
            unknown.append(arg)
        else:
            positional.append(arg)
    if unknown:
        print(f"Unknown option(s): {', '.join(unknown)}\n{_USAGE}", file=sys.stderr)
        sys.exit(2)
    if len(positional) != 1:
        print(_USAGE, file=sys.stderr)
        sys.exit(2)
    return positional[0], name, format_


def _validate_hex(hex_str: str) -> str:
    h = hex_str[1:] if hex_str.startswith("#") else hex_str
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not all(c in "0123456789abcdefABCDEF" for c in h):
        print(
            f'"{hex_str}" is not a valid hex color. Use #rrggbb or #rgb.',
            file=sys.stderr,
        )
        sys.exit(2)
    return "#" + h.lower()


def _validate_name(name: str) -> str:
    if not _NAME_RE.match(name):
        print(
            f'"--name" must be a lowercase kebab-case identifier (e.g. "primary", "brand-blue"). '
            f'Got: "{name}"',
            file=sys.stderr,
        )
        sys.exit(2)
    return name


def _fmt_oklch(L: float, C: float, H: float) -> str:
    return f"oklch({L:.3f} {C:.4f} {H:.1f})"


def build_scale(hex_color: str, name: str) -> dict:
    hex_color = _validate_hex(hex_color)
    seed_L, seed_C, seed_H = hex_to_oklch(hex_color)
    steps = []
    reasons: list[str] = []
    for step, target_L in _STEPS:
        clamped = not in_gamut(target_L, seed_C, seed_H)
        step_reasons = (
            [f"out of gamut, clamped to sRGB (requested oklch({target_L:.3f} {seed_C:.4f} {seed_H:.1f}))"]
            if clamped else []
        )
        if step_reasons:
            reasons.append(f"step {step}: {step_reasons[0]}")
        step_hex = oklch_to_hex(target_L, seed_C, seed_H)
        # Re-derive actual OKLCH after gamut clamping for accurate reporting.
        actual_L, actual_C, actual_H = hex_to_oklch(step_hex)
        steps.append({
            "step": step,
            "hex": step_hex,
            "oklch": _fmt_oklch(actual_L, actual_C, actual_H),
            "css_var": f"--color-{name}-{step}",
            "clamped": clamped,
            "reasons": step_reasons,
        })
    return {
        "name": name,
        "seed": hex_color,
        "seed_oklch": {
            "L": round(seed_L, 4),
            "C": round(seed_C, 4),
            "H": round(seed_H, 2),
        },
        "steps": steps,
        "reasons": reasons,
    }


def to_css(scale: dict) -> str:
    lines = [":root {"]
    for s in scale["steps"]:
        var = s["css_var"]
        lines.append(f"  {var}: var({var}, {s['hex']});")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    hex_color, name, format_ = _parse_args(sys.argv)
    if format_ not in ("css", "json", "both"):
        print(f'--format must be css, json, or both. Got: "{format_}"', file=sys.stderr)
        sys.exit(2)
    name = _validate_name(name)

    scale = build_scale(hex_color, name)

    if format_ == "css":
        print(to_css(scale))
    elif format_ == "json":
        print(json.dumps(scale, indent=2))
    else:  # both: JSON section, blank line, CSS section
        print(json.dumps(scale, indent=2))
        print()
        print(to_css(scale))


if __name__ == "__main__":
    main()
