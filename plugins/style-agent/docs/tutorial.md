# style-agent — Tutorial: your first class

Turn a plain-language description into utility classes, collapse utility soup into one named class, and migrate hard-coded inline styles into variable-driven CSS — in any web project, in a few minutes. No framework lock-in, no install step beyond the plugin itself.

If you want the command list first, see the [README](README.md). Otherwise, start here.

---

## Before you start

Prerequisites:

- Any web project with CSS — plain CSS, SCSS, Tailwind, or Bootstrap. The skills are framework-agnostic.
- `style-agent` installed via `/plugin install style-agent@shawn-sandy-agentic-acss-plugins`
- Claude Code open in your project directory

Unlike `acss-kit`, there is **no `/setup`, no config file, and no React/sass requirement**. The skills read your existing files at call time — they grep your `.css` to resolve classes and detect your stylesheet conventions on the fly.

This walkthrough chains all three commands in the order they naturally compose: **describe → consolidate → migrate**.

---

## Step 1 — Generate utilities from a description (`/create-utilities`)

```
/create-utilities "a centered flex row with 1rem padding, primary background, and rounded corners"
```

The skill will:

1. Detect your utility vocabulary — acss-kit, Tailwind, or Bootstrap; if none is found it falls back to Tailwind-compatible names (the de-facto standard).
2. Map the description to specific classes, ordered **layout → spacing → color → typography → border → shadow → state**.
3. Print a class string plus a one-line HTML example.

Illustrative output (Tailwind vocabulary):

```text
flex items-center p-4 bg-primary rounded
```

```html
<div class="flex items-center p-4 bg-primary rounded">…</div>
```

Why start here? You don't hand-pick class names you can describe. This skill **writes nothing** — it hands you a string to use. If the element is interactive (button, link, input), it also adds a framework-appropriate focus class and explains the choice in an `# a11y` note.

---

## Step 2 — Collapse the utility soup into one named class (`/css-to-class`)

The output of Step 1 is a class string — the exact input `/css-to-class` consolidates. The `[name]` argument is optional:

```
/css-to-class card-row "flex items-center p-4 bg-primary rounded"
```

The skill will:

1. Find every `.css` file in your project (excluding `node_modules`, `dist`, `build`, `.git`).
2. Resolve each utility token to its real declarations by grepping those files.
3. Emit one named class with resolved declarations inlined; any token it can't find becomes a `/* token: add declarations manually */` placeholder, kept in position.
4. Rewrite the element to use the single class.

Illustrative output (your project's CSS supplies the actual values):

```css
/* extracted: flex items-center p-4 bg-primary rounded */
.card-row {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--color-primary);
  border-radius: 0.5rem;
}
```

```html
<div class="card-row">…</div>
```

Notice two things:

- **The name is sanitised.** `card-row` is kebab-case, 20 chars max. Omit the argument and the skill auto-generates a name from the semantic tokens — asking you to confirm when the list is all-utility or the guess is ambiguous.
- **At-rule context is preserved.** If a token resolves inside an `@media`/`@supports`/`@layer` block in your source CSS, the generated class keeps that wrapper as a nested block — the declaration won't silently stop working at its breakpoint.

Still **read-only**: it prints the block and the refactored HTML; you decide where they land.

---

## Step 3 — Migrate inline styles instead (`/inline-style-to-class`)

The inverse direction — for styles already hard-coded on an element. This is the one command that **writes to your stylesheet**.

```
/inline-style-to-class hero-bg
```

…with the element selected in your editor, or pasted:

```html
<div style="background: #4f46e5; padding: 1.5rem; border-radius: 8px">
```

The skill will:

1. Detect your project stylesheet — preferring an entry file named `globals`, `main`, `index`, `styles`, `app`, or `base`; asking via a prompt only when the choice is ambiguous.
2. Tokenize **every concrete value** into a CSS variable — reusing an existing variable when one already holds that value, creating a new one (in your `tokens`/`variables` file or a `:root` block) when none does.
3. Keep the original literal as the `var()` fallback.
4. Append the class to the stylesheet and strip the inline `style` from your source — **in place** when run from an IDE selection.

Appended to your stylesheet:

```css
.hero-bg {
  background: var(--color-1, #4f46e5);
  padding: var(--space-1, 1.5rem);
  border-radius: var(--radius-1, 8px);
}
```

…and the element becomes:

```html
<div class="hero-bg">
```

Why variables-with-fallback? The fallback means the migrated class is **never more fragile than the inline style it replaced** — even with the variable undefined, it renders identically. Reuse-or-create keeps your token set from sprouting duplicate variables for the same value.

---

## Verify

The decisive check is what each command touches on disk:

```bash
git status   # after Steps 1 and 2: clean. They hand you code; they don't write it.
git diff     # after Step 3: shows the real changes.
```

After `/inline-style-to-class`, `git diff` should show three things:

- The new `.hero-bg` class appended to your detected stylesheet.
- Any new variables declared in your tokens file or a `:root` block (reused variables are not re-declared).
- The inline `style` attribute removed from the source element, replaced by `class="hero-bg"`.

Open the page: the element renders **identically** to before. The `var()` fallbacks guarantee it even if a variable is missing.

---

## Where to next

You have generated, consolidated, and migrated CSS without touching a framework config. From here:

- [README](README.md) — install and the full command table.
- [COMPONENT.md spec](component-md/spec.md) — the framework-neutral component format style-agent publishes, themed by a sibling [DESIGN.md](https://github.com/google-labs-code/design.md). Together they form a two-file design system: DESIGN.md owns tokens, COMPONENT.md owns components.
- **Pair with `acss-kit`** — in a React + fpkit project, `acss-kit`'s `/utility-add` ships the `utilities.css` bundle that `/create-utilities` and `/css-to-class` then detect and resolve against.
