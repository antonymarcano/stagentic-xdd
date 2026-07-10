---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0020 — Drive skill invocation from the frontmatter description

**Status:** Accepted

## Context

A skill only steers the agent if the model actually invokes it. Claude decides
that from the skill's frontmatter `description` in the skill listing; the body is
loaded only once the skill is called.

On the "make the failing test pass" task the xdd skill was **available but never
invoked** — 0/10 real-agent runs loaded it — while on the preceding "write a
failing test" task the same agent, same prompt, invoked it 10/10. The prompts
differ only in the step. The committed `description` — "Use when adding or changing
code" — did not read as relevant to a one-line "make it pass" edit, so the model
just did the edit.

This was invisible and corrosive: an entire ladder of body-wording experiments
was run against this task and every wording landed within noise (30–40%), read as
"guidance doesn't help." The real cause was that the body — and every wording —
never entered context. Whether a skill loads for a *sub-step* is therefore a
prerequisite for any body guidance being measurable at all, and it is
cross-cutting: it governs every skill and every sub-step, not this one task.

## Evidence

Invocation, as the share of real-agent runs (n=10 each) that loaded the skill:

| Task | `description` | Skill invoked |
|---|---|---|
| write a failing test | "Use when adding or changing code" | 10/10 |
| make the failing test pass | "Use when adding or changing code" | 0/10 |
| make the failing test pass | names each red-green-refactor step | 10/10 |

The generic wording sufficed for one sub-step but not the other, so invocation is
settled per task, not once.

Before this was diagnosed, a ladder of body-wording variants was run on the "make
it pass" task. Each landed within the no-guidance baseline's noise because the body
was never read — a
[representative run](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-runs/20260702-200812-test_make_the_failing_test_pass-e3472e2f/miles-to-km/transcript.md)
shows the skill in the listing but never called. Each wording links to its snapshot:

| Body wording (snapshot) | Fake-It rate |
|---|---|
| [no guidance (baseline)](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-00-no-guidance-SKILL.md) | 40% (4/10) |
| [Fake-It / Triangulation / Obvious Implementation sub-sections](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-01-subsections-SKILL.md) | 30% (3/10) |
| [sub-sections, plus a running `is_even` example](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-02-subsections-examples-SKILL.md) | 40% (4/10) |
| [single "do not use Obvious Implementation" section + example](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-03-oi-only-typo-SKILL.md) | 40% (4/10) |
| [as above, typo corrected](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-04-oi-only-SKILL.md) | 30% (3/10) |
| [generalised wording, no example](0020-drive-skill-invocation-from-the-frontmatter-description/superseded-wordings/stage-05-oi-generalised-SKILL.md) | 40% (4/10) |

## Decision

Ensure invocation by wording the skill's frontmatter `description` to name the
red-green-refactor steps explicitly, rather than relying on a generic phrase or on
a project `CLAUDE.md` directive. The committed description:

> Use for ALL test-driven development work — before writing a failing test, making
> a failing test pass, or refactoring. Invoke before adding or changing any
> production or test code.

Measured effect on the "make it pass" task: invocation **0/10 → 10/10**.

## Consequences

- **Model-specific** (ADR [0003](0003-pin-model-versions.md)): what a description
  must say to trigger invocation is a property of the pinned model; re-validate on
  a pin bump.
- **Protects the description from being trimmed.** A future editor who shortens it
  back to "use when adding code" silently returns invocation to ~0 on sub-steps —
  the guidance-rot risk ADR [0015](0015-capture-xdd-skill-missteps-as-lessons.md)
  warns of. This ADR records why the wording earns its length.
- **Lessons baseline on the loaded skill.** With invocation assured, a lesson's
  experiments measure the body, not whether it was read. The invocation issue
  lives here, once, instead of recurring in every lesson.
- Ships with the plugin, so no per-project setup is required.

## Alternatives considered

- **A `CLAUDE.md` directive** ("for any code change, invoke the xdd skill"):
  rejected as the primary mechanism — it lives in the user's project, not the
  plugin, so every consumer must add and maintain it; the description is the
  product-native trigger. Viable as a belt-and-braces fallback.
- **Rely on the generic description / model auto-selection:** rejected — 0/10 on
  the sub-step.
- **Force invocation with a hook/guardrail** (ADR
  [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)):
  rejected as primary — a hook can block a step but cannot make the model *choose*
  to invoke a skill; the description is the native signal. A hook remains a
  possible fallback.
