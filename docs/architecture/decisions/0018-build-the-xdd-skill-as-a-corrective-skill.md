---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0018 — Build the xdd skill as a Corrective Skill

**Status:** Proposed

## Context

The xdd skill steers a coding agent through Red-Green-Refactor. There are two ways to build it:

- **Prescriptive** — tell the agent how to do TDD, step by step.
- **Corrective** — let the model use its default approach and correct only the concepts it gets wrong.

The first real-agent scenario points to the corrective option. The task required only the **Red** step — write a failing test ready to make green.

The agent reached for the right principle *by name*, unprompted: it justified its work as *"failing for the right reason."*

But it held the concept inaccurately. It counted a collection-time `ModuleNotFoundError` as failing for the right reason, when the red that matters is the test failing on its **assertion** (a value comparison).

So the model already invokes the principle; what it lacks is the principle's correct meaning.

(Recorded as the first lesson, [`docs/lessons/20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md`](../../lessons/20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md).)

Several forces favour correcting that one concept over prescribing the whole procedure:

- **Guidance rots** (ADR [0015](0015-capture-xdd-skill-missteps-as-lessons.md)). The more prose a skill carries — especially prohibitions — the more a later editor prunes blindly. A small surface is cheaper to keep honest.
- **Prescriptive instructions are brittle and task-bound.** A corrected *definition of a concept* travels across tasks; a step-by-step "how to work" is tied to the exercise it was written for.
- **The model already reaches for the right principle, by name.** It needs the principle's meaning corrected, not the principle introduced. Re-teaching what it already invokes adds surface without value, and obscures which lines actually earn their place.
- **Behaviour is model-specific** (ADR [0003](0003-pin-model-versions.md)). What a model gets wrong by default is a property of that model, so a minimal corrective set is easier to re-validate when the pin moves than a full procedure is.

## Decision

Build the xdd skill as a **Corrective Skill**: minimal guidance that corrects only the concepts the model misrepresents by default, rather than prescribing how to work.

It is the *guidance* leg of ADR [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md), sharpened — guidance corrects understanding; guardrails and gateways enforce process.

Principles:

1. **Correct concepts, don't prescribe workflow.** A correction targets a concept the model holds inaccurately (e.g. "failing for the right reason"). Steps the model already performs well, or that belong to enforcement (e.g. commit-on-green), are out of scope — those are guardrails or gateways (ADR [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)), not skill guidance.
2. **Minimal surface.** Add the smallest correction that turns the scenario scorecard green without over-constraining. If a correction needs scaffolding to land, the concept wasn't the real gap.
3. **Built from lessons.** Each correction traces to a lesson (ADR [0015](0015-capture-xdd-skill-missteps-as-lessons.md)): the misrepresented concept, the evidence, and the corrective definition. The lesson's scenario is that correction's acceptance test.
4. **Model-scoped.** Each correction is recorded against the model it was validated under (ADR [0003](0003-pin-model-versions.md)). A correction may be unnecessary — or insufficient — for another model.

## Consequences

- The skill's surface stays small, so it rots less, and every line traces to a lesson and a failing scenario — its provenance is explicit (reinforces ADR [0015](0015-capture-xdd-skill-missteps-as-lessons.md)).
- Corrections work with the model's competence and generalise across tasks better than step-by-step instructions.
- The skill becomes model-specific. When the pinned model changes (ADR [0003](0003-pin-model-versions.md)) corrections must be re-validated: one that is now unnecessary is removed, not kept "just in case."
- Corrections can interact, so the full scenario suite must stay green after each addition.
- The line between "misrepresented concept" and "working style we'd prefer" is a judgement call; mis-classifying a process preference as a concept correction reintroduces the prescriptive bloat this decision avoids. The one-correction-per-lesson discipline and the minimal-surface test are the guard.
- A Corrective Skill can only correct what a scenario surfaces. Concepts the current scenarios do not exercise stay uncorrected until a scenario reveals them.

## Alternatives considered

- **Prescriptive skill** — spell out the full TDD procedure: rejected. Brittle, task-bound, a large surface that rots, and it overrides competence the model already has, making it harder to see which line earns its place.
- **No skill, rely on the task prompt alone:** rejected — the first real run shows a repeatable concept error the prompt does not fix.
- **Enforce via hooks/guardrails only:** rejected as the primary mechanism for *concept* errors — a hook can block a step but cannot correct a misunderstanding. Hooks remain the right tool for process steps (e.g. commit-on-green) and complement the corrective guidance rather than replacing it (ADR [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)).
