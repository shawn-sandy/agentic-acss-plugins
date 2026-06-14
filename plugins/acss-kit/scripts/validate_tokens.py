#!/usr/bin/env python3
"""
Validate the non-color token sections of a theme tokens JSON.

Checks the spacing / rounded / typography sections (the DESIGN.md-parity token
kinds) for structural correctness — the dimension/typography equivalent of the
WCAG contrast gate that validate_theme.py applies to colors:

  - spacing / rounded: every value is a valid dimension (0 | <num>px|em|rem)
  - spacing / rounded: recommended scale steps present (warning if missing)
  - typography: `size` is a dimension; `weight` numeric/keyword; `line` unitless
    or dimension; `tracking` a dimension; `family` a non-empty string

Usage:
    python validate_tokens.py <tokens.json>
    python validate_tokens.py --stdin        (reads JSON from stdin)
    python validate_tokens.py --self-test

Exit codes:
    0 = no errors (warnings allowed)
    1 = at least one structural error
    2 = usage / IO error

No external dependencies — stdlib only.
"""
from __future__ import annotations

import json
import re
import sys

DIMENSION_RE = re.compile(r"^(0|[0-9]*\.?[0-9]+(px|em|rem))$")
UNITLESS_RE = re.compile(r"^[0-9]*\.?[0-9]+$")
WEIGHT_RE = re.compile(r"^([1-9]00|normal|bold|lighter|bolder)$")

RECOMMENDED_STEPS = {
    "spacing": {"sm", "md", "lg"},
    "rounded": {"md"},
}
TYPO_SUBPROPS = ("family", "size", "weight", "line", "tracking")


def validate(tokens: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # Dimension scales: spacing, rounded.
    for kind in ("spacing", "rounded"):
        scale = tokens.get(kind)
        if scale is None:
            continue
        if not isinstance(scale, dict):
            errors.append(f"{kind}: must be an object mapping step name to dimension")
            continue
        for name, value in scale.items():
            if not isinstance(value, str) or not DIMENSION_RE.match(value):
                errors.append(f"{kind}.{name}: '{value}' is not a valid dimension (0 | <num>px|em|rem)")
        missing = RECOMMENDED_STEPS[kind] - set(scale)
        if missing:
            warnings.append(f"{kind}: missing recommended steps {sorted(missing)}")

    # Typography composites.
    typ = tokens.get("typography")
    if typ is not None:
        if not isinstance(typ, dict):
            errors.append("typography: must be an object mapping role to a composite")
        else:
            for role, sub in typ.items():
                if not isinstance(sub, dict):
                    errors.append(f"typography.{role}: must be an object")
                    continue
                for key in sub:
                    if key not in TYPO_SUBPROPS:
                        warnings.append(f"typography.{role}.{key}: unknown sub-property")
                if "size" in sub and not DIMENSION_RE.match(str(sub["size"])):
                    errors.append(f"typography.{role}.size: '{sub['size']}' is not a valid dimension")
                if "weight" in sub and not WEIGHT_RE.match(str(sub["weight"])):
                    errors.append(f"typography.{role}.weight: '{sub['weight']}' is not a valid font-weight")
                if "line" in sub:
                    v = str(sub["line"])
                    if not (UNITLESS_RE.match(v) or DIMENSION_RE.match(v)):
                        errors.append(f"typography.{role}.line: '{v}' must be unitless or a dimension")
                if "tracking" in sub:
                    v = str(sub["tracking"])
                    if not DIMENSION_RE.match(v):
                        errors.append(f"typography.{role}.tracking: '{v}' must be a dimension")
                if "family" in sub and not (isinstance(sub["family"], str) and sub["family"].strip()):
                    errors.append(f"typography.{role}.family: must be a non-empty string")

    return errors, warnings


def _report(tokens: dict) -> int:
    errors, warnings = validate(tokens)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — FAIL")
        return 1
    print(f"tokens OK ({len(warnings)} warning(s))")
    return 0


def self_test() -> int:
    passed = failed = 0

    def check(name: str, tokens: dict, expect_errors: bool) -> None:
        nonlocal passed, failed
        errors, _ = validate(tokens)
        ok = bool(errors) == expect_errors
        if ok:
            print(f"PASS: {name}")
            passed += 1
        else:
            print(f"FAIL: {name} — errors={errors}")
            failed += 1

    check("valid spacing + rounded", {"spacing": {"sm": "0.5rem", "md": "1rem", "lg": "1.5rem"}, "rounded": {"md": "0.5rem", "full": "9999px"}}, False)
    check("valid typography", {"typography": {"body-md": {"family": "Public Sans", "size": "1rem", "weight": "400", "line": "1.5", "tracking": "0.01em"}}}, False)
    check("bad spacing unit", {"spacing": {"md": "12"}}, True)
    check("bad radius value", {"rounded": {"md": "round"}}, True)
    check("bad typography size", {"typography": {"h1": {"size": "big"}}}, True)
    check("bad font weight", {"typography": {"h1": {"weight": "extra"}}}, True)
    check("empty input is valid", {}, False)
    check("colors-only input is valid (no token sections)", {"modes": {"light": {"--color-primary": "#fff"}}}, False)

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

    use_stdin = "--stdin" in args
    path = next((a for a in args if not a.startswith("--")), None)

    if not use_stdin and path is None:
        print("usage: validate_tokens.py <tokens.json> | --stdin", file=sys.stderr)
        return 2
    try:
        raw = sys.stdin.read() if use_stdin else open(path, encoding="utf-8").read()
        tokens = json.loads(raw)
    except Exception as e:
        print(f"error reading tokens: {e}", file=sys.stderr)
        return 2

    return _report(tokens)


if __name__ == "__main__":
    sys.exit(main())
