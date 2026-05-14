#!/usr/bin/env python3
"""
Detect the component-output or utilities target for an acss-kit project.

Usage:
    python detect_target.py [--target=react|html] [project_root]
    python detect_target.py --what=utilities [project_root]
    python detect_target.py --self-test

--target defaults to "react". --what=utilities selects the utilities path.

--- React target ---

Resolution:
  1. "generated" — <componentsDir>/ui.tsx exists locally.
  2. "none"      — React project root found but ui.tsx absent, or no root at all.

componentsDir comes from .acss-target.json at project root, falling back to
"src/components/fpkit".

Output (--target=react):

    {
      "source": "generated",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "import Button from '../src/components/fpkit/button/button'",
      "reasons": []
    }

    Failure A — no React project root in path ancestors:
    {
      "source": "none",
      "projectRoot": null,
      "componentsDir": "src/components/fpkit",
      "importMapHint": "",
      "reasons": ["No project root containing react was found."]
    }

    Failure B — root found, ui.tsx absent (clean project):
    {
      "source": "none",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "",
      "reasons": [
        "No fpkit component source found.",
        "Vendor components via /kit-add to bootstrap <componentsDir>/ui.tsx."
      ]
    }

Exit code 0 = source detected, 1 = none.

--- HTML target ---

Intentionally framework-agnostic: any writable directory is a valid root,
including static-site projects with no package.json.

Resolution:
  1. "configured" — .acss-html-target.json exists at root with componentsHtmlDir.
  2. "none"       — config absent; first /kit-add --target=html run will prompt
                    and write it.

componentsHtmlDir defaults to "components/html" when no config is present.

Output (--target=html):

    {
      "source": "configured",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": true,
      "reasons": []
    }

    Configured but foundation (_stateful.js) not yet copied:
    {
      "source": "configured",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": false,
      "reasons": ["_stateful.js not yet copied — first /kit-add --target=html run will copy it."]
    }

    Not configured:
    {
      "source": "none",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": false,
      "reasons": [
        "No .acss-html-target.json found.",
        "First /kit-add --target=html run will prompt for componentsHtmlDir and write this file."
      ]
    }

Exit code 0 = configured, 1 = none.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _target import (
    DEFAULT_COMPONENTS_DIR,
    DEFAULT_HTML_DIR,
    DEFAULT_UTILITIES_DIR,
    find_project_root,
    read_components_dir,
    read_html_dir,
    read_json_config,
)

FOUNDATION_FILENAME = "_stateful.js"


# ---------------------------------------------------------------------------
# React target
# ---------------------------------------------------------------------------

def detect_react(start: Path) -> tuple[dict, int]:
    root = find_project_root(start)
    if root is None:
        return {
            "source": "none",
            "projectRoot": None,
            "componentsDir": DEFAULT_COMPONENTS_DIR,
            "importMapHint": "",
            "reasons": ["No project root containing react was found."],
        }, 1

    components_dir = read_components_dir(root)
    if (root / components_dir / "ui.tsx").is_file():
        return {
            "source": "generated",
            "projectRoot": str(root),
            "componentsDir": components_dir,
            "importMapHint": f"import Button from '../{components_dir}/button/button'",
            "reasons": [],
        }, 0

    return {
        "source": "none",
        "projectRoot": str(root),
        "componentsDir": components_dir,
        "importMapHint": "",
        "reasons": [
            "No fpkit component source found.",
            "Vendor components via /kit-add to bootstrap <componentsDir>/ui.tsx.",
        ],
    }, 1


# ---------------------------------------------------------------------------
# HTML target
# ---------------------------------------------------------------------------

def detect_html(start: Path) -> tuple[dict, int]:
    root = start
    components_html_dir, configured = read_html_dir(root)
    foundation_present = (root / components_html_dir / FOUNDATION_FILENAME).is_file()

    if configured:
        reasons: list[str] = []
        if not foundation_present:
            reasons.append(
                f"{FOUNDATION_FILENAME} not yet copied — first /kit-add "
                "--target=html run will copy it."
            )
        return {
            "source": "configured",
            "projectRoot": str(root),
            "componentsHtmlDir": components_html_dir,
            "foundationPresent": foundation_present,
            "reasons": reasons,
        }, 0

    return {
        "source": "none",
        "projectRoot": str(root),
        "componentsHtmlDir": components_html_dir,
        "foundationPresent": foundation_present,
        "reasons": [
            "No .acss-html-target.json found.",
            "First /kit-add --target=html run will prompt for componentsHtmlDir "
            "and write this file.",
        ],
    }, 1


# ---------------------------------------------------------------------------
# Utilities target
# ---------------------------------------------------------------------------

def detect_utilities(start: Path) -> tuple[dict, int]:
    """Detect the drop directory for utilities.css and token-bridge.css.

    Resolution order:
      1. "configured" — .acss-target.json#utilitiesDir points at an existing dir.
      2. "default"    — React root found; fall back to DEFAULT_UTILITIES_DIR.
      3. "none"       — No React project root found.
    """
    root = find_project_root(start)
    if root is None:
        return {
            "source": "none",
            "projectRoot": None,
            "utilitiesDir": DEFAULT_UTILITIES_DIR,
            "bundlePath": "",
            "bridgePath": "",
            "reasons": ["No project root containing react was found."],
        }, 1

    data = read_json_config(root / ".acss-target.json")
    cd = data.get("utilitiesDir")
    if isinstance(cd, str) and cd.strip() and (root / cd.strip()).is_dir():
        utilities_dir, source = cd.strip(), "configured"
    else:
        utilities_dir, source = DEFAULT_UTILITIES_DIR, "default"

    return {
        "source": source,
        "projectRoot": str(root),
        "utilitiesDir": utilities_dir,
        "bundlePath": f"{utilities_dir}/utilities.css",
        "bridgePath": f"{utilities_dir}/token-bridge.css",
        "reasons": [],
    }, 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, fn, expect_source: str, **kwargs) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            result, _ = fn(root)
            ok = result["source"] == expect_source
            for key, val in kwargs.items():
                ok = ok and result.get(key) == val
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(f"FAIL: {name} — {result}")
                failed += 1

    # React tests
    run(
        "react — no package.json → none (null root)",
        {},
        detect_react,
        "none",
    )
    run(
        "react — package.json without react → none",
        {"package.json": json.dumps({"dependencies": {}})},
        detect_react,
        "none",
    )
    run(
        "react — package.json with react, no ui.tsx → none",
        {"package.json": json.dumps({"dependencies": {"react": "^18"}})},
        detect_react,
        "none",
    )
    run(
        "react — ui.tsx present → generated",
        {
            "package.json": json.dumps({"dependencies": {"react": "^18"}}),
            "src/components/fpkit/ui.tsx": "// stub\n",
        },
        detect_react,
        "generated",
    )
    run(
        "react — custom componentsDir via .acss-target.json → generated",
        {
            "package.json": json.dumps({"dependencies": {"react": "^18"}}),
            ".acss-target.json": json.dumps({"componentsDir": "src/ui/fpkit"}),
            "src/ui/fpkit/ui.tsx": "// stub\n",
        },
        detect_react,
        "generated",
    )

    # HTML tests
    run(
        "html — no config → none",
        {},
        detect_html,
        "none",
    )
    run(
        "html — config, no foundation → configured + warning",
        {".acss-html-target.json": json.dumps({"componentsHtmlDir": "public/snippets"})},
        detect_html,
        "configured",
        foundationPresent=False,
    )
    run(
        "html — config + foundation → configured clean",
        {
            ".acss-html-target.json": json.dumps({"componentsHtmlDir": "public/snippets"}),
            f"public/snippets/{FOUNDATION_FILENAME}": "// stub\n",
        },
        detect_html,
        "configured",
        foundationPresent=True,
    )
    run(
        "html — malformed config → none",
        {".acss-html-target.json": "not valid json{"},
        detect_html,
        "none",
    )
    run(
        "html — empty componentsHtmlDir → none",
        {".acss-html-target.json": json.dumps({"componentsHtmlDir": ""})},
        detect_html,
        "none",
    )

    # Utilities tests
    run(
        "utilities — no package.json → none",
        {},
        detect_utilities,
        "none",
    )
    run(
        "utilities — react found, no utilitiesDir in target → default",
        {"package.json": json.dumps({"dependencies": {"react": "^18"}})},
        detect_utilities,
        "default",
        utilitiesDir=DEFAULT_UTILITIES_DIR,
    )
    run(
        "utilities — configured utilitiesDir exists → configured",
        {
            "package.json": json.dumps({"dependencies": {"react": "^18"}}),
            ".acss-target.json": json.dumps({"utilitiesDir": "src/styles"}),
            "src/styles/.keep": "",
        },
        detect_utilities,
        "configured",
        utilitiesDir="src/styles",
    )
    run(
        "utilities — configured utilitiesDir missing on disk → default",
        {
            "package.json": json.dumps({"dependencies": {"react": "^18"}}),
            ".acss-target.json": json.dumps({"utilitiesDir": "src/styles"}),
        },
        detect_utilities,
        "default",
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = sys.argv[1:]

    if "--self-test" in args:
        return self_test()

    what = None
    target = "react"
    positional: list[str] = []
    for a in args:
        if a.startswith("--what="):
            what = a.split("=", 1)[1].strip().lower()
        elif a.startswith("--target="):
            target = a.split("=", 1)[1].strip().lower()
        else:
            positional.append(a)

    start = Path(positional[0]).resolve() if positional else Path.cwd()

    if what == "utilities":
        result, code = detect_utilities(start)
        print(json.dumps(result, indent=2))
        return code

    if target not in ("react", "html"):
        print("Usage: detect_target.py [--target=react|html|] [--what=utilities] [project_root]",
              file=sys.stderr)
        return 2

    if target == "react":
        result, code = detect_react(start)
    else:
        result, code = detect_html(start)

    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
