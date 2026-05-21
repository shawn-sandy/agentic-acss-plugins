---
name: acss-kit-component-author
description:
  "[Maintainer] Use when the maintainer asks to add a component to acss-kit —
  scaffolds a reference doc under references/components in the canonical
  embedded-markdown shape."
disable-model-invocation: false
---

# /acss-kit-component-author

Usage: `/acss-kit-component-author <component-name>`

Example: `/acss-kit-component-author tabs`

Scaffolds `plugins/acss-kit/skills/component-<component-name>/` with `SKILL.md`
and `reference.md` (all nine canonical sections). Does NOT implement the
TSX/SCSS — the maintainer fills those in after consulting the upstream fpkit
source.

## Steps

1. **Validate inputs.**
   - `<component-name>` must be lowercase kebab-case (alphanumeric + hyphens).
   - Refuse if `plugins/acss-kit/skills/component-<component-name>/` already
     exists.

2. **Capture the fpkit ref via AskUserQuestion.** Ask the maintainer for the
   fpkit version this reference will be verified against. Default to the
   most-common existing ceiling — read the verification banner of
   `plugins/acss-kit/skills/component-button/reference.md` (line ~3) and offer
   that as the default option (currently `@fpkit/acss@6.5.0`).
   Capture the answer as `<ref>` for the banner and as `<tag-or-sha>` for any
   GitHub URLs in the body.

3. **Capture intentional divergences via AskUserQuestion.** Ask whether this
   component will diverge from upstream in any documented way (inlined hooks,
   simplified compound API, dropped subcomponents, etc.). Default: "none".
   Capture as `<divergences>`. The verification banner is load-bearing for
   future maintainers — if there are no divergences, write "none" rather than
   leaving the field empty.

4. **Write the skill directory.** Create
   `plugins/acss-kit/skills/component-<component-name>/` and write two files:

   a. **`SKILL.md`** — mirror the shape of `plugins/acss-kit/skills/component-button/SKILL.md`:
      - frontmatter (in this order):
        - `name: component-<component-name>`
        - `description:` (one line, under 160 chars, "Use when the user asks to generate, create, or scaffold a <PascalCaseName>…")
        - `disable-model-invocation: true` (component-tier skills are hidden from auto-context; dispatched by exact name from the orchestrator — see `.claude/rules/skill-front-matter.md`)
        - `hint: >-` (folded scalar describing invocation surfaces and component-specific details). Template:
          ```yaml
          hint: >-
            Invoke explicitly via `/kit-add <component-name>`, `/kit-create`
            (then ask for a <component-name>), or call the
            `component-<component-name>` skill by name. Describe
            <component-specific details — variant, size, state, slots>.
          ```
        - `allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion`
      - Workflow: 5-step workflow (Read reference.md → init check → dep resolution → generate → verify)
      - Reference section linking to `reference.md` and `kit-core/references/`

   b. **`reference.md`** — the reference doc skeleton with all nine canonical sections:
   Outer fence uses 4 backticks so the inner triple-backtick blocks render
   correctly:

   ````markdown
   # Component: <PascalCaseName>

   > **Verified against fpkit source:** `<ref>`. Intentional divergences from
   > upstream: <divergences>.

   ## Overview

   <One-paragraph summary of the component's purpose. Note key WCAG patterns it
   addresses.>

   ## Generation Contract

   ```
   export_name: <PascalCaseName>
   file: <component-name>.tsx
   scss: <component-name>.scss
   imports: UI from '../ui'
   dependencies: []
   ```

   ## Props Interface

   ```tsx
   export type <PascalCaseName>Props = {
     children?: React.ReactNode
     // TODO: copy props from fpkit source at <ref>
   } & React.ComponentPropsWithoutRef<'div'>
   ```

   ## TSX Template

   ```tsx
   // TODO: copy from https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/components/<component-name>/<component-name>.tsx
   import React from 'react'
   import UI from '../ui'

   export default function <PascalCaseName>({ children, ...rest }: <PascalCaseName>Props) {
     return <UI as="div" {...rest}>{children}</UI>
   }
   ```

   ## CSS Variables

   ```scss
   // CSS custom properties this component reads
   // --<component-name>-bg
   // --<component-name>-color
   // (extend with the full variable list)
   ```

   ## SCSS Template

   ```scss
   // TODO: copy from https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/components/<component-name>/<component-name>.scss
   .<component-name> {
     background: var(--<component-name>-bg, transparent);
     color: var(--<component-name>-color, currentColor);
   }
   ```

   ## Accessibility

   - Keyboard interaction: <TODO>
   - ARIA: <TODO>
   - Focus management: <TODO>
   - Target size: <TODO>
   - Color contrast: <TODO>
   - WCAG 2.2 AA criteria addressed: <TODO>

   ## Usage Examples

   ```tsx
   import <PascalCaseName> from './<component-name>/<component-name>'
   import './<component-name>/<component-name>.scss'

   <<PascalCaseName>>Hello</<PascalCaseName>>
   ```
   ````

   Substitute `<component-name>`, `<PascalCaseName>`, `<ref>`, `<tag-or-sha>`,
   and `<divergences>` at write time. Leave every `TODO:` marker for the
   maintainer to fill in. The Usage Examples import path uses
   `./<component-name>/<component-name>` to match the convention in existing
   reference docs (e.g. `button.md`, `alert.md`) — the `src/components/fpkit/`
   portion is the project-level path the developer chose during `/kit-add`
   initialization, not part of the relative import.

5. **Run the reviewer agent.** Invoke the `component-reference-reviewer` agent
   against the new file. Expected outcome on a fresh skeleton: all checks PASS
   except possibly TSX Template imports (the placeholder uses only React +
   `'../ui'`, which should pass). Surface the agent's report inline.

7. **Print a summary.**
   - Files created: `skills/component-<component-name>/SKILL.md`, `skills/component-<component-name>/reference.md`
   - Reminders:
     - Resolve every `TODO:` placeholder before committing.
     - If the component has dependencies (e.g. wraps Button), update the
       `dependencies:` field in the Generation Contract and Step 3 of the SKILL.md workflow.
     - Re-run `/review-component <path>` after filling in the TSX/SCSS
       templates.

Do not write the TSX or SCSS implementation — those come from the upstream fpkit
source at the captured ref. The maintainer fills them in.
