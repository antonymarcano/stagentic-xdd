---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0016 — Trust the agent workspace so settings.json permissions apply in headless runs

**Status:** Proposed

## Context

A scenario runs the real agent headlessly: the harness (`ClaudeCli`) shells out to `claude -p` with `--permission-mode acceptEdits` and no human at the keyboard. The agent is allowed to run tests because the scene ships a `.claude/settings.json` whose `permissions.allow` carries `Bash(uv run pytest*)` — a deliberately narrow grant, the only command the task needs (ADR [0009](0009-select-inspector-and-agent-per-run-via-pytest-cli-options.md) selects the agent; this is how that agent is permitted to act).

Claude Code **2.1.193** introduced a **workspace-trust gate**: a project `.claude/settings.json`'s `permissions.allow` entries are **ignored** until the workspace has been trusted. The CLI says so on stderr and proceeds as if the grant were absent:

```
Ignoring 1 permissions.allow entry from .claude/settings.json: this workspace has
not been trusted. Run Claude Code interactively here once and accept the trust
dialog, or set projects["<workspace>"].hasTrustDialogAccepted: true in
~/.claude.json.
```

This collides with two existing decisions:

- Each scenario copies the scene into a **fresh temporary workspace per run**, with the agent's cwd at that workspace root (ADR [0008](0008-run-the-agent-with-cwd-at-the-workspace-root.md)). A brand-new tmp directory has never been through a trust dialog, so it is never trusted.
- The CLI version is **pinned and upgrades are deliberate migrations** (ADR [0002](0002-pin-claude-code-cli-version.md)). The gate is not a transient bug to wait out — it is a deliberate upstream security feature.

The net effect: the scene's `Bash(uv run pytest*)` grant is silently dropped, the agent's `uv run pytest` falls through to an approval prompt, and headless `-p` with no human to approve **denies** it. The agent cannot run the test, so the scenario's "ran pytest" / "FAILED result" characteristics fail for a reason unrelated to the agent's BDD/TDD behaviour — the path the real-agent walkthrough depends on is blocked.

Confirmed empirically: in an untrusted workspace the command is denied on both 2.1.193 and 2.1.195; with the same workspace marked trusted (`hasTrustDialogAccepted: true`), the `permissions.allow` grant applies and `uv run pytest` runs on the first attempt. Upgrading does not remove the gate.

## Decision

The harness **marks the workspace trusted before launching the agent**. Before invoking `claude`, `ClaudeCli` records the workspace as trusted in the user-level Claude config (`projects["<workspace>"].hasTrustDialogAccepted = true`), which is the non-interactive equivalent of accepting the trust dialog.

Trust-marking is treated as **environment setup the harness owns**, alongside the cwd it sets (ADR [0008](0008-run-the-agent-with-cwd-at-the-workspace-root.md)) and the `--add-dir` directories it passes — not as a property of the scene. The scene keeps expressing *what* the agent may do through its `permissions.allow`; the harness makes that grant effective by satisfying the trust precondition the platform now imposes.

## Consequences

- The scene's narrow allow-list stays the single source of truth for what the agent may run. The trust mark only lifts the precondition that was suppressing it; it does not widen the grant.
- The harness writes to the user-level Claude config (`~/.claude.json` on this container — a container-local file). Two cross-cutting concerns follow:
  - **Concurrency.** If scenarios run in parallel (e.g. pytest-xdist), concurrent writers must not corrupt the file — the write needs to be atomic, or guarded by a lock.
  - **Accumulation.** A unique tmp workspace per run means a new `projects[...]` entry per run; without pruning, the config grows unboundedly.
- The mechanism is version-coupled to a platform behaviour. Should a future CLI offer a first-class non-interactive trust switch (a flag or env var), this decision is the place to revisit — the harness seam is one method on `ClaudeCli`.
- The behaviour is exercised against a real `claude`, so its regression test belongs with the integration-marked suite, and the change lands TDD as its own behavioural commit after this ADR.

## Alternatives considered

- **`--dangerously-skip-permissions` / `--permission-mode bypassPermissions`:** one flag, no config mutation, but it bypasses *all* permission checks. The scene's allow-list is then inert and the agent could run anything — discarding the deliberate constraint the scenario is built around. Rejected: it removes the very thing the scene is asserting.
- **Move the allow-list onto the CLI (`--allowedTools` / `--settings`):** pass the permitted tools as launch arguments rather than discovering them from the untrusted workspace. Rejected: it splits the source of truth, taking *what the agent may do* out of the scene — where it is reviewed alongside the rest of the task fixture — and into harness wiring.
- **Pin below 2.1.193:** the gate is a deliberate upstream security feature, unlikely to be reverted; holding the pin to dodge it forgoes later fixes and only defers the problem (counter to ADR [0002](0002-pin-claude-code-cli-version.md)'s migrate-deliberately stance). Rejected.
- **Trust the workspace by hand before each run:** accepting the dialog interactively, or hand-editing the config, defeats the point of a headless, repeatable scenario suite. Rejected.
