# acss-kit — Troubleshooting

---

## "sass or sass-embedded not found in devDependencies"

**Symptom:** `/kit-add` aborts immediately with a message about missing sass.

**Fix:**

```bash
npm install -D sass
```

Then re-run `/kit-add`. The plugin reads `package.json`'s `devDependencies` key — make sure the install completed and the key is present before retrying.

If your project uses `sass-embedded` instead:

```bash
npm install -D sass-embedded
```

Either package satisfies the check.

---

## "Theme generated but my app still looks unstyled"

**Symptom:** `/setup` reports `Created src/styles/theme/light.css` and `dark.css`, but the running app shows no theme — text is browser-default, buttons aren't tinted, dark mode doesn't switch.

**Cause:** The theme CSS files exist on disk but nothing imports them. Step 7.5 of `/setup` should append `@import` lines to your project's main CSS/SCSS file; when it doesn't run (e.g. you ran `/setup --no-theme`, declined the prompt, or the project had no detectable entry file), the theme is never loaded into the cascade.

**Fix — re-run the wiring:** Either re-run `/setup` (idempotent — it picks up where it left off), or open `.acss-target.json` at the project root and inspect `stack.cssEntryFile`. If the field is missing, `/setup` did not wire any entry; if it points to a file, confirm that file imports `light.css` and `dark.css`.

To wire by hand, append these lines to your main CSS/SCSS entry (e.g. `src/styles/index.scss`):

```scss
@import "./theme/light.css";
@import "./theme/dark.css";
```

Then make sure that file is itself imported from your app entrypoint (typically `src/main.tsx`):

```ts
import './styles/index.scss';
```

Run `python3 plugins/acss-kit/scripts/verify_integration.py <project-root>` to confirm — it accepts theme imports living in either `stack.entrypointFile` (TSX) or `stack.cssEntryFile` (SCSS/CSS).

---

## "I want the theme imports in a different CSS file than /setup chose"

**Symptom:** `/setup` Step 7.5 wired the theme into `src/styles/index.scss`, but you want it in a different file (e.g. `src/index.css` because your project doesn't use SCSS).

**Fix:** Edit `.acss-target.json` to point `stack.cssEntryFile` at the file you actually want, then move (or delete + re-add) the `@import` lines:

```json
{
  "stack": {
    "cssEntryFile": "src/index.css"
  }
}
```

Or simply delete the `cssEntryFile` key and re-run `/setup` — the detector will list every candidate it finds and let you pick the right one.

---

## "Components are generating into the wrong directory"

**Symptom:** Files appear in a different folder than expected.

**Cause:** `.acss-target.json` at the project root contains a `componentsDir` value from a previous `/kit-add` run.

**Fix:** Open `.acss-target.json` and update `componentsDir` to the path you want:

```json
{
  "componentsDir": "src/components/fpkit"
}
```

Future `/kit-add` runs will use the new path. Existing generated files in the old directory are not moved — rename the directory manually and update your imports if you change the path after files have already been generated.

---

## Component name not recognized

**Symptom:** `/kit-add frobniz` fails or produces an empty preview.

**Fix:** Run `/kit-list` to see the full list of available component names. Names are lowercase and exact — `dialog`, not `Dialog` or `modal`. The available components are: badge, tag, heading, text, link, list, details, progress, icon, button, alert, card, nav, dialog, form.

If you need a component that is not listed, it does not yet have a bundled reference doc. Use `/kit-list` to check for aliases, or author a new component reference following the contributor recipe in the README.

---

## "ui.tsx already exists but looks different from what the plugin expects"

**Symptom:** After running `/kit-add`, you notice that the `ui.tsx` in your project does not match the `assets/foundation/ui.tsx` in the plugin. Your generated components import from it, but something behaves unexpectedly.

**Cause:** The skip-existing rule means `/kit-add` never overwrites `ui.tsx` once it exists. If you or another plugin wrote a different `ui.tsx` first, the generated components will import from that file.

**Fix:** Compare your `ui.tsx` against [`assets/foundation/ui.tsx`](../assets/foundation/ui.tsx). If they have diverged, copy the plugin's version and reconcile any local modifications. The `UI` component's polymorphic type chain (`PolymorphicRef<C>` → `UIProps<C>` → `UIComponent`) must be intact for generated components to type-check correctly.

---

## "Bottom-up generation order is surprising"

**Symptom:** You expected `alert` to be generated before `button`, but they were generated in the opposite order.

**Explanation:** The plugin generates leaf dependencies first. If Alert depends on Button, Button is generated first (it is closer to the leaf). This is intentional — it guarantees that every dependency exists on disk before the component that imports it is written.

If you are surprised by which component depends on which, run `/kit-list <component>` to see the full dependency list before running `/kit-add`.

---

## "My edited component was overwritten"

**Symptom:** You edited a generated file, then re-ran `/kit-add` and your changes were gone.

**This should not happen.** The skip-existing rule means `/kit-add` does not write to a file that already exists. If your edits were lost, check:

1. Did you delete and recreate the file before running `/kit-add`?
2. Was the file in the correct `componentsDir` at the time of the second run? (Check `.acss-target.json`.)
3. Did another manual edit or script rewrite the file outside the `/kit-add` flow? The plugin itself skips existing generated files.

---

## Import paths resolve incorrectly after renaming a component file

**Symptom:** After renaming `button/button.tsx` to `button/btn.tsx`, the Dialog component breaks because it imports from `../button/button`.

**Cause:** Import paths in generated files are resolved at generation time from the component's `file` field in its Generation Contract. Renaming files after generation requires updating imports manually.

**Fix:** Update all `import` statements that reference the old filename. There is no automated re-import for post-generation renames.

---

## Pilot skill failure modes

The three pilot skills (`component-creator`, `component-form`, `style-tune`) auto-trigger on natural-language prompts. Their parsers cover common cases but can decline on edge inputs. The fallback in every case is to drop down to the explicit slash command and edit by hand.

### `component-creator`: "No `acss-kit` component matches …"

**Symptom:** A prompt like *"create a small badge that says 5"* returns a halt message: *"No `acss-kit` component matches \"badge\". Run `/kit-list` to see the catalog…"*. `component-creator` only resolves components that have a dedicated `references/components/<name>.md` doc.

**Cause:** Six components — Badge, Tag, Heading, Text/Paragraph, Details, Progress — are still inline entries in `references/components/catalog.md`. The creator can't parse Props Interface against an inline entry, so prompts naming them fall through to the no-mapping halt.

**Fix:** Drop down to `/kit-add <name>` to vendor the component, then hand-edit the JSX where you want it. Promotion of inline entries to dedicated reference docs is tracked under "Authoring New Components" in `skills/components/SKILL.md`.

### `component-form`: "I don't know how to render the `<type>` field"

**Symptom:** A prompt like *"create a profile form with an avatar file upload and a colour picker for the accent"* triggers the skill but halts with an unsupported-field-type warning.

**Cause:** `component-form` v1 supports a fixed grammar of 11 field types — `text`, `email`, `password`, `tel`, `url`, `number`, `date`, `textarea`, `select`, `checkbox`, `radio` (see `## Field types` in the form SKILL). Anything outside that set (today: `type="file"`, `type="color"`, `type="range"`) is surfaced as a gap rather than silently emitted as a plain `<input>`.

**Fix:** Either restate the prompt using a recognised field type (most everyday fields fit — phone numbers as `tel`, dates of birth as `date`, quantities as `number`), or for the unsupported types drop the native element directly into the generated form (`<input type="file" />` / `<input type="color" />` / `<input type="range" />`) — they don't need an `Input`-component wrapper. For full hand-authored control, run `/kit-add field input` to vendor the primitives.

### `style-tune`: "I don't recognise that adjective" / "component out of v1 scope"

**Symptom:** A prompt like *"make the badges feel more luxurious"* halts. Reasons fall into two buckets: an unknown modifier, or a component outside the v1 coverage table.

**Cause:** `style-tune` v1 covers six components (Button, Card, Alert, Dialog, Input, Nav) across six token families (color, radius, spacing, elevation, size, height) — see [`skills/style-tune/references/intent-vocabulary.md`](../skills/style-tune/references/intent-vocabulary.md). Components like Badge, Tag, Field, Checkbox, Icon, Link, List, Popover, Table, Img fall through to a v2 hint, and modifiers outside the published vocabulary refuse rather than guess.

**Fix:** For an unsupported component, edit its CSS variables directly. Field, Checkbox, Icon, Link, List, Popover, Table, and Img each have a dedicated reference doc that lists their custom properties under `## CSS Variables`. Badge and Tag are inline-only entries in `references/components/catalog.md` — for those, vendor with `/kit-add badge` (or `/kit-add tag`) and edit the generated `.scss` directly. For an unsupported modifier, restate using a v1 phrase from the vocabulary table — *"warmer"*, *"softer"*, *"more spacious"*, *"more elevated"*, *"tone down"*, *"sharper"*, *"quieter"*, *"bolder"*, *"smaller"*, *"bigger"*, *"narrower"*, *"wider"*, *"shorter"*, *"taller"*.
