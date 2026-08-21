---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0016 — Hand the agent its permissions as a launch argument

**Status:** Accepted

## Context

A scenario runs the real agent headlessly: the harness (`ClaudeCli`) shells out to `claude -p` with `--permission-mode acceptEdits` and no human at the keyboard. The agent is allowed to run tests because the scene ships a `.claude/settings.json` whose `permissions.allow` carries `Bash(uv run pytest*)` — a deliberately narrow grant, the only command the task needs (ADR [0009](0009-select-inspector-and-agent-per-run-via-pytest-cli-options.md) selects the agent; this is how that agent is permitted to act).

Claude Code **2.1.193** introduced a **workspace-trust gate**. The gate keys on provenance: `permissions.allow` entries in a `.claude/settings.json` the CLI *discovers* in a workspace are ignored until that workspace has been trusted, because nobody has vouched for content found lying in a directory.

Each scenario copies the scene into a fresh temporary workspace per run, with the agent's cwd at that workspace root (ADR [0008](0008-run-the-agent-with-cwd-at-the-workspace-root.md)). A brand-new temporary directory has never been trusted, so the scene's file is always discovered content and its grant is always dropped.

The net effect: the agent's `uv run pytest` falls through to an approval prompt, and headless `-p` with no human to approve denies it. The agent cannot run the test, so the scenario's "ran pytest" / "FAILED result" characteristics fail for a reason unrelated to the agent's behaviour under test.

Measured on 2.1.220: a bare `uv run pytest` — an exact prefix match for the grant — returns `This command requires approval`, and the agent reports its red as unverified. A matching rule that denies is a rule that was never consulted.

## Decision

The harness passes the scene's settings file to `claude` as a launch argument: `--settings <workspace>/.claude/settings.json`.

Settings supplied as an argument are not discovered content — the invoker hands them over — so the trust gate does not apply. Measured on 2.1.220: passed this way, `Bash(uv run pytest*)` applies and the agent runs its test on the first attempt.

`ClaudeCli` works the path out from the workspace it is already handed, and passes `--settings` only when a file is there. No caller has to know that a scene keeps its settings at `.claude/settings.json`, and a caller running against a bare workspace — the contract and integration tests among them — is unaffected.

Supplying the permissions is environment setup the harness owns, alongside the cwd it sets (ADR [0008](0008-run-the-agent-with-cwd-at-the-workspace-root.md)) and the `--add-dir` directories it passes — not a property of the scene. The scene keeps expressing *what* the agent may do; the harness makes that grant effective by handing it over.

## Consequences

- The scene's narrow allow-list stays the single source of truth for what the agent may run. Passing the file by path neither moves the list into harness code nor widens it.
- The harness writes nothing outside the workspace under test. No shared state is mutated, so parallel scenarios do not contend and nothing accumulates between runs.
- The decision rests on `--settings`, a published command-line interface, rather than on the shape of the CLI's internal configuration state.
- The flag is pinned by a unit test over the composed command, and exercised end-to-end by the real-agent scenarios, which run a real `claude` in a workspace that has never been trusted.

## Alternatives considered

- **Mark the workspace trusted in the user-level configuration** (`projects["<workspace>"].hasTrustDialogAccepted = true` in `~/.claude.json`): satisfies the gate, and the grant then applies. Rejected: it modifies the wider environment in order to run an isolated test. It writes to shared state on every run, which parallel scenarios must lock against and which accumulates an entry per temporary workspace without pruning, and it depends on an internal configuration key rather than a published interface.
- **Pass the settings path into `ClaudeCli` from its caller**: the caller is what knows a scene keeps its settings at `.claude/settings.json`, so that knowledge would sit with the code owning the scene rather than in the CLI wrapper. Rejected for now: `ClaudeCli` is already handed the workspace, so it can work the path out without a new parameter, and adding one threads an argument through every caller and test double before anything works. Nothing yet needs a settings file anywhere else; when something does, the parameter is a small local change at that point.
- **Hand-list the permitted tools on the CLI (`--allowedTools "Bash(uv run pytest*)"`)**: also escapes the gate, but takes *what the agent may do* out of the scene — where it is reviewed alongside the rest of the task fixture — and into harness wiring, where every scenario shares one list. Rejected.
- **`--add-dir`**: widens the directories tools may access. It does not grant permission to run a command, so it cannot carry the allow-list.
- **`--dangerously-skip-permissions` / `--permission-mode bypassPermissions`**: one flag and no file to pass, but it bypasses *all* permission checks. The scene's allow-list is then inert and the agent could run anything — discarding the deliberate constraint the scenario is built around. Rejected: it removes the very thing the scene is asserting.
- **Pin below 2.1.193**: the gate is a deliberate upstream security feature, unlikely to be reverted; holding the pin to dodge it forgoes later fixes and only defers the problem (counter to ADR [0002](0002-pin-claude-code-cli-version.md)'s migrate-deliberately stance). Rejected.
- **Trust the workspace by hand before each run**: accepting the dialog interactively, or hand-editing configuration, defeats the point of a headless, repeatable scenario suite. Rejected.
