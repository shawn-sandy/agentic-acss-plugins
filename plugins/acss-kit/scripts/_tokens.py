"""
Shared token/CSS logic for tokens_to_css.py and css_to_tokens.py.

Internal module (_-prefix) — not a slash-command entry point.
Import via sys.path shim:
    import os, sys
    sys.path.insert(0, os.path.dirname(__file__))
    from _tokens import ROLE_GROUPS, format_palette, ...
"""
from __future__ import annotations

import re

# CSS selector constants used in both readers and writers.
LIGHT_SELECTOR = ":root"
DARK_SELECTOR = '[data-theme="dark"]'

# Canonical role definitions — single source of truth for names and order.
# Adding a role here automatically makes it visible to both the CSS writer
# (tokens_to_css.py) and the CSS reader (css_to_tokens.py).
ROLE_GROUPS: list[tuple[str, list[str]]] = [
    ("Backgrounds", [
        "--color-background",
        "--color-surface",
        "--color-surface-raised",
        "--color-surface-subtle",
    ]),
    ("Text", [
        "--color-text",
        "--color-text-muted",
        "--color-text-inverse",
        "--color-text-subtle",
    ]),
    ("Borders", ["--color-border", "--color-border-strong"]),
    ("Brand + semantic", [
        "--color-primary",
        "--color-primary-hover",
        "--color-success",
        "--color-warning",
        "--color-danger",
        "--color-info",
    ]),
    ("Focus", ["--color-focus-ring"]),
    ("Accent", ["--color-brand-accent"]),
]

# Flat set of every canonical role name (derived — do not edit directly).
ALL_ROLES: frozenset[str] = frozenset(r for _, roles in ROLE_GROUPS for r in roles)

# Roles that brand overlay files are allowed to override.
BRAND_ROLES: frozenset[str] = frozenset({
    "--color-primary",
    "--color-primary-hover",
    "--color-focus-ring",
    "--color-brand-accent",
})

# --- Internal regexes ---

_VAR_DECL_RE = re.compile(r"^\s*(--[a-z0-9-]+)\s*:\s*([^;]+);", re.IGNORECASE | re.MULTILINE)
_VAR_REF_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*(?:,\s*([^)]+))?\)")
_HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")
_SELECTOR_RE = re.compile(
    r'(:root|\[data-theme=["\']dark["\']\])\s*\{([^}]*)\}',
    re.DOTALL | re.IGNORECASE,
)


# --- Public helpers ---

def parse_vars(text: str) -> dict[str, str]:
    """Extract ``--name: value`` declarations from a CSS text block."""
    return {m.group(1): m.group(2).strip() for m in _VAR_DECL_RE.finditer(text)}


def resolve_hex(name: str, vars_: dict[str, str], depth: int = 3) -> str | None:
    """Follow var() chains and return the first hex value found, or None."""
    if depth < 0 or name not in vars_:
        return None
    raw = vars_[name]
    m = _HEX_RE.search(raw)
    if m:
        h = m.group(1)
        return "#" + (h if len(h) == 6 else "".join(c * 2 for c in h))
    m = _VAR_REF_RE.search(raw)
    if m:
        resolved = resolve_hex(m.group(1), vars_, depth - 1)
        if resolved:
            return resolved
        if m.group(2):
            fm = _HEX_RE.search(m.group(2))
            if fm:
                h = fm.group(1)
                return "#" + (h if len(h) == 6 else "".join(c * 2 for c in h))
    return None


def extract_selector_blocks(text: str) -> dict[str, str]:
    """Return ``{"light": block_text, "dark": block_text}`` from CSS source."""
    blocks: dict[str, str] = {}
    for m in _SELECTOR_RE.finditer(text):
        sel = m.group(1).strip()
        key = "dark" if "dark" in sel.lower() else "light"
        blocks[key] = blocks.get(key, "") + m.group(2)
    return blocks


def parse_palette_from_block(block: str) -> dict[str, str]:
    """Parse a CSS block into ``{role: hex}`` keeping only canonical roles."""
    vars_ = parse_vars(block)
    result: dict[str, str] = {}
    for name in ALL_ROLES:
        if name in vars_:
            resolved = resolve_hex(name, vars_)
            if resolved is not None:
                result[name] = resolved
    return result


def format_palette(palette: dict[str, str], selector: str, indent: str = "  ") -> str:
    """Render a palette dict as a CSS rule block ordered by ROLE_GROUPS."""
    lines = [f"{selector} {{"]
    for group_name, roles in ROLE_GROUPS:
        group_lines = [
            f"{indent}{role}: var({role}, {palette[role]});"
            for role in roles
            if role in palette
        ]
        if group_lines:
            lines.append(f"\n{indent}/* {group_name} */")
            lines.extend(group_lines)
    lines.append("}\n")
    return "\n".join(lines)
