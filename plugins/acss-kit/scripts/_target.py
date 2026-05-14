"""
Shared detection utilities for acss-kit scripts.

Internal module — not a slash-command entry point. Import via sys.path shim:

    import os, sys
    sys.path.insert(0, os.path.dirname(__file__))
    from _target import find_project_root, read_components_dir, ...
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_COMPONENTS_DIR = "src/components/fpkit"
DEFAULT_HTML_DIR = "components/html"
DEFAULT_UTILITIES_DIR = "src/styles"

SKIP_DIRS = frozenset({
    "node_modules", "dist", "build", ".git", ".next", ".cache", "out",
})

PAGE_EXTENSIONS = frozenset({
    ".html", ".htm", ".css", ".scss", ".sass", ".vue", ".svelte",
    ".njk", ".liquid", ".erb", ".php", ".js", ".mjs", ".cjs",
    ".jsx", ".ts", ".tsx", ".astro", ".md", ".mdx",
})

_IMPORT_PREFIXES: tuple[str, ...] = ("import", "require(", "@import", "@use", "@forward")


# ---------------------------------------------------------------------------
# Project-root detection
# ---------------------------------------------------------------------------

def find_project_root(start: Path) -> Optional[Path]:
    """Walk ancestors to find the closest package.json that declares react."""
    cur = start.resolve()
    while True:
        pkg = cur / "package.json"
        if pkg.is_file():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps:
                    return cur
            except Exception:
                pass
        if cur.parent == cur:
            return None
        cur = cur.parent


# ---------------------------------------------------------------------------
# Config-file readers
# ---------------------------------------------------------------------------

def read_json_config(path: Path) -> dict:
    """Return parsed JSON from *path*, or {} on any error."""
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def read_components_dir(root: Path) -> str:
    """Return componentsDir from .acss-target.json, falling back to default."""
    data = read_json_config(root / ".acss-target.json")
    cd = data.get("componentsDir")
    return cd.strip() if isinstance(cd, str) and cd.strip() else DEFAULT_COMPONENTS_DIR


def read_html_dir(root: Path) -> tuple[str, bool]:
    """Return (componentsHtmlDir, configured).

    configured=True when .acss-html-target.json exists with a valid
    componentsHtmlDir value; False otherwise (default dir is still returned).
    """
    data = read_json_config(root / ".acss-html-target.json")
    chd = data.get("componentsHtmlDir")
    if isinstance(chd, str) and chd.strip():
        return chd.strip(), True
    return DEFAULT_HTML_DIR, False


# ---------------------------------------------------------------------------
# Import-line scanning (shared by both verify scripts)
# ---------------------------------------------------------------------------

def find_import_line(text: str, basename: str) -> Optional[int]:
    """Return the 1-based line number of the first import line referencing
    *basename* in *text*, or None if absent.

    Recognises JS/TS (import, require()) and Sass (@import, @use, @forward).
    """
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if not any(stripped.startswith(p) for p in _IMPORT_PREFIXES):
            continue
        if basename in stripped:
            return idx
    return None


def iter_page_files(root: Path):
    """Yield every source/page file under *root*, skipping build/dep dirs."""
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() in PAGE_EXTENSIONS:
            yield p
