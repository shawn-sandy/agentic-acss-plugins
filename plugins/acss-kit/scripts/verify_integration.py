#!/usr/bin/env python3
"""
Verify that acss-kit artifacts are properly wired into the user's project.

Usage:
    python verify_integration.py [--target=react|html] [project_root]
    python verify_integration.py --self-test

--target defaults to "react".

--- React target ---

Detector contract: read-only, JSON to stdout, exit 0 when every wired-up
artifact is imported, exit 1 with populated `reasons` array otherwise.

Reads .acss-target.json for componentsDir, utilitiesDir, and
stack.entrypointFile. Then, for each artifact that exists on disk, checks
whether it is imported (by basename) in the entrypoint. Bridge ordering
relative to utilities.css is line-number compared.

Output (--target=react):

    All wired up:
    {
      "ok": true,
      "projectRoot": "/abs/path",
      "entrypointFile": "src/main.tsx",
      "checks": [
        {"artifact": "token-bridge.css", "imported": true},
        {"artifact": "utilities.css",    "imported": true},
        {"artifact": "light.css",        "imported": true}
      ],
      "reasons": []
    }

    Missing wires:
    {
      "ok": false,
      ...
      "reasons": [
        "token-bridge.css written to src/styles/ but not imported in src/main.tsx",
        "utilities.css imported but appears before token-bridge.css — bridge must load first."
      ]
    }

--- HTML target ---

Reads .acss-html-target.json for componentsHtmlDir. For each generated file
under that directory:

    - *.scss / *.css  → expect a <link rel="stylesheet"> or @import
    - *.js            → expect a <script src="..."> reference
    - *.html          → content fragments, not checked (listed as kind=snippet)

Output (--target=html):

    All wired up:
    {
      "ok": true,
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "checks": [
        {"artifact": "button.scss", "kind": "style",   "imported": true},
        {"artifact": "dialog.js",   "kind": "script",  "imported": true},
        {"artifact": "button.html", "kind": "snippet", "imported": null}
      ],
      "reasons": []
    }

Exit code 0 = ok, 1 = issues found.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))
from _target import (
    DEFAULT_COMPONENTS_DIR,
    DEFAULT_HTML_DIR,
    DEFAULT_UTILITIES_DIR,
    find_import_line,
    find_project_root,
    iter_page_files,
    read_html_dir,
    read_json_config,
)


# ---------------------------------------------------------------------------
# React target helpers
# ---------------------------------------------------------------------------

def _read_react_target(root: Path) -> dict:
    return read_json_config(root / ".acss-target.json")


def _find_any_use(root: Path, components_dir: str) -> bool:
    """Return True if any *.tsx/*.ts/*.jsx/*.js under src/ imports from componentsDir."""
    src = root / "src"
    if not src.is_dir():
        return False

    normalized = components_dir.replace("\\", "/").strip().strip("/")
    if not normalized:
        return False

    candidates: set[str] = {normalized, f"{normalized}/"}
    if normalized.startswith("src/"):
        rel = normalized[len("src/"):]
        if rel:
            candidates.add(rel)
            candidates.add(f"{rel}/")

    for ext in ("*.tsx", "*.ts", "*.jsx", "*.js"):
        for path in src.rglob(ext):
            try:
                txt = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for line in txt.splitlines():
                stripped = line.strip().replace("\\", "/")
                if not (stripped.startswith("import") or stripped.startswith("require(")):
                    continue
                if any(candidate in stripped for candidate in candidates):
                    return True
    return False


def verify_react(root: Path) -> dict:
    target = _read_react_target(root)
    components_dir = target.get("componentsDir") or DEFAULT_COMPONENTS_DIR
    utilities_dir = target.get("utilitiesDir") or DEFAULT_UTILITIES_DIR
    stack = target.get("stack") or {}
    entrypoint_rel = stack.get("entrypointFile")
    css_entry_rel = stack.get("cssEntryFile")

    checks: list[dict] = []
    reasons: list[str] = []

    if not entrypoint_rel:
        return {
            "ok": False,
            "projectRoot": str(root),
            "entrypointFile": None,
            "checks": checks,
            "reasons": [
                "stack.entrypointFile not set in .acss-target.json — run detect_stack.py and persist its result first."
            ],
        }

    entrypoint_path = root / entrypoint_rel
    if not entrypoint_path.is_file():
        return {
            "ok": False,
            "projectRoot": str(root),
            "entrypointFile": entrypoint_rel,
            "checks": checks,
            "reasons": [
                f"Entrypoint {entrypoint_rel} does not exist — re-run detect_stack.py."
            ],
        }

    entry_text = entrypoint_path.read_text(encoding="utf-8", errors="ignore")

    css_entry_text = ""
    css_entry_missing = False
    if css_entry_rel:
        css_entry_path = root / css_entry_rel
        if css_entry_path.is_file():
            css_entry_text = css_entry_path.read_text(encoding="utf-8", errors="ignore")
        else:
            css_entry_missing = True
            reasons.append(
                f"stack.cssEntryFile points at {css_entry_rel} but that file does not exist — "
                f"re-run /setup or remove the stale cssEntryFile entry from .acss-target.json."
            )

    def find_in_any(basename: str) -> Optional[tuple[str, int]]:
        line = find_import_line(entry_text, basename)
        if line is not None:
            return (entrypoint_rel, line)
        if css_entry_text:
            line = find_import_line(css_entry_text, basename)
            if line is not None:
                return (css_entry_rel, line)
        return None

    def imported_anywhere(basename: str) -> bool:
        return find_in_any(basename) is not None

    def relpath_from(importer_rel: str, artifact_path: Path) -> str:
        importer_dir = (root / importer_rel).parent
        rel = os.path.relpath(artifact_path, importer_dir).replace(os.sep, "/")
        if not rel.startswith(".") and not rel.startswith("/"):
            rel = f"./{rel}"
        return rel

    def import_fixup_hint(artifact_path: Path) -> str:
        hints = [
            f"{entrypoint_rel}: import '{relpath_from(entrypoint_rel, artifact_path)}';"
        ]
        if css_entry_rel and not css_entry_missing:
            hints.append(
                f"{css_entry_rel}: @import \"{relpath_from(css_entry_rel, artifact_path)}\";"
            )
        return " or ".join(hints)

    bridge_path = root / utilities_dir / "token-bridge.css"
    utilities_path = root / utilities_dir / "utilities.css"
    bridge_hit: Optional[tuple[str, int]] = None
    utilities_hit: Optional[tuple[str, int]] = None

    in_files = entrypoint_rel
    if css_entry_rel and not css_entry_missing:
        in_files = f"{entrypoint_rel} or {css_entry_rel}"

    if bridge_path.is_file():
        bridge_hit = find_in_any("token-bridge.css")
        imported = bridge_hit is not None
        checks.append({"artifact": "token-bridge.css", "imported": imported})
        if not imported:
            reasons.append(
                f"token-bridge.css written to {utilities_dir}/ but not imported in "
                f"{in_files} — add {import_fixup_hint(bridge_path)}"
            )

    if utilities_path.is_file():
        utilities_hit = find_in_any("utilities.css")
        imported = utilities_hit is not None
        checks.append({"artifact": "utilities.css", "imported": imported})
        if not imported:
            reasons.append(
                f"utilities.css written to {utilities_dir}/ but not imported in "
                f"{in_files} — add {import_fixup_hint(utilities_path)}"
            )

    if (
        bridge_hit is not None
        and utilities_hit is not None
        and bridge_hit[0] == utilities_hit[0]
        and utilities_hit[1] < bridge_hit[1]
    ):
        reasons.append(
            f"utilities.css is imported before token-bridge.css in {bridge_hit[0]} — the bridge "
            "must load first or utility classes will reference undefined CSS variables."
        )

    theme_files = []
    for candidate in ("light.css", "dark.css"):
        for base in (
            root / "src" / "styles" / "theme" / candidate,
            root / "src" / "styles" / candidate,
            root / "src" / candidate,
            root / utilities_dir / candidate,
        ):
            if base.is_file():
                theme_files.append((candidate, base))
                break
    if theme_files:
        any_imported = any(imported_anywhere(name) for name, _ in theme_files)
        checks.append({"artifact": "theme css", "imported": any_imported})
        if not any_imported:
            names = ", ".join(sorted({name for name, _ in theme_files}))
            reasons.append(
                f"Theme files present ({names}) but no theme CSS imported in {in_files}."
            )

    ui_path = root / components_dir / "ui.tsx"
    if ui_path.is_file():
        used = _find_any_use(root, components_dir)
        checks.append({"artifact": f"{components_dir}/ui.tsx", "imported": used})
        if not used:
            reasons.append(
                f"{components_dir}/ui.tsx is vendored but no source file under src/ references "
                f"{components_dir} — components are not yet wired into the app."
            )

    return {
        "ok": not reasons,
        "projectRoot": str(root),
        "entrypointFile": entrypoint_rel,
        "cssEntryFile": css_entry_rel,
        "checks": checks,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# HTML target helpers
# ---------------------------------------------------------------------------

_REFERENCE_TOKENS = (
    "<link",
    "<script",
    "@import",
    "@use",
    "@forward",
    "import",
    "require(",
    "url(",
)


def _is_referenced(basename: str, pages: list[Path]) -> bool:
    needle = basename
    window = 256
    for page in pages:
        try:
            text = page.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lower = text.lower()
        start = 0
        while True:
            idx = text.find(needle, start)
            if idx == -1:
                break
            window_start = max(0, idx - window)
            preceding = lower[window_start:idx]
            if any(token in preceding for token in _REFERENCE_TOKENS):
                return True
            start = idx + len(needle)
    return False


def _classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".scss", ".css", ".sass"):
        return "style"
    if suffix in (".js", ".mjs"):
        return "script"
    if suffix in (".html", ".htm"):
        return "snippet"
    return "other"


def verify_html(root: Path) -> dict:
    components_html_dir, configured = read_html_dir(root)

    configured_path = Path(components_html_dir)
    if configured_path.is_absolute() or ".." in configured_path.parts:
        return {
            "ok": False,
            "projectRoot": str(root),
            "componentsHtmlDir": components_html_dir,
            "checks": [],
            "reasons": [
                "componentsHtmlDir must be a project-relative path "
                "(no leading '/' and no '..' segments).",
            ],
        }

    artifacts_dir = root / configured_path
    if not artifacts_dir.is_dir():
        return {
            "ok": False,
            "projectRoot": str(root),
            "componentsHtmlDir": components_html_dir,
            "checks": [],
            "reasons": [
                f"componentsHtmlDir {components_html_dir} does not exist — "
                "run /kit-add --target=html first."
            ],
        }

    pages = [p for p in iter_page_files(root)
             if not p.is_relative_to(artifacts_dir)]

    checks: list[dict] = []
    reasons: list[str] = []

    for artifact in sorted(artifacts_dir.rglob("*")):
        if not artifact.is_file():
            continue
        if artifact.name == "_stateful.js":
            continue
        kind = _classify(artifact)
        if kind == "snippet":
            checks.append({"artifact": artifact.name, "kind": kind, "imported": None})
            continue
        if kind == "other":
            continue

        candidates = [artifact.name]
        if kind == "style" and artifact.suffix.lower() in (".scss", ".sass"):
            candidates.append(artifact.with_suffix(".css").name)
        imported = any(_is_referenced(name, pages) for name in candidates)
        checks.append({"artifact": artifact.name, "kind": kind, "imported": imported})
        if not imported:
            ref_path = f"{components_html_dir}/{artifact.name}"
            if kind == "style":
                if artifact.suffix.lower() in (".scss", ".sass"):
                    compiled_path = ref_path.rsplit(".", 1)[0] + ".css"
                    hint = (
                        f'compile {ref_path} with Sass and add '
                        f'<link rel="stylesheet" href="{compiled_path}">, '
                        f'or @import "{ref_path}" from your existing Sass '
                        "entrypoint"
                    )
                else:
                    hint = f'<link rel="stylesheet" href="{ref_path}">'
            else:
                hint = f'<script type="module" src="{ref_path}"></script>'
            reasons.append(
                f"{artifact.name} not referenced by any page under {root.name}/ "
                f"— add: {hint}"
            )

    return {
        "ok": not reasons,
        "projectRoot": str(root),
        "componentsHtmlDir": components_html_dir,
        "checks": checks,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, fn, expect_ok: bool,
            expect_reason_substr: Optional[str] = None, **kwargs) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            result = fn(root)
            ok = result["ok"] == expect_ok
            if expect_reason_substr is not None:
                ok = ok and any(expect_reason_substr in r for r in result["reasons"])
            for key, val in kwargs.items():
                ok = ok and result.get(key) == val
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(f"FAIL: {name} — ok={result['ok']!r} reasons={result['reasons']!r}")
                failed += 1

    pkg = '{"name":"t","dependencies":{"react":"18"}}'
    target_with_entry = json.dumps({
        "componentsDir": "src/components/fpkit",
        "utilitiesDir": "src/styles",
        "stack": {"entrypointFile": "src/main.tsx"},
    })

    # React tests
    run(
        "react — missing entrypointFile in target",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({"componentsDir": "src/components/fpkit"}),
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="stack.entrypointFile not set",
    )
    run(
        "react — bridge written but not imported",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "console.log('no imports')\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="token-bridge.css",
    )
    run(
        "react — bridge imported, no other artifacts",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "import './styles/token-bridge.css';\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=True,
    )
    run(
        "react — utilities imported before bridge → ordering reason",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": (
                "import './styles/utilities.css';\n"
                "import './styles/token-bridge.css';\n"
            ),
            "src/styles/token-bridge.css": ":root{}",
            "src/styles/utilities.css": ".m-1{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="bridge must load first",
    )
    run(
        "react — ui.tsx vendored but never used",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "console.log('hi')\n",
            "src/components/fpkit/ui.tsx": "export const UI = {};",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="ui.tsx is vendored",
    )
    run(
        "react — ui.tsx used in a feature file",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "import App from './app';\n",
            "src/app.tsx": "import { UI } from './components/fpkit/ui';\n",
            "src/components/fpkit/ui.tsx": "export const UI = {};",
        },
        verify_react,
        expect_ok=True,
    )
    run(
        "react — find_any_use rejects bare-segment false positive",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "// docs reference: see fpkit upstream\n",
            "src/components/fpkit/ui.tsx": "export const UI = {};",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="ui.tsx is vendored",
    )
    run(
        "react — bridge imported via SCSS cssEntryFile counts as wired",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "import './styles/index.scss';\n",
            "src/styles/index.scss": "@import \"./token-bridge.css\";\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=True,
    )
    run(
        "react — ordering check fires inside cssEntryFile",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "import './styles/index.scss';\n",
            "src/styles/index.scss": (
                "@import \"./utilities.css\";\n"
                "@import \"./token-bridge.css\";\n"
            ),
            "src/styles/token-bridge.css": ":root{}",
            "src/styles/utilities.css": ".m-1{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="bridge must load first",
    )
    run(
        "react — split bridge/utilities across files → no ordering reason",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": (
                "import './styles/token-bridge.css';\n"
                "import './styles/index.scss';\n"
            ),
            "src/styles/index.scss": "@import \"./utilities.css\";\n",
            "src/styles/token-bridge.css": ":root{}",
            "src/styles/utilities.css": ".m-1{}",
        },
        verify_react,
        expect_ok=True,
    )
    run(
        "react — fixup hint names cssEntryFile with @import syntax",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "console.log('hi');\n",
            "src/styles/index.scss": "body { margin: 0; }\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="src/styles/index.scss: @import \"./token-bridge.css\";",
    )
    run(
        "react — cssEntryFile configured but missing → explicit reason",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "import './styles/token-bridge.css';\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="stack.cssEntryFile points at src/styles/index.scss but that file does not exist",
    )
    run(
        "react — theme imported via cssEntryFile counts as wired",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "import './styles/index.scss';\n",
            "src/styles/index.scss": (
                "@import \"./theme/light.css\";\n"
                "@import \"./theme/dark.css\";\n"
            ),
            "src/styles/theme/light.css": ":root{}",
            "src/styles/theme/dark.css": ":root{}",
        },
        verify_react,
        expect_ok=True,
    )
    run(
        "react — theme files present but not imported in either entry",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {
                    "entrypointFile": "src/main.tsx",
                    "cssEntryFile": "src/styles/index.scss",
                },
            }),
            "src/main.tsx": "console.log('hi');\n",
            "src/styles/index.scss": "body { margin: 0; }\n",
            "src/styles/theme/light.css": ":root{}",
            "src/styles/theme/dark.css": ":root{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="src/main.tsx or src/styles/index.scss",
    )
    run(
        "react — Next-style entrypoint outside src/: relpath suggestion is correct",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({
                "componentsDir": "src/components/fpkit",
                "utilitiesDir": "src/styles",
                "stack": {"entrypointFile": "app/layout.tsx"},
            }),
            "app/layout.tsx": "export default function L(){return null}\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        verify_react,
        expect_ok=False,
        expect_reason_substr="../src/styles/token-bridge.css",
    )

    # HTML tests
    html_cfg = json.dumps({"componentsHtmlDir": "components/html"})

    run(
        "html — componentsHtmlDir missing → reason explains why",
        {".acss-html-target.json": html_cfg},
        verify_html,
        expect_ok=False,
        expect_reason_substr="does not exist",
    )
    run(
        "html — componentsHtmlDir as a non-string (list) → falls back to default",
        {".acss-html-target.json": json.dumps({"componentsHtmlDir": ["unexpected"]})},
        verify_html,
        expect_ok=False,
        expect_reason_substr="components/html does not exist",
    )
    run(
        "html — config JSON is a top-level array → treated as empty",
        {".acss-html-target.json": "[1, 2, 3]"},
        verify_html,
        expect_ok=False,
        expect_reason_substr="components/html does not exist",
    )
    run(
        "html — config JSON is a top-level string → treated as empty",
        {".acss-html-target.json": '"components/html"'},
        verify_html,
        expect_ok=False,
        expect_reason_substr="components/html does not exist",
    )
    run(
        "html — absolute componentsHtmlDir is rejected",
        {".acss-html-target.json": json.dumps({"componentsHtmlDir": "/etc/passwd"})},
        verify_html,
        expect_ok=False,
        expect_reason_substr="must be a project-relative path",
    )
    run(
        "html — traversal segment in componentsHtmlDir is rejected",
        {".acss-html-target.json": json.dumps({"componentsHtmlDir": "../../escape"})},
        verify_html,
        expect_ok=False,
        expect_reason_substr="must be a project-relative path",
    )
    run(
        "html — stylesheet linked from index.html → ok",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "index.html": (
                "<!doctype html><html><head>"
                '<link rel="stylesheet" href="components/html/button.scss">'
                "</head></html>"
            ),
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — stylesheet not linked anywhere → reason w/ <link> hint",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "index.html": "<!doctype html><html></html>",
        },
        verify_html,
        expect_ok=False,
        expect_reason_substr='<link rel="stylesheet"',
    )
    run(
        "html — script wired via <script src> → ok",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/dialog.js": "export {}",
            "index.html": (
                '<!doctype html><html><body>'
                '<script type="module" src="components/html/dialog.js"></script>'
                '</body></html>'
            ),
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — script not wired → reason w/ <script> hint",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/dialog.js": "export {}",
            "index.html": "<!doctype html><html></html>",
        },
        verify_html,
        expect_ok=False,
        expect_reason_substr='<script type="module"',
    )
    run(
        "html — *.html snippets are not checked for inclusion",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.html": "<button class=\"btn\"></button>",
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — _stateful.js is excluded from checks",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/_stateful.js": "export const wireDisabled = ()=>{};",
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — stylesheet linked via @import in user SCSS counts as wired",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "src/styles/main.scss": '@import "../../components/html/button.scss";',
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — multi-line <script src=...> counts as wired",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/dialog.js": "export {}",
            "index.html": (
                "<!doctype html><html><body>\n"
                "<script\n"
                '  type="module"\n'
                '  src="components/html/dialog.js"\n'
                "></script>\n"
                "</body></html>\n"
            ),
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — ES-module bootstrap importing the artifact counts as wired",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/dialog.js": "export {}",
            "src/main.js": "import './components/html/dialog.js';\n",
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — .scss fix-up hint mentions Sass compilation",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "index.html": "<!doctype html><html></html>",
        },
        verify_html,
        expect_ok=False,
        expect_reason_substr="compile components/html/button.scss with Sass",
    )
    run(
        "html — page links compiled .css → satisfies the .scss artifact",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "index.html": (
                "<!doctype html><html><head>"
                '<link rel="stylesheet" href="components/html/button.css">'
                "</head></html>"
            ),
        },
        verify_html,
        expect_ok=True,
    )
    run(
        "html — node_modules copy of artifact does not count",
        {
            ".acss-html-target.json": html_cfg,
            "components/html/button.scss": ".btn{}",
            "node_modules/old/index.html": (
                '<link rel="stylesheet" href="components/html/button.scss">'
            ),
        },
        verify_html,
        expect_ok=False,
        expect_reason_substr="button.scss not referenced",
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

    target = "react"
    positional: list[str] = []
    for a in args:
        if a.startswith("--target="):
            target = a.split("=", 1)[1].strip().lower()
        else:
            positional.append(a)

    if target not in ("react", "html"):
        print("Usage: verify_integration.py [--target=react|html] [project_root]",
              file=sys.stderr)
        return 2

    start = Path(positional[0]).resolve() if positional else Path.cwd()

    if target == "react":
        root = find_project_root(start)
        if root is None:
            print(json.dumps({
                "ok": False,
                "projectRoot": None,
                "entrypointFile": None,
                "checks": [],
                "reasons": ["No project root containing react was found."],
            }, indent=2))
            return 1
        result = verify_react(root)
    else:
        result = verify_html(start)

    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
