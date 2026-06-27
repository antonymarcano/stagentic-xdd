---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0017 — Record the resolved CLI version and model in the run transcript

**Status:** Accepted

## Context

A scenario run produces durable artefacts — the agent's `transcript.md` and the critic's `critique.md` (both built by `ClaudeTranscriber`). They record *what the agent and critic did*, but not *which `claude` CLI version and model produced them*.

That gap is expensive when a run regresses. A scenario that had been passing began failing: the agent could no longer run its test. Isolating the cause meant re-running the scenario under candidate CLI versions and comparing behaviour — empirical bisection — before the culprit surfaced: a workspace-trust behaviour change between CLI versions (ADR [0016](0016-trust-the-agent-workspace-for-headless-runs.md)). The investigation was only necessary because the evidence didn't say which version each run used; the deciding variable was invisible in the artefacts.

Two existing decisions make this gap sharper:

- The CLI and model are **pinned, and upgrades are deliberate migrations** (ADR [0002](0002-pin-claude-code-cli-version.md), ADR [0003](0003-pin-model-versions.md)). Those decisions presume the pinned versions are what actually ran — but nothing in a run's artefacts records what ran, so a pin drift (or an in-session override) leaves no trace.
- A **coaching record** is meant to tie a misstep to the model it appeared under (ADR [0015](0015-capture-xdd-skill-missteps-as-coaching-records.md)). A misstep comes from a non-deterministic run; if the version and model aren't captured at source, that provenance is reconstructed from memory, not lifted from evidence.

The authoritative source for both values is the **session JSONL the transcriber already reads**: each entry the running process writes carries the CLI version as a top-level `version` field, and each assistant entry carries the `model` it ran under — both recorded by the process that actually ran. This is more trustworthy than asking `claude --version` separately — a subprocess runs whatever binary is on disk at exec time, which need not match a version checked elsewhere. That exact mismatch was part of what made the regression above hard to reason about.

## Decision

`ClaudeTranscriber` emits a **versions header** as a block at the top of every transcript it produces, sourced from the session JSONL it already reads — the CLI version from the first entry carrying a top-level `version`, the model from the first assistant entry's `message.model`, each falling back to `unknown` when no entry supplies it — one value per line, so a diff isolates which value changed:

````
`[VERSIONS]` Used in this run:
```
CLI: claude 2.1.195
MODEL: claude-opus-4-8[1m]
```
````

Because both the agent's `transcript.md` and the critic's `critique.md` are transcriber outputs, each carries its own header — so the agent run and the critic run are both recorded, including when they use different models.

Drift is caught by the existing **approval test** over the transcript: the header changes the instant a version or model changes, so a silent shift fails the test rather than passing unnoticed. No separate assert-against-pin check is added — the approval test is the tripwire, and a working-run-versus-failing-run diff of the header points straight at a changed variable.

## Consequences

- A regression that turns on a version or model change is visible in the artefacts: the approval test fails on the shift, and comparing two runs' headers isolates the variable at a glance — collapsing the empirical bisection that this decision's context describes.
- The header is deterministic given the pins (ADR [0002](0002-pin-claude-code-cli-version.md), ADR [0003](0003-pin-model-versions.md)), so it does not make approval tests flaky; it only moves when something it is meant to catch moves.
- A coaching record (ADR [0015](0015-capture-xdd-skill-missteps-as-coaching-records.md)) can lift the model from the transcript verbatim rather than recall it.
- When a JSONL supplies neither value, the line reads `unknown` rather than being omitted, keeping the block shape stable for the approval diff.
- Adding the header changes the transcript's shape, so the transcript-shape tests — `ClaudeTranscriber`'s tests and the transcriber approval test (the `varied-transcript` case, cf. ADR [0014](0014-separate-claude-jsonl-translation-from-the-transcriber.md)) — update. The change lands TDD in `ClaudeTranscriber` as its own behavioural commit.

## Alternatives considered

- **A separate `versions.json` per run dir:** rejected — an extra file, not co-located with the transcript the inspector reads and the coaching record cites, and it would not be covered by the transcript approval test that gives the drift tripwire for free.
- **An explicit assert-against-pin check** (fail/warn when a run's version differs from the pin): rejected as redundant for the approval-tested scenario — the approval test already trips on any header change. Recording, not enforcing, is the goal here; enforcement is ADR [0002](0002-pin-claude-code-cli-version.md)/[0003](0003-pin-model-versions.md)'s concern.
- **Capture in the archiver by re-reading the transcript:** rejected — the transcriber already reads the JSONL these values live in; routing them out and back through the archiver is indirection for no gain.
- **Read the version from `claude --version` rather than the JSONL:** rejected — that reports whatever binary a separate call resolves, not the one that produced this transcript; the JSONL entries are written by the process that actually ran, so they are the process of record, and the difference is precisely what obscured the regression above.
