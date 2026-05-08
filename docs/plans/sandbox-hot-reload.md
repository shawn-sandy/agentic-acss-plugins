# Hot reload for the test sandbox preview server

## Context

Today, previewing a generated component in a browser is a manual, no-reload flow documented in `plugins/acss-kit/docs/recipes.md` (lines 189–289):

1. `npx sass --no-source-map <name>.scss > /tmp/<name>.css`
2. Hand-paste the compiled CSS into a `<style>` block in `<name>-preview.html`
3. `python3 -m http.server 7743` from `tests/sandbox/`
4. Open browser, edit, **redo all three steps for every change**

There is no actual "server" in the repo — only this documented one-liner. The paste-CSS step blocks any reload-on-save workflow.

This plan replaces that flow with a single `tests/serve.sh` that watches SCSS, recompiles to CSS, and full-reloads the browser via esbuild's built-in SSE channel. Zero new dependencies — `esbuild` and `sass` are already in `tests/package.json`. Theme/component iteration becomes edit → save → see result.

## Objective

Add hot reloading to the sandbox preview workflow by introducing a single `tests/serve.sh` wrapper that runs `sass --watch` + `esbuild --serve` together, and updating the preview HTML template + docs to use `<link rel="stylesheet">` plus a tiny SSE client.

## Steps

1. **Create `tests/serve.sh`** — single entry point, sibling of `run.sh`/`e2e.sh`/`setup.sh`.
   - Why: Per `tests/README.md`, all test entry points live in `tests/`. The sandbox itself is gitignored and wiped by `setup.sh --reset`, so server config must live outside it.
   - Behavior:
     - Verify `tests/sandbox/` exists; if not, print `Run tests/setup.sh first.` and exit 1.
     - Verify `tests/node_modules/.bin/sass` and `…/esbuild` exist; if not, print `Run npm --prefix tests ci first.` and exit 1.
     - From `tests/`, start `npx sass --watch sandbox/src/components/fpkit:sandbox/src/components/fpkit sandbox/src/styles/theme:sandbox/src/styles/theme --no-source-map` backgrounded. Capture the PID into `SASS_PID`.
     - Probe port `7743`; if bind fails, increment to `7744`, `7745`, … until success (max 10 tries). Simplest implementation: attempt `npx esbuild --servedir=sandbox --serve=$PORT` in a retry loop and bump on bind error — avoids hard-coding `lsof`/`nc`.
     - Print `Serving http://localhost:<port>/` to stdout. **Do not** auto-open a browser.
     - Trap `EXIT`/`INT`/`TERM` with: `kill "$SASS_PID" 2>/dev/null; wait "$SASS_PID" 2>/dev/null` so the sass watcher exits cleanly on macOS.
     - Run esbuild in the foreground so Ctrl+C delivers SIGINT to the trap.
   - Preserve port `7743` as the default so existing docs and muscle memory continue to work.

1a. **Auto-generate `tests/sandbox/index.html` on each `serve.sh` start.**
   - Why: Multi-component sessions (`/kit-add button card input`) produce several `*-preview.html` files. A directory listing makes them discoverable without remembering filenames.
   - Behavior: Before starting esbuild, glob `tests/sandbox/*-preview.html`, write a simple `<ul>` of `<a href="…">` entries plus the same SSE reload script as the templates. Overwrite on every run so it stays current.
   - File is throwaway and re-generated; safe to commit-ignore.

2. **Update the preview HTML template in `recipes.md`** (lines 231–285).
   - Why: The current template inlines compiled CSS in a `<style>` block, which makes hot reload impossible without rebuilding the HTML on every save.
   - Replace the `<style>` block with:
     - `<link rel="stylesheet" href="src/components/fpkit/<name>/<name>.css">` for the component
     - Optional `<link rel="stylesheet" href="src/styles/theme/light.css">` if a theme is present
     - A short `<script>` that opens an `EventSource('/esbuild')` and calls `location.reload()` on the `change` event (~5 lines)
   - Keep the inline reset/typography styles (`*, *::before…`, `body`, `h1`, `h2`, `.row`) — these are fixture chrome, not component output.

3. **Update the recipe steps in `recipes.md`** (lines 189–229).
   - Why: The old "compile → paste → serve" steps no longer apply.
   - Replace step 1 (manual `sass` compile) and step 3 (`python3 -m http.server`) with a single instruction: `tests/serve.sh` from the repo root. Drop the `kill %1` step — Ctrl+C handles it.
   - Note that the SSE reload script in the template is what makes `serve.sh` worth running; without it, falling back to `python3 -m http.server 7743` from `tests/sandbox/` still works (mention this as a fallback for environments without Node).

4. **Update `tests/README.md`** (lines 129–207, the "Demo fixture" section).
   - Why: Line 131 currently says "previewing rendered components in a real browser was explicitly removed." That framing is now stale — we're adding back a static-HTML preview server, but explicitly not the React dev server that was removed.
   - Add a short subsection "Live preview: `tests/serve.sh`" pointing to the recipe in `plugins/acss-kit/docs/recipes.md#preview-a-generated-component-in-a-browser`.
   - Reword line 131 to clarify that the removed server was a React/Vite dev server; the new `serve.sh` is a static preview reloader, not an app shell.

5. **Add the SSE client snippet inline in the template** rather than as a separate file.
   - Why: The sandbox is wiped by `setup.sh --reset`. Anything stored *inside* `tests/sandbox/` is ephemeral. Inlining ~5 lines in the HTML template (which lives in `recipes.md`) keeps it durable.
   - Snippet shape: `new EventSource('/esbuild').addEventListener('change', () => location.reload());` wrapped in a guard so it no-ops when the page is opened over `python3 -m http.server` (no `/esbuild` endpoint).

6. **Update `CLAUDE.md`'s "Testing locally" section** with one line pointing at `tests/serve.sh` for live preview, alongside the existing `tests/run.sh` and `tests/e2e.sh` entries.
   - Why: Anyone scanning CLAUDE.md should see the third entry point.

7. **Add `tests/sandbox/.gitignore`** to exclude generated CSS and the auto-index.
   - Why: `sass --watch` writes `<name>.css` next to `<name>.scss`. The sandbox is normally gitignored under `.claude/worktrees/`, but `setup.sh` can scaffold elsewhere — those compiled CSS files would then surface in `git status`.
   - Entries: `**/fpkit/**/*.css`, `**/fpkit/**/*.css.map`, `index.html`.
   - `tests/setup.sh` already initializes a git repo inside the sandbox; emit this file alongside `RECIPE.md` so it's part of the bootstrap commit.

## Caveats

- **First-paint cold start**: on the very first `serve.sh` run, the browser may load before `sass --watch` finishes its initial compile pass — the page renders unstyled. The recipe should note: *"If the page renders unstyled on first open, save any SCSS file once to trigger compilation, then refresh."* The SSE reload covers all subsequent edits.
- **`.acss-target.json` redirects**: if a project has configured a non-default components directory via `.acss-target.json`, the hardcoded `sandbox/src/components/fpkit` watch path misses it. For the initial implementation, document this assumption in `tests/serve.sh`'s usage block. Reading `.acss-target.json` to derive the watch path is a follow-up.
- **`claude-in-chrome` MCP timing**: when the recipe is exercised via MCP (`navigate` then `computer screenshot`), a screenshot fired immediately after a save may capture a pre-reload frame. The recipe should suggest a brief wait or `wait_for(network_idle)` between the save and the screenshot.
- **Plan filename**: this file is named with the harness-assigned codename. On execution, rename to `sandbox-hot-reload.md` before committing per the project's plan-naming rule.

## Critical files

- **Create:** `tests/serve.sh` (~50 LOC bash with port retry + index generation, executable)
- **Create:** `tests/sandbox/.gitignore` (3 lines, emitted by `setup.sh`)
- **Edit:** `plugins/acss-kit/docs/recipes.md` — recipe steps + HTML template (lines 189–289)
- **Edit:** `tests/README.md` — Demo fixture section (lines 129–207)
- **Edit:** `tests/setup.sh` — emit `tests/sandbox/.gitignore` alongside `RECIPE.md`
- **Edit:** `CLAUDE.md` — Testing locally section (one line)

## Reused / existing pieces

- `esbuild` (already in `tests/package.json` devDeps) — provides `--servedir` static server + built-in `/esbuild` SSE reload channel
- `sass` (already in `tests/package.json` devDeps) — `--watch` mode handles recompilation
- Port `7743` (currently documented in `recipes.md:214`) — kept verbatim
- `tests/setup.sh` scaffolding — unchanged; `serve.sh` is purely additive
- `tests/sandbox/` directory layout — unchanged

## Verification

1. **Clean scaffold:** `tests/setup.sh --reset` then `cd tests/sandbox && claude` and run `/kit-add button` to generate `src/components/fpkit/button/{button.tsx,button.scss}`.
2. **Author preview:** Following the updated recipe in `recipes.md`, write `tests/sandbox/button-preview.html` from the new template (uses `<link>` + SSE script).
3. **Start the reloader:** From the repo root, `tests/serve.sh`. Confirm it logs the sass watcher startup and serves on `http://localhost:7743`.
4. **Initial render:** Open `http://localhost:7743/button-preview.html` in a browser (or via `claude-in-chrome` MCP). Verify variants render with compiled CSS.
5. **Live SCSS reload:** Edit `src/components/fpkit/button/button.scss` (e.g. change a color). Save. Within ~1s, the browser tab repaints with the new style — no manual refresh, no paste step.
6. **Live HTML reload:** Edit `button-preview.html` (e.g. add a variant). Save. The page reloads.
7. **Theme reload:** If `/theme-create` has been run, edit `src/styles/theme/light.css`. Save. Page reloads with new theme tokens.
8. **Clean shutdown:** Ctrl+C on `serve.sh`. Confirm both the sass watcher and esbuild server exit (no orphan `npx sass --watch` process — check with `ps -ef | grep sass`).
9. **Fallback path:** Stop `serve.sh`, run `python3 -m http.server 7743` from `tests/sandbox/`, reopen the URL. The SSE script no-ops gracefully (no console errors), the page renders, and edits require a manual refresh — confirming the template still works for environments without Node.
10. **Existing tests still green:** `tests/run.sh` from the repo root passes (no regression in component/manifest validation).

## Next Steps (out of scope)

- CSS-only injection (swap `<link>` href without full reload) — would need ~30 LOC of custom client and is a UX upgrade, not a foundational requirement. Worth considering after the full-reload baseline lands.
- Auto-open browser on `serve.sh` start (`open http://localhost:7743`) — nice-to-have, platform-specific.
- Wire `serve.sh` into a `tests/package.json` script (`npm --prefix tests run serve`) — convenience only; the shell script is the primary surface.
- Watch `*.tsx` for component-spec changes and re-run `tsc --noEmit` — separate concern from CSS preview reload.

## Interview Summary

### Key Decisions Confirmed

- **Watcher invocation**: Run both `npx esbuild` and `npx sass` from `tests/` so they resolve against `tests/node_modules`. Replaces the bogus `npx --prefix` syntax in the original draft.
- **Template migration**: Hard-cut to `<link rel="stylesheet">`. Drop the inlined-`<style>` template entirely. Existing `*-preview.html` files are throwaway scratch artifacts.
- **Port handling**: Try `7743`, auto-fallback to `7744`, `7745`, … on bind failure (max 10 retries). Print the chosen URL to stdout.
- **Process cleanup**: Capture `SASS_PID`, trap with explicit `kill "$SASS_PID"; wait "$SASS_PID"`. Survives macOS edge cases where bare `kill 0` leaves orphans.
- **SCSS error UX**: Terminal stderr only. Browser keeps last good CSS. No overlay code, no error page.
- **Multi-component preview**: `serve.sh` auto-generates `tests/sandbox/index.html` listing every `*-preview.html` it finds; refreshes on each start.
- **Launch behavior**: Print URL, do not auto-open. CI/scripting-friendly.
- **State preservation**: Full `location.reload()` is acceptable. CSS-link-swap stays in Next Steps.

### Open Risks & Concerns

- Compiled CSS files leak into `git status` if `tests/setup.sh` is run outside a `.claude/worktrees/` location — addressed by the new `tests/sandbox/.gitignore` step.
- `.acss-target.json` redirects are not honored by the hardcoded watch path. Documented as a Caveat; deriving the watch path from `.acss-target.json` is a follow-up.
- First-paint cold-start race: page may render unstyled until first SCSS save. Documentation-only mitigation in the recipe.
- `lsof`/`nc` portability sidestepped by using esbuild bind-failure retries instead of pre-probing the port.
- `claude-in-chrome` MCP screenshots may race with reloads; recipe should advise a brief wait between save and screenshot.

### Recommended Next Steps

1. Rename plan file from `declarative-imagining-moler.md` to `sandbox-hot-reload.md` on execution exit.
2. Run a smoke pass after implementation: `tests/setup.sh --reset` → `/kit-add button` → `tests/serve.sh` → edit `button.scss` → confirm reload.
3. Hold the CSS-link-swap (no-reload) upgrade in `Next Steps` until the full-reload baseline ships and is in use.

### Simplification Opportunities

None — the plan is at the right level of abstraction for the chosen scope.
