---
description: Convert an inline style attribute, JSX style object, or <style> block into a named CSS class and append it to the project stylesheet, replacing hard-coded values with CSS variables
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

Convert an inline `style` attribute, JSX `style` object, or `<style>` block into a single named CSS class appended to the project stylesheet. Hard-coded colors, units, and values are replaced with CSS variables — reusing an existing variable when one matches, creating a new one when none does.

**IDE selection supported:** select an element or style block in your editor (VS Code, JetBrains), then run `/inline-style-to-class [name]`. The skill reads the selection, generates the class, and edits the source file in-place — replacing the inline style with the new class reference.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/inline-style-to-class/SKILL.md`.

All behavior — argument handling, input parsing, name rules, stylesheet and variable discovery, value tokenizing, class emission, new-variable declaration, file append, HTML/JSX refactoring, and summary output — is defined in the skill file above.
