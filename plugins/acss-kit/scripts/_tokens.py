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
            f"{indent}{role}: {palette[role]};"
            for role in roles
            if role in palette
        ]
        if group_lines:
            lines.append(f"\n{indent}/* {group_name} */")
            lines.extend(group_lines)
    lines.append("}\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Non-color token kinds (DESIGN.md parity: spacing, rounded, typography).
#
# These are MODE-INDEPENDENT (no light/dark split) — a single :root block.
# JSON group keys mirror DESIGN.md (`spacing`, `rounded`, `typography`); the
# emitted CSS custom-property prefixes mirror the Tailwind v4 @theme namespaces
# (`--space-*`, `--radius-*`, `--font-*`) so a DESIGN.md `css-tailwind` export
# remaps mechanically. Adding a default here makes it visible to the writer
# (tokens_to_css.py) and the reader (css_to_tokens.py) alike.
# ---------------------------------------------------------------------------

SPACE_PREFIX = "--space-"
RADIUS_PREFIX = "--radius-"
FONT_PREFIX = "--font-"

# JSON group key -> (css prefix, comment) for the two dimension scales.
SCALE_KINDS: dict[str, tuple[str, str]] = {
    "spacing": (SPACE_PREFIX, "Spacing"),
    "rounded": (RADIUS_PREFIX, "Radius"),
}

# Default scales — a sane fallback for projects with no DESIGN.md.
SPACE_SCALE: dict[str, str] = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "2xl": "3rem",
}
RADIUS_SCALE: dict[str, str] = {
    "none": "0",
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "1rem",
    "xl": "1.5rem",
    "full": "9999px",
}

# Typography composite sub-properties, in emit order. Key is the JSON sub-key;
# the CSS custom property is `--font-<role>-<key>`.
TYPO_SUBPROPS: tuple[str, ...] = ("family", "size", "weight", "line", "tracking")

# Default typography roles (DESIGN.md-recommended names).
DEFAULT_TYPOGRAPHY: dict[str, dict[str, str]] = {
    "headline-lg": {"family": "system-ui, sans-serif", "size": "2rem", "weight": "700", "line": "1.2"},
    "headline-md": {"family": "system-ui, sans-serif", "size": "1.5rem", "weight": "700", "line": "1.25"},
    "body-lg": {"family": "system-ui, sans-serif", "size": "1.125rem", "weight": "400", "line": "1.6"},
    "body-md": {"family": "system-ui, sans-serif", "size": "1rem", "weight": "400", "line": "1.5"},
    "body-sm": {"family": "system-ui, sans-serif", "size": "0.875rem", "weight": "400", "line": "1.5"},
    "label-md": {"family": "system-ui, sans-serif", "size": "0.875rem", "weight": "600", "line": "1.4", "tracking": "0.01em"},
    "label-sm": {"family": "system-ui, sans-serif", "size": "0.75rem", "weight": "500", "line": "1.3", "tracking": "0.02em"},
}


def resolve_fallback(raw: str) -> str:
    """Return the ``var(--x, <fallback>)`` fallback if present, else the raw value."""
    m = _VAR_REF_RE.search(raw)
    if m and m.group(2):
        return m.group(2).strip()
    return raw.strip()


def format_scales(
    scales: list[tuple[str, str, dict[str, str]]],
    selector: str = LIGHT_SELECTOR,
    indent: str = "  ",
) -> str:
    """Render one or more dimension scales into a single :root block.

    ``scales`` is a list of ``(comment, css_prefix, {name: value})`` tuples.
    Each value is emitted as a raw definition ``<prefix><name>: <value>;`` —
    consumers add the ``var(--token, <fallback>)`` read. (A self-referential
    definition like ``var(--x, --x)`` would be a CSS cycle → guaranteed-invalid,
    so token files must define raw values.)
    """
    lines = [f"{selector} {{"]
    for comment, prefix, mapping in scales:
        group_lines = [
            f"{indent}{prefix}{name}: {value};"
            for name, value in mapping.items()
        ]
        if group_lines:
            lines.append(f"\n{indent}/* {comment} */")
            lines.extend(group_lines)
    lines.append("}\n")
    return "\n".join(lines)


def format_typography(
    typography: dict[str, dict[str, str]],
    selector: str = LIGHT_SELECTOR,
    indent: str = "  ",
) -> str:
    """Render typography composites as flattened ``--font-<role>-<sub>`` props."""
    lines = [f"{selector} {{"]
    for role, sub in typography.items():
        role_lines = [
            f"{indent}{FONT_PREFIX}{role}-{key}: {sub[key]};"
            for key in TYPO_SUBPROPS
            if key in sub
        ]
        if role_lines:
            lines.append(f"\n{indent}/* {role} */")
            lines.extend(role_lines)
    lines.append("}\n")
    return "\n".join(lines)


def parse_scale_from_block(block: str, prefix: str) -> dict[str, str]:
    """Parse ``<prefix><name>: <value>;`` declarations into ``{name: value}``."""
    out: dict[str, str] = {}
    for name, raw in parse_vars(block).items():
        if name.startswith(prefix):
            out[name[len(prefix):]] = resolve_fallback(raw)
    return out


def parse_typography_from_block(block: str) -> dict[str, dict[str, str]]:
    """Parse ``--font-<role>-<sub>`` declarations into ``{role: {sub: value}}``."""
    out: dict[str, dict[str, str]] = {}
    for name, raw in parse_vars(block).items():
        if not name.startswith(FONT_PREFIX):
            continue
        rest = name[len(FONT_PREFIX):]
        if "-" not in rest:
            continue
        role, sub = rest.rsplit("-", 1)
        if sub not in TYPO_SUBPROPS:
            continue
        out.setdefault(role, {})[sub] = resolve_fallback(raw)
    return out
