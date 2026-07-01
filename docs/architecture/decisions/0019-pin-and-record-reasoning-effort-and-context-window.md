---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0019 — Pin and record reasoning effort and the context window

**Status:** Proposed

## Context

A lesson (ADR [0015](0015-capture-xdd-skill-missteps-as-lessons.md)) ties a misstep to the configuration it appeared under, and ADR [0017](0017-record-cli-version-and-model-in-the-run-transcript.md) records the CLI version and model in the run transcript — lifted from the session JSONL the transcriber already reads. Two further configuration variables that bear on that provenance are still unrecorded, and one of them is also uncontrolled:

- **Reasoning effort.** The harness passes no `--effort`, so runs use the CLI default (high for Opus 4.8). Effort is absent from both the session JSONL and the `system/init` event, so — unlike the version and model — it cannot be lifted from a run's artefacts after the fact. It is invisible, and a default that shifts between CLI versions would silently change what a lesson was captured under.
- **Context window.** The harness resolves to `claude-opus-4-8[1m]` — the 1M-context variant (Opus 4.8 maps to 1M by default). But ADR 0017's header reads `message.model`, which on the CLI version the first lessons were captured under (2.1.191) is the API id `claude-opus-4-8`, dropping the `[1m]` suffix. The 1M form is visible only in the `system/init` event's `model` field.

So a lesson today cannot state, from evidence, the effort or the context window it was produced under.

## Decision

1. **Pin reasoning effort.** The harness's `claude -p` invocation (`play/src/claude_cli.py`) passes `--effort high`. High is the current Opus 4.8 default, so pinning records the behaviour the first lessons were captured under rather than changing it.
   - Effort levels are **model-dependent**: Opus 4.8/4.7 accept `low|medium|high|xhigh|max`; Opus 4.6 and Sonnet 4.6 accept `low|medium|high|max`; Haiku 4.5 has no documented effort support. The flag is **gated on the resolved model** — passed only for a model that supports the chosen level, never for one that does not (it would fail the run).

2. **Record effort and the context window** in the run transcript, alongside ADR 0017's version + model header.
   - Effort is recorded as the value the harness sets — it is not echoed back by the CLI.
   - The context window is recorded from the `system/init` event's `model` (the `[1m]` form), not the per-message `message.model`.

## Consequences

- A lesson records the effort and context window it was produced under, from evidence — completing the provenance ADR 0015/0017 began.
- Pinning effort makes runs reproducible on that axis; a later change of effort is deliberate and visible in the header — caught by the transcript approval test the same way ADR 0017's version and model are.
- The harness must know the resolved model to gate the flag — a new coupling for `ClaudeCli`, which today passes no model and lets the CLI resolve it.
- Capturing the `[1m]` form means reading the `system/init` event, a source the ADR 0017 transcriber does not currently read.

## Alternatives considered

- **Append to ADR 0017 instead of a new ADR:** rejected — 0017's accepted decision is recording-only, lifted from the JSONL; this adds a new decision (pinning effort, gated on model) and a recording source the JSONL does not carry. One decision per ADR.
- **Leave effort at the CLI default, unrecorded:** rejected — the default is invisible after the fact and can shift between CLI versions, silently changing what a lesson was captured under.
- **Pass `--effort` unconditionally:** rejected — it fails on a model with no effort support (e.g. Haiku 4.5).
- **Record the API model id only, without the `[1m]`:** rejected — it cannot distinguish the 1M variant from the standard-context model, which is itself a provenance variable.
