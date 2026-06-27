---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0015 — Capture xdd-skill missteps as coaching records

**Status:** Proposed

## Context

The xdd skill is built by closing Test-Driven Agentic Behaviour(TDAB) scenario failures: a real agent runs a task under the skill (ADR [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md)'s task chain, ADR [0001](0001-start-with-tdab-and-vanilla-pytest.md)'s strategy), an inspector scores the transcript, and where the agent falls short of TDD/BDD discipline we change the guidance until it passes.

Today, once the scenario passes, the durable traces are the committed artifacts — the passing scenario and the guidance diff — both of which show only the *corrected* end-state. The session that produced them, including how the misstep actually manifested, is gone. So the guidance diff records *what* changed, but neither artifact records *why* the guidance exists or *what* misstep it defends against. Several forces make that loss expensive:

- **Guidance rots without recorded rationale.** A `SKILL.md` line — especially a prohibitive "do not" — that carries no record of the failure it prevents gets pruned blindly by a later editor who cannot see what it was holding back.
- **Behaviour and fixes are model-dependent.** A misstep may appear under one model and not another, and a correction may hold for one model but not another. Without recording the model, a fix's reliability cannot be reasoned about (and ADR [0003](0003-pin-model-versions.md) already makes the model an explicit variable).
- **Correcting a misstep may take several attempts.** Resolving one shortfall can mean trying a sequence of guidance approaches before one works. Which approaches failed, and why the winner won, is the reusable part — and it is discarded if only the final diff of scenario and chosen guidance path survives.
- **An overseeing agent is on the roadmap** which will catch a coding agent *repeating* these missteps during ordinary coding work. Development of the overseer needs source material — both for its checks and for its own agentic scenarios — and that material is exactly the catalogue of missteps and their corrections.

## Decision

Record a **coaching record** for each distinct BDD/TDD misstep a coding agent makes under the xdd skill.

1. **Scope is the xdd skill only** — a record is a lesson in BDD/TDD applied during a coding exercise.

2. **One record per principle.** A single failed scenario may surface several distinct missteps; each is its own record (e.g. "stopped at an import-error red" and "wrote a formula where a literal was demanded" are separate lessons).

3. **Location and naming:** `docs/coaching/<date-time>-<slug>.md`.

4. **Written as we go.** The record drives the work; it is not a post-hoc write-up. It is committed **on green**, bundled with the guidance change(s) that resolved the misstep. Because a series of corrections may be needed, several records and the final change can land together in that green commit.

5. **One-way link integrity.** A record may link to the task that produced it. The task must **never** link to a record. The task directory is the agent's working fixture (ADR [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md)); anything in it that points at a lesson would coach the agent under test and compromise the behaviour being measured.

6. **Each record carries:**
   - **Task** — the coding exercise.
   - **Misstep** — what the agent did, captured as its **actual manifestation**: the verbatim transcript or output evidence from the run, not a paraphrase. The committed green state preserves only the corrected behaviour, so this evidence survives nowhere else.
   - **Model(s)** — the model(s) the misstep was seen in, and the model(s) the corrective guidance was validated under.
   - **Why it's wrong** — the reasoning, distilled from the coaching dialogue.
   - **The correct step** — what should have happened.
   - **Coaching dialogue** — the actual exchange that corrected the misstep, verbatim (not a paraphrase). It records what it took to get the agent to re-articulate the correct behaviour, and — like the misstep manifestation — is lost once the session is gone.
   - **Experiments** — the guidance/guardrail/gateway mechanisms (ADR [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)) tried to correct it, and which individual choice or combination won and why.
   - **Guidance change** — the change that resolved it (which file, what was added or removed).
   - **Lesson name** — the underlying principle, not the mechanical fix.

## Consequences

- Every guidance line — every prohibition — gains provenance: the concrete misstep it defends against and what it took to correct. A later editor can see what a clause holds back before removing it.
- The corpus becomes the source material for the overseeing agent: its checks and its agentic scenarios are seeded from recorded missteps and their detection signatures.
- The model field makes the model-specificity of a misstep, or of its fix, visible, and ties the catalogue to the pinned-model regime (ADR [0003](0003-pin-model-versions.md)).
- The experiment trail teaches which guidance approach suits which class of misstep — for example, prohibitions piling up in prose around one decision is a signal to try a Promptbook diagram.
- Writing as we go captures the real dialogue and the misstep's actual manifestation — both ephemeral. The manifestation comes from a non-deterministic run, so if it isn't lifted into the record before green, the run that produced it is unrecoverable. A series of corrections then lands together in one green commit.
- The one-way link rule protects test integrity at the cost of discoverability from the task side: a reader on the task cannot navigate to its lessons, by design.
- Adds work to each corrective cycle. The 'coaching' dialogue happens anyway so only adds a small overhead in logging the dialogue, test results and experiments.

## Alternatives considered

- **One record per scenario** instead of per principle: fewer files, but bundles unrelated lessons, blunting reuse and making the overseer's source material harder to lift out one principle at a time.
- **Write the record after green**, as a write-up: rejected because the record is meant to drive the work; written after the fact it reconstructs the dialogue rather than capturing it, and loses the corrections that did not survive to green.
- **Record only the final guidance diff**, not the experiments: rejected because the failed approaches and the reason the winner won are the most reusable part when choosing a guidance mechanism for the next misstep.
