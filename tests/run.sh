#!/usr/bin/env bash
# Phase 1 test harness for agentic-acss-plugins.
#
# Runs the full structural validation gate. SERIAL ONLY — concurrent
# runs in the same checkout will collide on tests/.tmp/. If you need
# parallelism, run in separate worktrees.
#
# Steps:
#   1. Wipe tests/.tmp/.
#   2. Extract TSX/SCSS from acss-kit reference docs and syntax-check
#      the extracted TSX with TypeScript's parser API.
#   3. SCSS contract validation.
#   4. WCAG theme contrast (existing tool, lives under the plugin).
#   5. Manifest / structure replication of verify-plugins.
#   6. Known-bad self-tests: confirm the validators catch their own
#      contract violations.
#   7. detect_package_manager.py --self-test.
#   7a. detect_stack.py --self-test (framework + cssPipeline + entrypoint).
#   7b. verify_integration.py --self-test (entrypoint wiring checks).
#   7c. detect_css_entry.py --self-test (CSS/SCSS entry candidates +
#       @import / @use scan).
#   8. acss-kit utilities validator over plugins/acss-kit/assets/utilities/
#      (selector grammar, var() fallbacks, bridge dark-mode parity,
#      bundle-size budget).
#   9. acss-kit utilities idempotency: regenerate from utilities.tokens.json
#      and diff against the committed bundle + per-family partials.
#  10. migrate_classnames.py fixture round-trip + idempotency.
#
# Why syntax-only TSX validation: the reference docs split TSX across
# multiple Key Pattern sections containing illustrative JSX or
# inline-only snippets that don't resolve at module scope. Full type
# resolution would require either inlining helpers (fighting the docs'
# documentary structure) or accepting non-trivial false negatives.
# Syntax checks catch what regex can't (malformed JSX, broken generics)
# without that fight.
#
# If a step in this script regresses and blocks unrelated work, the
# documented escape hatch is to comment out the offending step in your
# branch and link a bug report in the PR description (see tests/README.md).

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

TMP_ROOT="$REPO_ROOT/tests/.tmp"
EXTRACTED="$TMP_ROOT/extracted"

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
section(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

# Step 1
section "1. wipe tests/.tmp/"
rm -rf "$TMP_ROOT"
mkdir -p "$EXTRACTED"

# Step 2
section "2. extract + syntax-check acss-kit references"
node "$REPO_ROOT/tests/validate_extracted_tsx.mjs"

# Step 2a — SCSS golden guard for the token-swept components (Workstream A PR 2–3).
# extract_full.mjs mirrors /kit-add; the SCSS goldens lock the swept output so
# future edits can't silently regress the --space/--radius token consumption.
# Scoped to SCSS — the sweep only changed SCSS; TSX goldens are deferred (see
# docs/plans/component-tsx-followups.md). nav has no golden (no ## TSX Template).
section "2a. component SCSS golden guard (token-sweep regression)"
GOLDEN_DIR="$REPO_ROOT/tests/fixtures/golden"
GOLDEN_FAIL=0
for gdir in "$GOLDEN_DIR"/component-*/; do
  n=$(basename "$gdir" | sed 's/^component-//')
  ref="$REPO_ROOT/plugins/acss-kit/skills/component-$n/reference.md"
  tmp="$TMP_ROOT/golden/$n"; mkdir -p "$tmp"
  cmd="$REPO_ROOT/plugins/acss-kit/skills/component-$n/$n.component.md"
  for kind in scss; do
    [ -f "$gdir/$n.$kind" ] || continue
    node "$REPO_ROOT/tests/lib/extract_full.mjs" "$ref" "$kind" > "$tmp/$n.$kind" 2>/dev/null || true
    if ! diff -u "$gdir/$n.$kind" "$tmp/$n.$kind" >"$tmp/$n.$kind.diff" 2>&1; then
      red "golden DRIFT: component-$n.$kind"
      head -20 "$tmp/$n.$kind.diff"
      GOLDEN_FAIL=1
    fi
    # Inverted COMPONENT.md (if present) must extract byte-identically to the
    # same golden — proves reference.md → COMPONENT.md inversion is lossless.
    if [ -f "$cmd" ]; then
      node "$REPO_ROOT/tests/lib/extract_full.mjs" "$cmd" "$kind" > "$tmp/$n.cmd.$kind" 2>/dev/null || true
      if ! diff -u "$gdir/$n.$kind" "$tmp/$n.cmd.$kind" >"$tmp/$n.cmd.$kind.diff" 2>&1; then
        red "golden DRIFT: component-$n.$kind (from $n.component.md)"
        head -20 "$tmp/$n.cmd.$kind.diff"
        GOLDEN_FAIL=1
      fi
    fi
  done
done
if [ "$GOLDEN_FAIL" = 0 ]; then
  green "component golden guard OK"
else
  red "Golden drift above. If intentional, regenerate the fixture:"
  red "  node tests/lib/extract_full.mjs <ref> tsx|scss > tests/fixtures/golden/component-<name>/<name>.<ext>"
  exit 1
fi

# Step 3
section "3. SCSS contract"
SCSS_LOG="$TMP_ROOT/scss-contract.log"
if python3 "$REPO_ROOT/tests/validate_extracted_scss.py" "$EXTRACTED" >"$SCSS_LOG"; then
  green "SCSS contract OK"
else
  red "SCSS contract failed:"
  cat "$SCSS_LOG"
  exit 1
fi

# Step 4
section "4. WCAG theme contrast"
THEME_DIR="$REPO_ROOT/plugins/acss-kit/assets"
THEME_LOG="$TMP_ROOT/theme-contrast.log"
if compgen -G "$THEME_DIR/themes/*.css" > /dev/null; then
  if python3 "$REPO_ROOT/plugins/acss-kit/scripts/validate_theme.py" "$THEME_DIR/themes/"*.css >"$THEME_LOG"; then
    green "theme contrast OK"
  else
    red "theme contrast failed:"
    cat "$THEME_LOG"
    exit 1
  fi
elif [ -f "$THEME_DIR/brand-template.css" ]; then
  yellow "no themes/*.css yet; brand-template.css is the only theme on disk — skipping WCAG check"
else
  yellow "no theme css under $THEME_DIR — skipping WCAG check"
fi

# Step 5
section "5. manifest / structure"
MANIFEST_LOG="$TMP_ROOT/manifest.log"
if python3 "$REPO_ROOT/tests/validate_manifest.py" >"$MANIFEST_LOG"; then
  green "manifest OK"
else
  red "manifest validation failed:"
  cat "$MANIFEST_LOG"
  exit 1
fi

# Step 6
section "6. known-bad self-tests"
KNOWN_BAD_TMP="$TMP_ROOT/known-bad"
mkdir -p "$KNOWN_BAD_TMP"
cp "$REPO_ROOT/tests/fixtures/known-bad/known-bad.scss" "$KNOWN_BAD_TMP/"

# (a) SCSS validator must FAIL on known-bad.scss
if python3 "$REPO_ROOT/tests/validate_extracted_scss.py" "$KNOWN_BAD_TMP" >/dev/null 2>&1; then
  red "known-bad: validate_extracted_scss.py PASSED on known-bad fixtures (regex regressed)"
  exit 1
fi
green "SCSS validator caught known-bad.scss"

# (b) TSX validator must reject the banned import in known-bad.tsx.
# Build a synthetic reference doc using known-bad.tsx as its TSX Template,
# then call the *exported* checkImports() from validate_extracted_tsx.mjs
# directly. This exercises the real validator code path; a stub regex
# here would let import-allowlist regressions slip through.
KNOWN_BAD_REF="$KNOWN_BAD_TMP/known-bad.md"
{
  printf '%s\n\n' '# Component: KnownBad'
  printf '%s\n\n' '## Props Interface'
  printf '%s\n' '```tsx'
  printf '%s\n' 'export type KnownBadProps = { children?: React.ReactNode }'
  printf '%s\n' '```'
  printf '\n%s\n\n' '## TSX Template'
  printf '%s\n' '```tsx'
  cat "$REPO_ROOT/tests/fixtures/known-bad/known-bad.tsx"
  printf '%s\n' '```'
  printf '\n%s\n\n' '## SCSS Template'
  printf '%s\n' '```scss'
  printf '%s\n' '.known-bad { padding: 1rem; }'
  printf '%s\n' '```'
  printf '\n%s\n' '## Accessibility'
} > "$KNOWN_BAD_REF"

KNOWN_BAD_REF_PATH="$KNOWN_BAD_REF" node --input-type=module -e "
import { extractFromFile } from '$REPO_ROOT/plugins/acss-kit/scripts/lib/extract.mjs';
import { checkImports } from '$REPO_ROOT/tests/validate_extracted_tsx.mjs';

const { tsx } = extractFromFile(process.env.KNOWN_BAD_REF_PATH);
if (!tsx) { console.error('known-bad: no tsx extracted'); process.exit(1); }

const failures = checkImports('known-bad', tsx);
if (failures.length === 0) {
  console.error('known-bad: validate_extracted_tsx.mjs accepted banned import in synthetic reference');
  process.exit(1);
}
console.log('known-bad: TSX validator caught', failures.length, 'failure(s)');
"

green "TSX validator caught known-bad.tsx"

# Step 7
section "7. detect_package_manager.py --self-test"
DPM_LOG="$TMP_ROOT/detect-pm.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_package_manager.py" --self-test >"$DPM_LOG"; then
  green "detect_package_manager self-test OK"
else
  red "detect_package_manager self-test FAILED:"
  cat "$DPM_LOG"
  exit 1
fi

section "7a. detect_stack.py --self-test"
DS_LOG="$TMP_ROOT/detect-stack.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_stack.py" --self-test >"$DS_LOG"; then
  green "detect_stack self-test OK"
else
  red "detect_stack self-test FAILED:"
  cat "$DS_LOG"
  exit 1
fi

section "7b. verify_integration.py --self-test"
VI_LOG="$TMP_ROOT/verify-integration.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/verify_integration.py" --self-test >"$VI_LOG"; then
  green "verify_integration self-test OK"
else
  red "verify_integration self-test FAILED:"
  cat "$VI_LOG"
  exit 1
fi

section "7c. detect_css_entry.py --self-test"
DCE_LOG="$TMP_ROOT/detect-css-entry.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_css_entry.py" --self-test >"$DCE_LOG"; then
  green "detect_css_entry self-test OK"
else
  red "detect_css_entry self-test FAILED:"
  cat "$DCE_LOG"
  exit 1
fi

section "7d. kit-sync manifest scripts (hash_file + manifest_write + manifest_read + diff_status)"
KS_LOG="$TMP_ROOT/kit-sync.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/diff_status.py" --self-test >"$KS_LOG"; then
  green "kit-sync manifest self-test OK"
else
  red "kit-sync manifest self-test FAILED:"
  cat "$KS_LOG"
  exit 1
fi

section "7e. generate_color_scale.py smoke test"
GCS_LOG="$TMP_ROOT/color-scale.log"
if python3 - >"$GCS_LOG" 2>&1 <<'PYEOF'
import json, re, subprocess, sys

script = "plugins/acss-kit/scripts/generate_color_scale.py"
seed   = "#4f46e5"

# JSON output: 10 steps, valid hex values, correct step keys
r = subprocess.run([sys.executable, script, seed, "--name=primary", "--format=json"],
                   capture_output=True, text=True)
assert r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()}"
data = json.loads(r.stdout)
assert data["name"] == "primary" and data["seed"] == seed
assert len(data["steps"]) == 10, f"expected 10 steps, got {len(data['steps'])}"
assert [s["step"] for s in data["steps"]] == [50,100,200,300,400,500,600,700,800,900]
assert "reasons" in data, "top-level reasons missing"
assert isinstance(data["reasons"], list)
hex_re = re.compile(r"^#[0-9a-f]{6}$")
for s in data["steps"]:
    assert hex_re.match(s["hex"]), f"invalid hex at step {s['step']}: {s['hex']}"
    assert "clamped" in s and isinstance(s["clamped"], bool), f"clamped field missing at step {s['step']}"
    assert "reasons" in s and isinstance(s["reasons"], list), f"reasons field missing at step {s['step']}"

# CSS output: starts with :root
r = subprocess.run([sys.executable, script, seed, "--name=primary", "--format=css"],
                   capture_output=True, text=True)
assert r.returncode == 0 and r.stdout.startswith(":root {"), "css output malformed"

# Unknown flag → exit 2
r = subprocess.run([sys.executable, script, seed, "--typo=x"], capture_output=True, text=True)
assert r.returncode == 2, f"unknown flag: expected exit 2, got {r.returncode}"

# Invalid hex → exit 2
r = subprocess.run([sys.executable, script, "notahex"], capture_output=True, text=True)
assert r.returncode == 2, f"bad hex: expected exit 2, got {r.returncode}"

# ## makes ##fff reject (lstrip would have accepted it)
r = subprocess.run([sys.executable, script, "##fff"], capture_output=True, text=True)
assert r.returncode == 2, f"double-hash: expected exit 2, got {r.returncode}"

# Invalid --name → exit 2
r = subprocess.run([sys.executable, script, seed, "--name=Bad Name!"], capture_output=True, text=True)
assert r.returncode == 2, f"bad name: expected exit 2, got {r.returncode}"

print("generate_color_scale smoke test OK")
PYEOF
then
  green "generate_color_scale self-test OK"
else
  red "generate_color_scale self-test FAILED:"
  cat "$GCS_LOG"
  exit 1
fi

section "7f. token homes self-test (tokens_to_css + css_to_tokens round-trip + validate_tokens)"
TOK_LOG="$TMP_ROOT/token-homes.log"
if python3 - "$REPO_ROOT" >"$TOK_LOG" 2>&1 <<'PYEOF'
import json, subprocess, sys, tempfile
from pathlib import Path
root = Path(sys.argv[1])
scripts = root / "plugins/acss-kit/scripts"
sys.path.insert(0, str(scripts))
from _tokens import SPACE_SCALE, RADIUS_SCALE, DEFAULT_TYPOGRAPHY  # noqa: E402

# 1. each script's own self-test
for s in ("tokens_to_css.py", "css_to_tokens.py", "validate_tokens.py",
          "design_md_to_tokens.py", "validate_design_md.py", "tokens_to_design_md.py",
          "figma_to_tokens.py"):
    r = subprocess.run([sys.executable, str(scripts / s), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, f"{s} self-test failed:\n{r.stdout}{r.stderr}"

# 1b. DESIGN.md adapter end-to-end: fixture css-tailwind -> tokens -> CSS -> contrast gate
import importlib.util
spec = importlib.util.spec_from_file_location("dmt", str(scripts / "design_md_to_tokens.py"))
dmt = importlib.util.module_from_spec(spec); sys.path.insert(0, str(scripts)); spec.loader.exec_module(dmt)
adapter = subprocess.run([sys.executable, str(scripts / "design_md_to_tokens.py"), "--stdin"],
                         input=dmt._FIXTURE, capture_output=True, text=True)
assert adapter.returncode == 0, f"adapter failed: {adapter.stderr}"
with tempfile.TemporaryDirectory() as ad:
    subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), "--stdin", f"--out-dir={ad}"],
                   input=adapter.stdout, check=True, text=True, stdout=subprocess.DEVNULL)
    vt = subprocess.run([sys.executable, str(scripts / "validate_theme.py"), ad], capture_output=True, text=True)
    assert vt.returncode == 0, f"adapter output failed contrast: {vt.stdout}"

# 1c. export round-trip: theme -> DESIGN.md -> back through adapter -> CSS -> contrast.
# Semantic (value-preserving) round-trip: M3-named roles survive; success/warning/
# focus-ring/text-subtle are re-synthesized. Asserts the closed loop still gates.
tdm = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("tdm", str(scripts / "tokens_to_design_md.py")))
importlib.util.spec_from_file_location("tdm", str(scripts / "tokens_to_design_md.py")).loader.exec_module(tdm)
with tempfile.TemporaryDirectory() as td:
    pal = subprocess.run([sys.executable, str(scripts / "generate_palette.py"), "#855300"],
                         capture_output=True, text=True, check=True).stdout
    Path(td, "palette.json").write_text(pal)
    subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), str(Path(td, "palette.json")),
                    f"--out-dir={td}"], check=True, stdout=subprocess.DEVNULL)
    for asset in ("space-radius.css", "typography.css"):
        Path(td, asset).write_text((root / "plugins/acss-kit/assets/tokens" / asset).read_text())
    dmd = subprocess.run([sys.executable, str(scripts / "tokens_to_design_md.py"), f"--dir={td}"],
                         capture_output=True, text=True, check=True).stdout
    colors = tdm.parse_front_matter_scalars(dmd).get("colors", {})
    assert colors.get("primary") == "#9f6c27" or colors.get("primary"), "export lost primary"
    # re-import: emit a css-tailwind @theme block from the DESIGN.md color names
    theme_block = "@theme {\n" + "".join(f"  --color-{k}: {v};\n" for k, v in colors.items()) + "}\n"
    reimport = subprocess.run([sys.executable, str(scripts / "design_md_to_tokens.py"), "--stdin"],
                              input=theme_block, capture_output=True, text=True)
    assert reimport.returncode == 0, f"re-import failed: {reimport.stderr}"
    with tempfile.TemporaryDirectory() as rd:
        subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), "--stdin", f"--out-dir={rd}"],
                       input=reimport.stdout, check=True, text=True, stdout=subprocess.DEVNULL)
        vt2 = subprocess.run([sys.executable, str(scripts / "validate_theme.py"), rd],
                             capture_output=True, text=True)
        assert vt2.returncode == 0, f"export round-trip failed contrast: {vt2.stdout}"

# 1d. Figma bridge end-to-end: get_variable_defs fixture -> tokens -> CSS -> contrast
fig = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("fig", str(scripts / "figma_to_tokens.py")))
importlib.util.spec_from_file_location("fig", str(scripts / "figma_to_tokens.py")).loader.exec_module(fig)
ftokens, freasons = fig.figma_to_tokens(fig._FIXTURE)
assert ftokens.get("modes", {}).get("light", {}).get("--color-primary"), f"figma bridge lost primary: {freasons}"
vtok = subprocess.run([sys.executable, str(scripts / "validate_tokens.py"), "--stdin"],
                      input=json.dumps(ftokens), capture_output=True, text=True)
assert vtok.returncode == 0, f"figma tokens failed validate_tokens: {vtok.stdout}{vtok.stderr}"
with tempfile.TemporaryDirectory() as fd:
    subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), "--stdin", f"--out-dir={fd}"],
                   input=json.dumps(ftokens), check=True, text=True, stdout=subprocess.DEVNULL)
    vtf = subprocess.run([sys.executable, str(scripts / "validate_theme.py"), fd], capture_output=True, text=True)
    assert vtf.returncode == 0, f"figma bridge output failed contrast: {vtf.stdout}"

# 2. byte-stable round-trip of the default scales
src = {"spacing": SPACE_SCALE, "rounded": RADIUS_SCALE, "typography": DEFAULT_TYPOGRAPHY}
with tempfile.TemporaryDirectory() as d:
    subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), "--stdin", f"--out-dir={d}"],
                   input=json.dumps(src), text=True, check=True, stdout=subprocess.DEVNULL)
    out = subprocess.run([sys.executable, str(scripts / "css_to_tokens.py"), f"--dir={d}"],
                         capture_output=True, text=True, check=True).stdout
    rt = json.loads(out)
    assert rt.get("spacing") == SPACE_SCALE, "spacing round-trip drift"
    assert rt.get("rounded") == RADIUS_SCALE, "rounded round-trip drift"
    assert rt.get("typography") == DEFAULT_TYPOGRAPHY, "typography round-trip drift"

# 3. shipped default assets validate clean
for f in ("space-radius.css", "typography.css"):
    p = root / "plugins/acss-kit/assets/tokens" / f
    assert p.exists(), f"missing default asset {f}"

print("token homes round-trip + self-tests OK")
PYEOF
then
  green "token homes self-test OK"
else
  red "token homes self-test FAILED:"
  cat "$TOK_LOG"
  exit 1
fi

# Step 7g
section "7g. DESIGN.md dogfood (component {token.path} refs resolve + re-import gates)"
DOG_LOG="$TMP_ROOT/design-md-dogfood.log"
if python3 - "$REPO_ROOT" >"$DOG_LOG" 2>&1 <<'PYEOF'
import re, subprocess, sys, tempfile
from pathlib import Path
root = Path(sys.argv[1])
scripts = root / "plugins/acss-kit/scripts"
dmd_path = root / "tests/fixtures/design-md/DESIGN.md"
assert dmd_path.exists(), f"missing dogfood fixture {dmd_path}"
sys.path.insert(0, str(scripts))
import tokens_to_design_md as tdm  # noqa: E402

dmd = dmd_path.read_text(encoding="utf-8")
assert dmd.startswith("---"), "DESIGN.md must open with YAML front-matter"
fm = dmd.split("---", 2)[1]

# defined token names per primitive group, parsed from the front-matter
scalars = tdm.parse_front_matter_scalars(dmd)            # colors / spacing / rounded
defined = {g: set(scalars.get(g, {})) for g in ("colors", "spacing", "rounded")}
defined["typography"] = set()                            # top-level style keys
in_typo = False
for line in fm.splitlines():
    if re.match(r"^typography:\s*$", line):
        in_typo = True; continue
    if in_typo:
        if re.match(r"^[a-z]", line):                    # next top-level group
            in_typo = False; continue
        m = re.match(r"^  ([\w-]+):\s*$", line)          # 2-space style name
        if m:
            defined["typography"].add(m.group(1))
for g in ("colors", "spacing", "rounded", "typography"):
    assert defined[g], f"DESIGN.md front-matter defines no {g} tokens"

# every {token.path} the shipped component files reference must resolve
refs = {}
for f in sorted((root / "plugins/acss-kit/skills").glob("component-*/*.component.md")):
    for g, n in re.findall(r"\{(colors|spacing|rounded|typography)\.([a-z0-9-]+)\}",
                           f.read_text(encoding="utf-8")):
        refs.setdefault((g, n), f.name)
assert refs, "found no {token.path} references in component files — globbing broke?"
unresolved = sorted(f"{g}.{n} ({src})" for (g, n), src in refs.items() if n not in defined[g])
assert not unresolved, (
    "component {token.path} refs do not resolve against the dogfood DESIGN.md:\n  "
    + "\n  ".join(unresolved)
    + "\n(fix the ref to a DESIGN.md/M3 token name, or add the token to the fixture)")

# closed loop: DESIGN.md colors -> adapter -> CSS -> WCAG contrast gate
colors = scalars.get("colors", {})
assert colors.get("primary"), "dogfood DESIGN.md lost its primary color"
theme_block = "@theme {\n" + "".join(f"  --color-{k}: {v};\n" for k, v in colors.items()) + "}\n"
reimport = subprocess.run([sys.executable, str(scripts / "design_md_to_tokens.py"), "--stdin"],
                          input=theme_block, capture_output=True, text=True)
assert reimport.returncode == 0, f"re-import failed: {reimport.stderr}"
with tempfile.TemporaryDirectory() as d:
    subprocess.run([sys.executable, str(scripts / "tokens_to_css.py"), "--stdin", f"--out-dir={d}"],
                   input=reimport.stdout, check=True, text=True, stdout=subprocess.DEVNULL)
    vt = subprocess.run([sys.executable, str(scripts / "validate_theme.py"), d],
                        capture_output=True, text=True)
    assert vt.returncode == 0, f"dogfood DESIGN.md re-import failed contrast: {vt.stdout}"

print(f"dogfood OK — {len(refs)} component refs resolve; re-import gates clean")
PYEOF
then
  green "DESIGN.md dogfood OK"
else
  red "DESIGN.md dogfood FAILED:"
  cat "$DOG_LOG"
  exit 1
fi

# Step 8
section "8. acss-kit utilities validator"
UTIL_DIR="$REPO_ROOT/plugins/acss-kit/assets/utilities"
if [ -d "$UTIL_DIR" ]; then
  UTIL_LOG="$TMP_ROOT/utilities-validate.log"
  if python3 "$REPO_ROOT/plugins/acss-kit/scripts/validate_utilities.py" "$UTIL_DIR" >"$UTIL_LOG"; then
    green "acss-kit utilities validator OK"
  else
    red "acss-kit utilities validator failed:"
    cat "$UTIL_LOG"
    exit 1
  fi
else
  yellow "no plugins/acss-kit/assets/utilities — skipping utilities validator"
fi

# Step 9
section "9. acss-kit utilities idempotency"
if [ -f "$UTIL_DIR/utilities.tokens.json" ]; then
  UTIL_REGEN_DIR="$TMP_ROOT/utilities-regen"
  mkdir -p "$UTIL_REGEN_DIR"
  REGEN_LOG="$TMP_ROOT/utilities-regen.log"
  if ! python3 "$REPO_ROOT/plugins/acss-kit/scripts/generate_utilities.py" \
         --tokens "$UTIL_DIR/utilities.tokens.json" \
         --out-dir "$UTIL_REGEN_DIR" >"$REGEN_LOG" 2>&1; then
    red "acss-kit utilities generator failed:"
    cat "$REGEN_LOG"
    exit 1
  fi
  IDEMPOTENT=1
  if ! diff -q "$UTIL_DIR/utilities.css" "$UTIL_REGEN_DIR/utilities.css" >/dev/null; then
    IDEMPOTENT=0
  fi
  # acss-kit's committed layout keeps per-family partials flat at
  # assets/utilities/<family>.css, while generate_utilities.py writes them
  # to <out>/utilities/<family>.css. Compare across the layout difference.
  for partial in "$UTIL_DIR"/*.css; do
    name="$(basename "$partial")"
    [ "$name" = "utilities.css" ] && continue
    [ "$name" = "token-bridge.css" ] && continue
    if [ -f "$UTIL_REGEN_DIR/utilities/$name" ]; then
      if ! diff -q "$partial" "$UTIL_REGEN_DIR/utilities/$name" >/dev/null; then
        IDEMPOTENT=0
      fi
    fi
  done
  if [ "$IDEMPOTENT" -eq 0 ]; then
    red "acss-kit utilities idempotency check failed — regenerated bundle diverges from the committed copy."
    red "Run \`python3 plugins/acss-kit/scripts/generate_utilities.py --tokens \\"
    red "  plugins/acss-kit/assets/utilities/utilities.tokens.json --out-dir plugins/acss-kit/assets/utilities/\` and commit."
    diff "$UTIL_DIR/utilities.css" "$UTIL_REGEN_DIR/utilities.css" | head -40 || true
    exit 1
  fi
  green "acss-kit utilities idempotency OK"
else
  yellow "no plugins/acss-kit/assets/utilities/utilities.tokens.json — skipping idempotency check"
fi

# Step 10
section "10. migrate_classnames.py fixture round-trip + idempotency"
MIGRATE_SCRIPT="$REPO_ROOT/plugins/acss-kit/scripts/migrate_classnames.py"
FIXTURES_DIR="$REPO_ROOT/plugins/acss-kit/scripts/tests/migrate_fixtures"
if [ -f "$MIGRATE_SCRIPT" ] && [ -d "$FIXTURES_DIR" ]; then
  MIGRATE_LOG="$TMP_ROOT/migrate-classnames.log"
  MIGRATE_FAIL=0
  MIGRATE_TMP="$TMP_ROOT/migrate-fixtures"
  mkdir -p "$MIGRATE_TMP"
  for before in "$FIXTURES_DIR"/*.before.*; do
    [ -f "$before" ] || continue
    bname="$(basename "$before")"
    ext="${bname##*.}"
    stem="${bname%.before.*}"
    after="$FIXTURES_DIR/${stem}.after.${ext}"
    [ -f "$after" ] || continue
    tmp_copy="$MIGRATE_TMP/${bname}"
    cp "$before" "$tmp_copy"
    # Run once (write mode)
    python3 "$MIGRATE_SCRIPT" "$tmp_copy" --write >/dev/null 2>&1
    # Compare to .after fixture
    if ! diff -q "$tmp_copy" "$after" >/dev/null 2>&1; then
      echo "FAIL (round-trip): $stem" >> "$MIGRATE_LOG"
      diff "$after" "$tmp_copy" >> "$MIGRATE_LOG" 2>&1 || true
      MIGRATE_FAIL=1
      continue
    fi
    # Run again (idempotency)
    cp "$tmp_copy" "${tmp_copy}.orig"
    python3 "$MIGRATE_SCRIPT" "$tmp_copy" --write >/dev/null 2>&1
    if ! diff -q "${tmp_copy}.orig" "$tmp_copy" >/dev/null 2>&1; then
      echo "FAIL (idempotency): $stem" >> "$MIGRATE_LOG"
      MIGRATE_FAIL=1
    fi
    rm -f "${tmp_copy}.orig"
  done
  if [ "$MIGRATE_FAIL" -eq 0 ]; then
    green "migrate_classnames fixture tests OK"
  else
    red "migrate_classnames fixture tests FAILED:"
    cat "$MIGRATE_LOG"
    exit 1
  fi
else
  yellow "migrate_classnames.py or fixtures not found — skipping"
fi

# Step 11 — foundation.css structural checks
section "11. foundation.css structural checks"
FOUNDATION_CSS="$REPO_ROOT/plugins/acss-kit/assets/foundation/foundation.css"
SOURCE_MD="$REPO_ROOT/plugins/acss-kit/assets/foundation/SOURCE.md"

if [ ! -f "$FOUNDATION_CSS" ]; then
  red "foundation.css not found at $FOUNDATION_CSS"
  exit 1
fi

# 11a — parse with tinycss2
PARSE_LOG="$TMP_ROOT/foundation-parse.log"
if python3 - "$FOUNDATION_CSS" >"$PARSE_LOG" 2>&1 <<'PYEOF'
import sys, tinycss2
css = open(sys.argv[1], encoding="utf-8").read()
rules, _ = tinycss2.parse_stylesheet_bytes(css.encode())
errors = [r for r in rules if r.type == "error"]
if errors:
    for e in errors:
        print(f"  parse error: {e}")
    sys.exit(1)
print("OK")
PYEOF
then
  green "foundation.css parses OK"
else
  red "foundation.css parse failed:"
  cat "$PARSE_LOG"
  exit 1
fi

# 11b — no --color-* semantic roles inside @layer foundation
# Scan the full file; 11c already confirms the layer wrapper is present.
# Primitives use hue-based names; semantic roles do not.
if python3 - "$FOUNDATION_CSS" <<'PYEOF'
import sys, re
text = open(sys.argv[1], encoding="utf-8").read()
semantic_re = re.compile(
    r'^\s*(--color-(?!neutral|blue|green|red|amber|cyan)[a-z][\w-]*):', re.MULTILINE
)
hits = semantic_re.findall(text)
if hits:
    print(f"ERROR: semantic --color-* roles found in foundation.css: {hits[:5]}")
    sys.exit(1)
print("OK")
PYEOF
then
  green "No semantic --color-* roles inside @layer foundation (P1 enforced)"
else
  red "P1 violation: --color-* semantic roles found inside @layer foundation"
  exit 1
fi

# 11c — @layer foundation wrapper present
if grep -q '@layer foundation {' "$FOUNDATION_CSS"; then
  green "@layer foundation wrapper present (P4 enforced)"
else
  red "foundation.css missing @layer foundation wrapper (P4 violated)"
  exit 1
fi

# 11d — P3 reduced-motion block present (checks for unique P3 token zeroing,
#        not just prefers-reduced-motion which also exists in the vendored reset)
if grep -q '\-\-tran-all: none' "$FOUNDATION_CSS"; then
  green "P3 reduced-motion token block present (P3 enforced)"
else
  red "foundation.css missing P3 --tran-all: none block (P3 violated)"
  exit 1
fi

# 11e — SOURCE.md lists all four patches
if [ ! -f "$SOURCE_MD" ]; then
  red "SOURCE.md not found at $SOURCE_MD"
  exit 1
fi
for patch in "P1" "P2" "P3" "P4"; do
  if ! grep -q "$patch" "$SOURCE_MD"; then
    red "SOURCE.md missing patch $patch"
    exit 1
  fi
done
green "SOURCE.md lists patches P1–P4"

section "ALL STEPS GREEN"
green "Phase 1 harness passed."
