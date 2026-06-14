#!/usr/bin/env python3
"""
Validate a DESIGN.md before the token pipeline consumes it (Workstream A PR 4).

Detector contract: JSON to stdout with a `reasons` array; exit 0 = usable,
1 = rejected, 2 = usage / IO error.

Shells the upstream linter (`npx @google/design.md lint <file> --format json`)
and normalizes its findings to our contract. Per the 2026-06-14 review decision,
a **missing primary color is a hard error** (the primary is the OKLCH seed the
whole pipeline depends on) — diverging from the upstream CLI, which treats
`missing-primary` as a warning. Other warnings are surfaced in `reasons` but do
not fail.

Usage:
    python validate_design_md.py <DESIGN.md>
    python validate_design_md.py --self-test

⚠️ FORMAT BOUNDARY — the upstream `lint --format json` shape is `alpha` and
unverified here. `classify()` assumes findings of the form
`{"rule": <id>, "level": "error|warning|info", "message": <str>}` (also accepts
`severity`/`ruleId`). Reconcile in classify()/ERROR_RULES against the real CLI.
See docs/plans/design-md-token-parity.md (PR 4) and Appendix C of the proposal.
"""
from __future__ import annotations

import json
import subprocess
import sys

# Rules that REJECT the file (exit 1). `missing-primary` is here by our decision
# even though upstream emits it as a warning.
ERROR_RULES = {"broken-ref", "duplicate-section", "duplicate-heading", "missing-primary"}


def _finding_field(f: dict, *names: str) -> str:
    for n in names:
        if n in f and f[n]:
            return str(f[n])
    return ""


def classify(findings: list[dict]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) from a list of lint findings."""
    errors: list[str] = []
    warnings: list[str] = []
    for f in findings or []:
        rule = _finding_field(f, "rule", "ruleId", "id")
        level = _finding_field(f, "level", "severity").lower()
        msg = _finding_field(f, "message", "msg", "text") or rule
        line = f"[{rule}] {msg}" if rule else msg
        if rule in ERROR_RULES or level == "error":
            errors.append(line)
        else:
            warnings.append(line)
    return errors, warnings


def _lint_via_npx(design_md_path: str) -> list[dict]:
    proc = subprocess.run(
        ["npx", "@google/design.md", "lint", design_md_path, "--format", "json"],
        capture_output=True, text=True,
    )
    # The CLI exits non-zero when it finds errors; that's expected — we parse stdout.
    out = proc.stdout.strip()
    if not out:
        if proc.returncode not in (0, 1):
            raise RuntimeError(
                f"`npx @google/design.md lint` failed (exit {proc.returncode}). "
                f"Is Node/npx available? stderr: {proc.stderr.strip()[:300]}"
            )
        return []
    data = json.loads(out)
    # Accept {"findings": [...]} or a bare [...] array.
    return data.get("findings", data) if isinstance(data, dict) else data


def _emit(errors: list[str], warnings: list[str]) -> int:
    result = {
        "ok": not errors,
        "reasons": errors,          # detector contract: reasons populated on failure
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            print(f"PASS: {name}"); passed += 1
        else:
            print(f"FAIL: {name} {detail}"); failed += 1

    e, w = classify([{"rule": "missing-primary", "level": "warning", "message": "no primary"}])
    check("missing-primary is a hard error (our decision)", e and not w, f"e={e} w={w}")

    e, w = classify([{"rule": "broken-ref", "level": "error", "message": "{colors.nope}"}])
    check("broken-ref rejects", bool(e))

    e, w = classify([
        {"rule": "contrast-ratio", "level": "warning", "message": "AA fail"},
        {"rule": "orphaned-tokens", "level": "warning", "message": "unused"},
    ])
    check("warnings do not reject", (not e) and len(w) == 2, f"e={e} w={w}")

    e, w = classify([{"severity": "error", "ruleId": "duplicate-section", "msg": "two ## Colors"}])
    check("alt field names (severity/ruleId/msg)", bool(e))

    e, w = classify([])
    check("clean → no errors/warnings", not e and not w)

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED"); return 1
    print(f"\nAll {total} self-tests PASSED"); return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()

    path = next((a for a in args if not a.startswith("--")), None)
    if path is None:
        print("usage: validate_design_md.py <DESIGN.md>", file=sys.stderr)
        return 2
    try:
        findings = _lint_via_npx(path)
    except Exception as e:
        print(f"error linting DESIGN.md: {e}", file=sys.stderr)
        return 2
    errors, warnings = classify(findings)
    return _emit(errors, warnings)


if __name__ == "__main__":
    sys.exit(main())
