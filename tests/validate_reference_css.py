#!/usr/bin/env python3
"""Syntax-check every fenced CSS block in the style-agent css references.

Walks the directory (or single file) passed as argv[1] — defaulting to
plugins/style-agent/skills/css/references/ — extracts every fenced code
block from each markdown file, then asserts:

  - Every ```css fence tokenizes without a parse error. tinycss2 parses
    the block as a stylesheet and the result is walked recursively so
    errors nested inside a rule's prelude or block (an unmatched brace,
    a bad string or URL token) are caught too.
  - No ```scss fence exists at all. The css skill's references are
    plain-CSS-only by decision, so an scss fence is a failure regardless
    of whether it parses.

This is a tokenizer-level syntax gate, not a correctness gate. tinycss2
will happily accept an invalid `container-type` keyword or a `:has()`
containing a pseudo-element — the prose assertions in the reference
files themselves remain the real check on the gotcha claims.

Output contract: generator/validator style — human-readable results to
stdout, errors to stderr, exit 0 on success, 1 on validation failure and
2 on usage / setup errors. Mirrors validate_extracted_scss.py.
"""

import re
import sys
from pathlib import Path

try:
    import tinycss2
except ImportError:
    print(
        "tinycss2 not installed: run `pip3 install --user tinycss2`",
        file=sys.stderr,
    )
    sys.exit(2)


DEFAULT_TARGET = "plugins/style-agent/skills/css/references"

FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)\s*$")


def extract_fences(content: str):
    """Yield (index, language, code, closed) for every fenced block in a file.

    Index is 1-based and counts every fence in the file, not only the css
    ones, so a reported fence-index lines up with what a reader counts.
    `closed` is False when the fence ran to EOF without a closing marker —
    such a block silently absorbs the rest of the document, so a valid CSS
    prefix would otherwise pass validation.
    """
    fences = []
    lines = content.splitlines()
    i = 0
    index = 0
    while i < len(lines):
        opener = FENCE_OPEN_RE.match(lines[i])
        if not opener:
            i += 1
            continue
        indent, marker, lang = opener.groups()
        char = marker[0]
        min_len = len(marker)
        body = []
        closed = False
        i += 1
        while i < len(lines):
            candidate = lines[i].strip()
            if (
                candidate
                and candidate[0] == char
                and set(candidate) == {char}
                and len(candidate) >= min_len
            ):
                i += 1
                closed = True
                break
            body.append(lines[i][len(indent):] if lines[i].startswith(indent) else lines[i])
            i += 1
        index += 1
        fences.append((index, lang.lower(), "\n".join(body), closed))
    return fences


def walk_for_errors(nodes, failures, label):
    """Recursively collect tinycss2 ParseError nodes from a node list."""
    for node in nodes:
        if getattr(node, "type", None) == "error":
            failures.append(
                f"{label}: parse error at line {node.source_line}: {node.message}",
            )
        for attr in ("content", "prelude", "arguments"):
            nested = getattr(node, attr, None)
            if isinstance(nested, list):
                walk_for_errors(nested, failures, label)


def collect_failures_for_file(path: Path, root: Path):
    failures = []
    rel = path.relative_to(root) if root in path.parents or root == path.parent else path
    content = path.read_text(encoding="utf-8")

    for index, lang, code, closed in extract_fences(content):
        label = f"{rel}:fence-{index}"
        if not closed:
            failures.append(
                f"{label}: unterminated fence — no closing marker before EOF",
            )
            continue
        if lang == "scss":
            failures.append(
                f"{label}: scss fence found — the css references are plain-CSS-only",
            )
            continue
        if lang != "css":
            continue
        rules = tinycss2.parse_stylesheet(code, skip_whitespace=True)
        walk_for_errors(rules, failures, label)

    return failures


def main() -> int:
    if len(sys.argv) > 2:
        print(
            "usage: validate_reference_css.py [references-dir-or-file]",
            file=sys.stderr,
        )
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    target = Path(sys.argv[1]) if len(sys.argv) == 2 else repo_root / DEFAULT_TARGET

    if target.is_file():
        md_files = [target]
        root = target.parent
    elif target.is_dir():
        md_files = sorted(target.rglob("*.md"))
        root = target
    else:
        print(f"no such file or directory: {target}", file=sys.stderr)
        return 2

    if not md_files:
        print(f"no markdown files under {target}", file=sys.stderr)
        return 2

    failures = []
    for path in md_files:
        failures.extend(collect_failures_for_file(path, root))

    if failures:
        print(
            f"reference CSS validation FAILED: "
            f"{len(failures)} problem(s) across {len(md_files)} file(s)",
            file=sys.stderr,
        )
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"reference CSS OK — {len(md_files)} markdown file(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
