# Raise `skillListingBudgetFraction` to 0.05 (project settings)

## Context

Claude Code's default `skillListingBudgetFraction` is `0.01` — about 1% of the model's context window (~8K chars on a 200K-token window) is reserved for the per-turn listing of every installed skill's `description:` frontmatter. This repo's environment has ~193 SKILL.md files installed (184 cached plugin skills + 9 user skills), which leaves only ~41 chars per skill before descriptions start being truncated or dropped entirely.

When a skill description is truncated, the activation triggers ("Use when…", capability verbs) get cut, which in turn causes Claude to miss skill matches that should fire. The Claude Code binary (v2.1.138) emits a runtime warning recommending `/skills` to disable some, **or raise `skillListingBudgetFraction`** — the user is acting on that hint.

The setting is currently absent from every settings file in scope:

<ul>
<li><code>/Users/shawnsandy/.claude/settings.json</code> (global user)</li>
<li><code>/Users/shawnsandy/devbox/acss-plugins/.claude/settings.json</code> (this project)</li>
<li><code>/Users/shawnsandy/devbox/acss-plugins/.claude/settings.local.json</code> (project local)</li>
</ul>

So the 1% the user references is the binary's built-in default, not an explicit configuration.

## Objective

Add a top-level `"skillListingBudgetFraction": 0.05` key to the project's `.claude/settings.json` so that — when working in `acss-plugins` — Claude Code allocates ~5% of the context window (~40K chars) to skill listings. At ~193 installed skills, this yields ~207 chars per skill: enough headroom for the 160-char description target the `optimizing-descriptions` skill pursues, plus room for future skill installs. Cost: ~8K extra prompt-cache prefix tokens per session.

## Files to modify

<ul>
<li><a href="../../.claude/settings.json">/Users/shawnsandy/devbox/acss-plugins/.claude/settings.json</a> — add one top-level key alongside the existing <code>hooks</code> block.</li>
</ul>

## Steps

<ol>
<li>
<strong>Add the <code>skillListingBudgetFraction</code> key to <code>.claude/settings.json</code>.</strong>
Insert <code>"skillListingBudgetFraction": 0.05</code> as a new top-level sibling of the existing <code>"hooks"</code> object (insert before <code>hooks</code> for readability — top-level scalar settings before the larger hooks block).
<ul>
  <li><em>Why:</em> placing it at the top level (not nested) is what Claude Code's settings loader reads. <code>0.05</code> raises the per-turn skill-listing budget from ~8K to ~40K chars, comfortably fitting all ~193 installed skills' descriptions at the 160-char target.</li>
  <li><em>Verify:</em> run <code>jq '.skillListingBudgetFraction' /Users/shawnsandy/devbox/acss-plugins/.claude/settings.json</code> and confirm the output is exactly <code>0.05</code> (not <code>null</code>, not a string).</li>
</ul>
</li>

<li>
<strong>Confirm the file is still valid JSON and the existing <code>hooks</code> block is intact.</strong>
The PostToolUse JSON-validation hook on this very file (lines 27–36 of the current file) will run automatically on save; no separate command needed, but cross-check manually.
<ul>
  <li><em>Why:</em> a typo (trailing comma, mismatched brace) would silently disable every hook in the project — the branch-guard PreToolUse hook is what blocks commits to <code>main</code>, and losing it is a real-world risk.</li>
  <li><em>Verify:</em> run <code>python3 -c "import json; d=json.load(open('/Users/shawnsandy/devbox/acss-plugins/.claude/settings.json')); print(sorted(d.keys())); print(len(d['hooks']['PostToolUse']), 'PostToolUse hooks'); print(len(d['hooks']['PreToolUse']), 'PreToolUse hook(s)')"</code> and confirm: keys include both <code>hooks</code> and <code>skillListingBudgetFraction</code>, PostToolUse count is <code>6</code>, PreToolUse count is <code>1</code>.</li>
</ul>
</li>
</ol>

## Verification

End-to-end confirmation that the change took effect:

<ul>
<li><strong>File-level:</strong> <code>jq '{skillListingBudgetFraction, hookCount: (.hooks.PostToolUse | length)}' /Users/shawnsandy/devbox/acss-plugins/.claude/settings.json</code> returns <code>{"skillListingBudgetFraction": 0.05, "hookCount": 6}</code>.</li>
<li><strong>Runtime:</strong> in a fresh Claude Code session opened in <code>/Users/shawnsandy/devbox/acss-plugins</code>, run <code>/doctor</code> and confirm no skill-listing-truncation warnings are present (the warning that prompted this change should be gone).</li>
<li><strong>Spot-check skill activation:</strong> ask Claude something that should trigger a skill whose description sits in the 150–200 char range (e.g. <code>skill-reviewer:optimizing-descriptions</code>, whose description starts with "Rewrites <code>description:</code> frontmatter…" — this skill activated correctly in this session, but its full trigger text was previously vulnerable to truncation). Confirm the skill is offered/runs without needing to be invoked by full slug.</li>
<li><strong>No regressions:</strong> attempt a <code>git commit</code> on a non-<code>main</code> feature branch — the PreToolUse branch-guard hook should still allow it. Attempt a <code>git commit</code> while on <code>main</code> — it should still be blocked.</li>
</ul>

## Next steps (out of scope)

<ul>
<li>If <code>/doctor</code> still shows truncation in this session despite the new setting, consider raising further to <code>0.07</code> or running the <code>skill-reviewer:optimizing-descriptions</code> skill across installed plugins to shorten descriptions.</li>
<li>Mirror this setting into <code>~/.claude/settings.json</code> (global user) so other projects on this machine benefit — currently scoped only to <code>acss-plugins</code> per the user's choice.</li>
<li>Document the chosen value and its rationale in the project's <code>CLAUDE.md</code> if other contributors are expected to inherit this configuration.</li>
</ul>
