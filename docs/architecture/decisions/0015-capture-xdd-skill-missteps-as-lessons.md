---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0015 — Capture xdd-skill missteps as lessons

**Status:** Proposed

## Context

The xdd skill is built by closing Test-Driven Agentic Behaviour(TDAB) scenario failures: a real agent runs a task under the skill (ADR [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md)'s task chain, ADR [0001](0001-start-with-tdab-and-vanilla-pytest.md)'s strategy), an inspector scores the transcript, and where the agent falls short of TDD/BDD discipline we change the guidance until it passes.

Today, once the scenario passes, the durable traces are the committed artifacts — the passing scenario and the guidance diff — both of which show only the *corrected* end-state. The session that produced them, including how the misstep actually manifested, is gone. So the guidance diff records *what* changed, but neither artifact records *why* the guidance exists or *what* misstep it defends against. Several forces make that loss expensive:

- **Guidance rots without recorded rationale.** A `SKILL.md` line — especially a prohibitive "do not" — that carries no record of the failure it prevents gets pruned blindly by a later editor who cannot see what it was holding back.
- **Behaviour and fixes are model-dependent.** A misstep may appear under one model and not another, and a correction may hold for one model but not another. Without recording the model, a fix's reliability cannot be reasoned about (and ADR [0003](0003-pin-model-versions.md) already makes the model an explicit variable).
- **Correcting a misstep may take several attempts.** Resolving one shortfall can mean trying a sequence of guidance approaches before one works. Which approaches failed, and why the winner won, is the reusable part — and it is discarded if only the final diff of scenario and chosen guidance path survives.
- **An overseeing agent is on the roadmap** which will catch a coding agent *repeating* these missteps during ordinary coding work. Development of the overseer needs source material — both for its checks and for its own agentic scenarios — and that material is exactly the catalogue of missteps and their corrections.

## Decision

Record a **lesson** for each distinct BDD/TDD misstep a coding agent makes under the xdd skill.

1. **Scope is the xdd skill only** — each lesson captures BDD/TDD discipline applied during a coding exercise.

2. **One lesson per principle.** A single failed scenario may surface several distinct missteps; each is its own lesson (e.g. "stopped at an import-error red" and "wrote a formula where a literal was demanded" are separate lessons).

3. **Location and naming:** `docs/lessons/<date-time>-<slug>/` — a directory holding the lesson write-up (`lesson.md`) and the preserved run artefact (transcript, critique, and workspace source; transient trees such as `.venv` are excluded).

4. **Written as we go.** The lesson drives the work; it is not a post-hoc write-up. It is committed **on green**, bundled with the guidance change(s) that resolved the misstep. Because a series of corrections may be needed, several lessons and the final change can land together in that green commit.

5. **One-way link integrity.** A lesson may link to the task that produced it. The task must **never** link to a lesson. The task directory is the agent's working fixture (ADR [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md)); anything in it that points at a lesson would coach the agent under test and compromise the behaviour being measured.

6. **Each lesson carries:**
   - **Task** — the coding exercise.
   - **Scenario** — the spec test whose scorecard revealed the misstep, linked from the lesson. Unlike the task fixture, the test is harness the agent never sees, so this outward link carries no coaching risk (§5).
   - **Misstep** — what the agent did, in brief, with the single most telling line. The full manifestation is the preserved run artefact co-located in the lesson directory (§3), which the lesson links to for the full evidence.
   - **Config(s)** — the configuration the misstep was seen in, and the configuration the corrective guidance was validated under: the model (with context window), the reasoning effort, and the CLI version.
   - **Evidence** — the critic's verdict as a trimmed scorecard, linking the preserved `critique.md` for the full critique.
   - **Review** — the corrective feedback on the misstep, authored together by the coach and a context-aware agent and composed from the transcript after the run. It anchors in the agent's stated rationale, names why that reasoning stopped short, and gives the correct step. Where more than one disciplined path reaches the same end-state, it lists the acceptable alternatives; the invariant is the end-state, not the path. Write it while the reasoning is fresh — it is lost once the session is gone.
   - **Experiments** — the guidance/guardrail/gateway mechanisms (ADR [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)) tried to correct it, and which individual choice or combination won and why.
   - **Guidance change** — the change that resolved it (which file, what was added or removed).
   - **Lesson name** — the underlying principle, not the mechanical fix.

## Consequences

- Every guidance line — every prohibition — gains provenance: the concrete misstep it defends against and what it took to correct. A later editor can see what a clause holds back before removing it.
- The corpus becomes the source material for the overseeing agent: its checks and its agentic scenarios are seeded from recorded missteps and their detection signatures.
- The config field makes the model-, effort-, and context-specificity of a misstep, or of its fix, visible, and ties the catalogue to the pinned-version regime (ADR [0003](0003-pin-model-versions.md)).
- The experiment trail teaches which guidance approach suits which class of misstep — for example, prohibitions piling up in prose around one decision is a signal to try a Promptbook diagram.
- Writing as we go captures the review while the reasoning is fresh, and copies the run artefact before the tmp workspace is cleaned — both ephemeral. The manifestation comes from a non-deterministic run, so if the artefact isn't copied (and the review written) before green, the run that produced it is unrecoverable. A series of corrections then lands together in one green commit.
- The one-way link rule protects test integrity at the cost of discoverability from the task side: a reader on the task cannot navigate to its lessons, by design.
- Adds work to each corrective cycle. The review happens anyway, so it only adds a small overhead in logging the feedback, test results and experiments.

## Alternatives considered

- **One record per scenario** instead of per principle: fewer files, but bundles unrelated lessons, blunting reuse and making the overseer's source material harder to lift out one principle at a time.
- **Write the lesson after green**, as a write-up: rejected because the lesson is meant to drive the work; written after the fact it reconstructs the review rather than capturing it, and loses the corrections that did not survive to green.
- **Record only the final guidance diff**, not the experiments: rejected because the failed approaches and the reason the winner won are the most reusable part when choosing a guidance mechanism for the next misstep.
