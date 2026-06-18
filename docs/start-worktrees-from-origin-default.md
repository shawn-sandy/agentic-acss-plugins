# Start Worktrees From Origin's Default Branch

A guide to the SessionStart hook that snaps a fresh worktree branch onto `origin/<default>` so every session begins from the latest default branch — what it does, why it exists, how it fires, and how to apply it.

> **Origin.** Written 2026-06-18 from a working session. The prompt was a single question: *"Can we always ensure that worktrees are created from the default origin?"* Investigation found sibling worktrees sitting 15, 22, and 80 commits behind `origin/main`. The existing SessionStart hook freshened the local `main` ref but never moved the worktree's own branch onto it. We added a guarded `git reset --hard` to close that gap and verified every branch of the logic before shipping. This guide captures the rule and its edges.

> **Per-user, not in this repo.** The hook this guide documents lives in `~/.claude/settings.json` — a personal, machine-local file under your home directory. It is **not** committed to `acss-plugins`, and a teammate who clones this repo will not have it. Every `~/.claude/...` path below is per-user. The repo's own committed `.claude/settings.json` has **no** `SessionStart` hook (verified: `grep -c SessionStart .claude/settings.json` → `0`), so the freshness behavior described here comes entirely from the user-level config and does not travel with the repository.

---

## Table of contents

1. [The rule in one sentence](#1-the-rule-in-one-sentence)
2. [What it is](#2-what-it-is)
3. [Why it exists](#3-why-it-exists)
4. [How it works structurally](#4-how-it-works-structurally)
5. [How it fires](#5-how-it-fires)
6. [Decision criteria](#6-decision-criteria)
7. [Operational script](#7-operational-script)
8. [Boundaries](#8-boundaries)
9. [Interactions with related systems](#9-interactions-with-related-systems)
10. [Project-specific context (acss-plugins)](#10-project-specific-context-acss-plugins)
11. [Maintenance and audit](#11-maintenance-and-audit)
12. [Verification protocol](#12-verification-protocol)

---

## 1. The rule in one sentence

**At session start, a clean worktree branch with no commits of its own is reset onto `origin/<default>` — so work always begins from the freshest default branch, never a stale checkout.**

Everything below unpacks that sentence.

The word *clean* and the clause *with no commits of its own* are the entire safety story: they are the two guards that decide whether the reset fires or the branch is left untouched.

---

## 2. What it is

A single `command` hook on the **SessionStart** event in `~/.claude/settings.json` (per-user). De-escaped and commented for reading — the stored value is a single line with no comments:

```bash
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
test -n "$DEFAULT_BRANCH" || exit 0
CURRENT=$(git branch --show-current 2>/dev/null)

if [ "$CURRENT" = "$DEFAULT_BRANCH" ]; then
  # On the default branch itself — just fast-forward it.
  git pull --ff-only origin "$DEFAULT_BRANCH" 2>/dev/null \
    && echo "OK: $DEFAULT_BRANCH is up to date with origin"
else
  # On a worktree / session branch — freshen the default ref first.
  git fetch origin "$DEFAULT_BRANCH":"$DEFAULT_BRANCH" 2>/dev/null
  BEHIND=$(git rev-list --count HEAD.."$DEFAULT_BRANCH" 2>/dev/null)
  if [ -z "$(git status --porcelain)" ] \
     && [ "$(git rev-list --count "$DEFAULT_BRANCH"..HEAD 2>/dev/null)" = "0" ]; then
    # Clean tree AND no commits of its own → safe to snap onto origin's default.
    git reset --hard "$DEFAULT_BRANCH" >/dev/null 2>&1
    if [ -n "$BEHIND" ] && [ "$BEHIND" != "0" ]; then
      echo "OK: reset $CURRENT to origin/$DEFAULT_BRANCH (was $BEHIND behind)"
    else
      echo "OK: $CURRENT already at origin/$DEFAULT_BRANCH"
    fi
  else
    # Has local commits or a dirty tree → leave it alone.
    echo "OK: origin/$DEFAULT_BRANCH fetched; $CURRENT kept (local commits or dirty tree)"
  fi
fi || true
```

The exact value of the `command` field as stored in `~/.claude/settings.json` (JSON-escaped, single line, `"timeout": 15`):

```text
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0; DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'); test -n \"$DEFAULT_BRANCH\" || exit 0; CURRENT=$(git branch --show-current 2>/dev/null); if [ \"$CURRENT\" = \"$DEFAULT_BRANCH\" ]; then git pull --ff-only origin \"$DEFAULT_BRANCH\" 2>/dev/null && echo \"OK: $DEFAULT_BRANCH is up to date with origin\"; else git fetch origin \"$DEFAULT_BRANCH\":\"$DEFAULT_BRANCH\" 2>/dev/null; BEHIND=$(git rev-list --count HEAD..\"$DEFAULT_BRANCH\" 2>/dev/null); if [ -z \"$(git status --porcelain)\" ] && [ \"$(git rev-list --count \"$DEFAULT_BRANCH\"..HEAD 2>/dev/null)\" = \"0\" ]; then git reset --hard \"$DEFAULT_BRANCH\" >/dev/null 2>&1; if [ -n \"$BEHIND\" ] && [ \"$BEHIND\" != \"0\" ]; then echo \"OK: reset $CURRENT to origin/$DEFAULT_BRANCH (was $BEHIND behind)\"; else echo \"OK: $CURRENT already at origin/$DEFAULT_BRANCH\"; fi; else echo \"OK: origin/$DEFAULT_BRANCH fetched; $CURRENT kept (local commits or dirty tree)\"; fi; fi || true
```

The four moving parts:

- **`DEFAULT_BRANCH`** — resolved from `refs/remotes/origin/HEAD`, never hard-coded. On this repo it resolves to `main` (verified: `git symbolic-ref refs/remotes/origin/HEAD` → `refs/remotes/origin/main`).
- **`CURRENT`** — the branch checked out in this worktree (`git branch --show-current`).
- **`BEHIND`** — `git rev-list --count HEAD..$DEFAULT_BRANCH`: how many commits the default branch is *ahead of* this worktree. Used only for the human-readable message.
- **The guard** — empty `git status --porcelain` (clean tree, no untracked files) **and** `git rev-list --count $DEFAULT_BRANCH..HEAD` equal to `0` (no commits unique to this branch).

---

## 3. Why it exists

`git worktree add <path>`, with no commit-ish, bases the new branch on **`HEAD`** — not on origin. The official git-worktree documentation says so directly:

> "If _<branch>_ doesn't exist, a new branch based on **`HEAD`** is automatically created…"

Nothing fetches first. So whatever commit the repository happens to be sitting on at creation time becomes the new worktree's base. If that local checkout is stale, the worktree is born stale, and it stays stale until something moves it.

The evidence that triggered this work, read straight off `git branch -vv` during the session:

| Worktree branch | State vs. `origin/main` |
| --- | --- |
| `claude/beautiful-chebyshev-9c03a4` | `behind 15` |
| `claude/suspicious-mccarthy-ca7865` | `behind 22` |
| `claude/zen-tesla-7650ba` | `behind 80` |

The prior version of this hook already fetched origin. But on a worktree branch it ran only `git fetch origin main:main` — which updates the local `main` ref and leaves the checked-out branch exactly where it was. Local `main` got fresh; the branch you were actually working on did not. That asymmetry is the whole bug: the hook kept the wrong ref current.

This also serves a standing rule in the author's global instructions:

> "Unless otherwise specified, always pull the latest of the default branch from origin before starting any work."

For the default branch, the old hook honored that. For worktree branches, it did not. The added reset extends the same guarantee to every session branch.

---

## 4. How it works structurally

```text
SessionStart fires
  │
  ├─ not inside a git work tree? ................. exit 0  (no-op)
  ├─ origin/HEAD unset (no DEFAULT_BRANCH)? ...... exit 0  (no-op)
  │
  ├─ CURRENT == DEFAULT_BRANCH  (you are on main)
  │     └─ git pull --ff-only origin main
  │          └─ "OK: main is up to date with origin"
  │
  └─ CURRENT != DEFAULT_BRANCH  (you are on claude/<slug>)
        └─ git fetch origin main:main          (freshen the local default ref)
             └─ clean tree  AND  0 commits ahead of main?
                  ├─ YES → git reset --hard main
                  │          ├─ was behind   → "reset <branch> to origin/main (was N behind)"
                  │          └─ already there → "<branch> already at origin/main"
                  └─ NO  → "origin/main fetched; <branch> kept (local commits or dirty tree)"
```

Why `reset --hard` and not `rebase`: the reset only ever runs when the branch has **zero** unique commits, so there is nothing to replay. In that state, `reset --hard <default>` is a pure fast-forward in effect — it moves the branch pointer up to origin's tip. The git-reset documentation describes the operation as: *"Overwrite all files and directories with the version from <commit>… Tracked files not in <commit> are removed so that the working tree matches <commit>."* That sounds destructive, and it is — which is exactly why the two guards gate it.

The range notation does the heavy lifting. Per the git-rev-list docs, `A..B` means *"commits reachable from B but not from A,"* and `--count` *"print[s] a number stating how many commits would have been listed."* So:

| Expression | Reads as | Used for |
| --- | --- | --- |
| `git rev-list --count $DEFAULT_BRANCH..HEAD` | commits on this branch not in default | the **guard** (must be `0`) |
| `git rev-list --count HEAD..$DEFAULT_BRANCH` | commits in default not on this branch | the **`BEHIND`** message count |

---

## 5. How it fires

The hook is registered with **no matcher**, so it runs on every `SessionStart` trigger. Per the Claude Code hooks reference, SessionStart *"runs when Claude Code starts a new session or resumes an existing session"* with these source values:

- `startup` — a new session
- `resume` — `--resume`, `--continue`, or `/resume`
- `clear` — `/clear`
- `compact` — auto or manual compaction

Any of those fires it. What **prevents** the reset from happening, in order of the checks:

1. **Not a git work tree** — `git rev-parse --is-inside-work-tree` fails → `exit 0`.
2. **No `origin/HEAD`** — `DEFAULT_BRANCH` comes back empty → `exit 0`. Fresh clones sometimes lack this ref; set it with `git remote set-head origin -a`.
3. **You are on the default branch** — takes the fast-forward-pull path instead, never the reset path.
4. **Dirty tree or untracked files** — `git status --porcelain` is non-empty → skip, branch kept.
5. **Branch has its own commits** — `$DEFAULT_BRANCH..HEAD` count is non-zero → skip, branch kept.

The trailing `|| true` guarantees the hook never fails the session, regardless of network state or git errors. Offline, the `fetch` simply fails and is ignored (it is followed by `;`, not `&&`); the branch is then evaluated against the **local** default ref, so at worst you start from the last-known-local default rather than a broken startup.

---

## 6. Decision criteria

> *Does this worktree branch carry work of its own, or is it a fresh checkout off a stale base?*

That question is the hinge. The hook answers it with two cheap git queries and branches five ways.

### Fresh and behind → reset (the point of the whole thing)

Clean tree, zero unique commits, and `origin/<default>` has moved ahead. The branch is snapped forward and you see `reset <branch> to origin/main (was N behind)`. This is the case that fixed the 15/22/80-behind worktrees.

### Fresh and already current → no-op reset

Clean tree, zero unique commits, already at origin's tip. The `reset --hard` runs but moves nothing; you see `<branch> already at origin/main`. Verified live: HEAD `9e5b756` → `9e5b756`, unchanged.

### Has its own commits → skip (data-loss protection)

`$DEFAULT_BRANCH..HEAD` is non-zero, so the branch holds work that is not in the default. The reset is skipped and you see `origin/main fetched; <branch> kept (local commits or dirty tree)`. Verified live: `claude/amazing-austin-6e776c` reported `ahead-of-main=3` and was classified **SKIP**.

### Dirty tree → skip

Uncommitted or untracked changes make `git status --porcelain` non-empty. Even a branch with zero unique commits is left alone so an in-progress edit is never overwritten. This guard matters because `reset --hard` *can* remove untracked files; the porcelain check forecloses that path entirely.

### On the default branch → fast-forward pull

Not a reset case at all. `git pull --ff-only origin main` keeps `main` itself current and reports `main is up to date with origin`.

---

## 7. Operational script

The hook is automatic; the "operations" here are about reading it correctly and not fighting it.

- **DO** let the hook run — opening any session on a fresh worktree branch starts you on the latest default. No action required.
- **DO NOT** manually `git pull`/`rebase` a fresh worktree branch at the start of a session expecting the hook to have left it pinned; it may have already snapped it forward.

- **DO** read the hook's one-line output to learn what happened to your branch — `reset … (was N behind)` means it moved; `kept (local commits or dirty tree)` means it did not.
- **DO NOT** ignore a `kept` line when you expected a reset — it is telling you the branch has uncommitted changes or commits of its own.

- **DO** commit or stash work you want to keep in a worktree branch — committed work (unique commits) and uncommitted work (dirty tree) are both protected.
- **DO NOT** leave an intentionally-pinned-but-empty branch and expect the base to hold; a clean branch with no commits is, by design, a reset candidate on the next session start.

- **DO** run `git remote set-head origin -a` in a clone where the hook prints nothing — a missing `origin/HEAD` silently disables it.
- **DO NOT** hard-code a branch name into the hook; `origin/HEAD` resolution is what makes it portable across repos whose default is `master`, `develop`, etc.

---

## 8. Boundaries

What this hook explicitly does **not** do:

1. **Does not control `git worktree add`.** The base commit at creation is still `HEAD`; the hook corrects freshness *after the fact*, at the next session start — it does not make creation itself origin-aware.
2. **Does not touch a branch with its own commits.** Any unique commit (`$DEFAULT_BRANCH..HEAD` > 0) makes it skip.
3. **Does not touch a dirty or untracked tree.** A non-empty `git status --porcelain` makes it skip.
4. **Does not run outside a git work tree, or when `origin/HEAD` is unset.** Both are early `exit 0`.
5. **Does not rebase, and does not handle divergence.** A branch that is both ahead and behind is "ahead > 0," so it is skipped — not replayed onto the new base.
6. **Does not push or modify `origin`.** It only fetches and moves local refs.
7. **Does not alter the primary checkout beyond a fast-forward pull** when that checkout is on the default branch.
8. **Does not travel with any repository.** It is user-level config; see the per-user disclaimer at the top and §10.

---

## 9. Interactions with related systems

All paths in this section are **per-user** (`~/.claude/...`) unless stated otherwise — they live under the home directory, not in any repo a teammate clones.

- **SessionEnd settings-backup hook** (`~/.claude/settings.json`, per-user). Runs `bash $HOME/.claude/scripts/settings-backup.sh`. Because the SessionStart freshness hook lives in the same `settings.json`, edits to it are captured by this backup at session end — the hook's own source is versioned even though it is not in any project repo.
- **PreToolUse `main-guard`** (both per-user `~/.claude/settings.json` and the repo's committed `.claude/settings.json`). Blocks direct `git commit`/`git push` to `main`/`master`/`primary`. Complementary: the main-guard stops you writing *to* the default branch; the SessionStart hook keeps your worktree branch current *from* it.
- **Global standing rule** (per-user global `CLAUDE.md`): *"always pull the latest of the default branch from origin before starting any work."* The SessionStart hook is the automation of that rule for worktree branches.

---

## 10. Project-specific context (acss-plugins)

These facts are local to this repository, not general:

- The repo's own committed `.claude/settings.json` contains **no `SessionStart` hook** (verified: `grep -c SessionStart .claude/settings.json` → `0`). It ships only `PostToolUse` validators and a `PreToolUse` main-guard. So in this repo the freshness behavior is supplied entirely by the per-user hook — a contributor without it gets no auto-reset.
- This repo's `CLAUDE.md` documents the worktree convention the hook operates on:
  > "Claude Code on the web sessions develop on `claude/<slug>` branches assigned per session — push there, not to a hand-named feature branch."
  > "`.claude/worktrees/` is Claude Code session scratch — ignored by git."
- Those `claude/<slug>` branches are exactly the `CURRENT != DEFAULT_BRANCH` case in §4 — the population the reset path targets.
- `origin/HEAD` here resolves to `refs/remotes/origin/main`, so `DEFAULT_BRANCH` is `main` for every worktree in this repo.

---

## 11. Maintenance and audit

- **Update when default-branch detection changes.** The hook trusts `refs/remotes/origin/HEAD`. If a repo renames its default branch, run `git remote set-head origin -a` so the symbolic ref tracks the new name — no hook edit needed.
- **Revisit if you want rebase semantics.** Today a diverged branch (ahead > 0) is skipped. If you ever want behind-and-ahead branches replayed onto the new base, that is a `rebase` variant and a deliberate change — do not bolt it onto the reset path without re-guarding.
- **Prune if the worktree workflow ends.** If you stop using `claude/<slug>` worktree branches, the `CURRENT != DEFAULT_BRANCH` path stops mattering and the hook can shrink back to the plain fast-forward pull.
- **Audit cost is near zero.** The hook is two `rev-list --count` queries plus a `status --porcelain` — all local, all fast, inside the `"timeout": 15` budget.
- **Re-verify before trusting this doc.** It is a snapshot of `~/.claude/settings.json` on 2026-06-18. That file is per-user and mutable; confirm the current hook body matches §2 before relying on a detail here.

---

## 12. Verification protocol

The checks actually run this session. Re-run them after any edit to the hook.

**1. Settings JSON still parses** (a broken `settings.json` disables every hook):

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('valid JSON')"
# expect: valid JSON
```

**2. Dry-run the hook body in a worktree and confirm it is non-destructive when already current.** Paste the de-escaped body from §2 into a clean worktree whose branch sits at origin's tip, then:

```bash
git rev-parse --short HEAD   # before
# ...run the hook body...
git rev-parse --short HEAD   # after — must be identical
git status --porcelain       # must still be empty
```

Expected line: `OK: <branch> already at origin/main`. Observed this session: HEAD `9e5b756` → `9e5b756`, tree clean.

**3. Audit the reset-vs-skip decision across real branches** without mutating anything:

```bash
for b in <branch-with-commits> <stale-branch> HEAD; do
  ahead=$(git rev-list --count main..$b 2>/dev/null)
  [ "$ahead" = "0" ] && echo "$b: RESET (no unique commits)" \
                     || echo "$b: SKIP ($ahead unique commit(s) — protected)"
done
```

Expected: a branch with its own work prints `SKIP`; a purely-behind branch prints `RESET`. Observed this session: `claude/amazing-austin-6e776c` → `SKIP (3 unique commit(s))`; `claude/suspicious-mccarthy-ca7865` → `RESET`.

---

## Quick reference

```text
RULE: fresh worktree branch → starts from origin/<default> at session start

DEFAULT_BRANCH = basename(symbolic-ref origin/HEAD)   # never hard-coded
CURRENT        = git branch --show-current

           ┌─ not a git tree / no origin/HEAD ........ exit 0 (no-op)
           │
SessionStart┤  CURRENT == default ... pull --ff-only ... "up to date"
           │
           └─ CURRENT != default
                fetch origin <default>:<default>
                GUARD = (clean tree) AND (0 commits ahead of default)
                  GUARD true  + behind  → reset --hard → "reset … (was N behind)"
                  GUARD true  + current → reset --hard → "… already at origin/<default>"
                  GUARD false           → skip          → "… kept (local commits or dirty tree)"

PROTECTED (never reset):  own commits  |  dirty tree  |  untracked files
SCOPE: per-user ~/.claude/settings.json — NOT committed to any repo
PRECONDITION: origin/HEAD must be set →  git remote set-head origin -a
```

---

## Cross-references

External (verified 2026-06-18):

- Claude Code hooks reference — SessionStart event, command hook type: <https://code.claude.com/docs/en/hooks>
- `git worktree` — default base is `HEAD`: <https://git-scm.com/docs/git-worktree>
- `git reset` — `--hard` working-tree semantics: <https://git-scm.com/docs/git-reset>
- `git rev-list` — `--count` and `A..B` range notation: <https://git-scm.com/docs/git-rev-list>

Config files:

- `~/.claude/settings.json` — **per-user, not in this repo**; holds the SessionStart hook (§2), the SessionEnd settings-backup hook, and a PreToolUse main-guard.
- `.claude/settings.json` (committed, this repo) — PostToolUse validators + PreToolUse main-guard; **no SessionStart hook**.
- `CLAUDE.md` (this repo) — the `claude/<slug>` worktree convention and `.claude/worktrees/` scratch note (§10).
