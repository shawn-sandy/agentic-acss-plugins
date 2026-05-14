# Migration guide — acss-kit v0.x → v1.0.0

This guide covers every user-facing change introduced in the v0.12 / v0.13 / v1.0.0 series and explains exactly what you need to do after upgrading.

---

## 1. Uninstall `acss-utilities`, install `acss-kit` v1.0.0

Utility commands (`/utility-add`, `/utility-bridge`, `/utility-list`, `/utility-tune`) now live inside `acss-kit`. The `acss-utilities` plugin is tombstoned at v1.0.0 — existing installs keep working but no new features will be added there.

```text
/plugin uninstall acss-utilities@shawn-sandy-agentic-acss-plugins
/plugin update acss-kit@shawn-sandy-agentic-acss-plugins
```

No CSS class names changed. Your existing `utilities.css` and `token-bridge.css` files in your project work without modification.

---

## 2. Command renames and additions

| Old command | New command | Notes |
|---|---|---|
| `/kit-add-html <name>` | `/kit-add --target=html <name>` | Old form still works (prints deprecation notice) |
| (acss-utilities) `/utility-add` | `/utility-add` | Now in acss-kit; arguments unchanged |
| (acss-utilities) `/utility-bridge` | `/utility-bridge` | Now in acss-kit; arguments unchanged |
| (acss-utilities) `/utility-list` | `/utility-list` | Now in acss-kit; arguments unchanged |
| (acss-utilities) `/utility-tune` | `/utility-tune` | Now in acss-kit; arguments unchanged |

---

## 3. Token bridge is now regenerated automatically

`token-bridge.css` was a static file that contained hard-coded hex fallbacks copied from `generate_palette.py`. Those fallbacks went stale every time you regenerated your theme.

From v1.0.0, every `/theme-create` and `/theme-update` run automatically regenerates `token-bridge.css` from your active theme via `generate_bridge.py`. The generated bridge uses `var()` chains with fresh hex fallbacks extracted from your current `light.css`/`dark.css`.

**Action required if you have a custom `token-bridge.css`:** If you manually edited `token-bridge.css` to add extra aliases, move those additions to `assets/utilities/vocab.json` before upgrading so they survive regeneration.

---

## 4. Vocabulary outcome — utility class names unchanged

The vocabulary delta between acss-kit roles and fpkit-style utility names is now declared in `assets/utilities/vocab.json`:

| acss-kit role | fpkit utility token | Utility class example |
|---|---|---|
| `--color-danger` | `--color-error` | `bg-error`, `text-error` |
| `--color-surface-raised` | `--color-surface-secondary` | `bg-surface-secondary` |

Utility class names (`bg-error`, `text-error`, etc.) are **not** renamed — existing markup works without changes.

---

## 5. Asset paths (plugin developers only)

If you reference acss-kit or acss-utilities assets in custom tooling:

| Old path | New path |
|---|---|
| `plugins/acss-utilities/assets/utilities.css` | `plugins/acss-kit/assets/utilities/utilities.css` |
| `plugins/acss-utilities/assets/token-bridge.css` | `plugins/acss-kit/assets/utilities/token-bridge.css` |
| `plugins/acss-utilities/assets/utilities.tokens.json` | `plugins/acss-kit/assets/utilities/utilities.tokens.json` |
| `plugins/acss-utilities/assets/utilities/<family>.css` | `plugins/acss-kit/assets/utilities/<family>.css` |
| `plugins/acss-utilities/scripts/generate_utilities.py` | `plugins/acss-kit/scripts/generate_utilities.py` |
| `plugins/acss-utilities/scripts/validate_utilities.py` | `plugins/acss-kit/scripts/validate_utilities.py` |
| `plugins/acss-utilities/scripts/migrate_classnames.py` | `plugins/acss-kit/scripts/migrate_classnames.py` |

---

## 6. Rollback

To stay on v0.x:

```text
/plugin install acss-kit@0.13.0@shawn-sandy-agentic-acss-plugins
/plugin install acss-utilities@0.5.0@shawn-sandy-agentic-acss-plugins
```

Or pin in your `plugin-lock.json` (if your Claude Code version supports it).

---

## 7. One-time bridge refresh for existing projects

If you already have a `token-bridge.css` in your project from a previous `acss-utilities` install, regenerate it once after upgrading to get fresh hex fallbacks:

```text
/utility-bridge
```

This runs `generate_bridge.py` against your current `src/styles/theme/` files and writes an up-to-date bridge without any manual hex editing.
