---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0001 — Start development by applying the TDAB pattern with vanilla pytest

**Status:** Accepted

## Context

This plugin's purpose is to guide an AI agent through BDD/TDD — starting with the inner-loop Red-Green-Refactor cycle — and, eventually, to drive outer-loop customer scenarios as well. The intent is for the plugin to be language-agnostic; we start with Python only because it is the language the plugin and `stagentic-play` are themselves written in, not because the plugin's guidance is limited to it. Both loops are themselves driven by agent behaviour, which is non-deterministic and resists ordinary assertions; the [TDAB pattern](https://substack.com/@antonymarcano/note/c-252213610) addresses this by specifying each behaviour as a scenario evaluated against a scorecard rubric.

We need to choose how those scenarios are expressed and executed during the bootstrap phase, before any framework code exists.

The [experiments directory](../../../experiments/) holds spikes exploring different shapes for that execution, including a Screenplay-style DSL on top of pytest + `claude -p` ([`agentic-screenplay-spike`](../../../experiments/agentic-screenplay-spike/)).

## Decision

Apply the TDAB pattern using vanilla pytest from day one. The framework emerges during refactoring, not before.

1. **First scenario: a Python "Red-Green Increments" test.** A pytest test asserts that an agent, given a clean fixture with a placeholder test, performs Red-Green-Refactor one behaviour at a time. Plain pytest — no DSL, no abstractions.

2. **Stub the agent first.** The When step initially produces canned transcript content. This makes the bootstrap deterministic and fast, and separates "is the harness correct?" from "does the agent behave?".

3. **Auditor first, critic later, swapped by pytest fixture.** The Then step starts as an *Auditor*: in-process Python code that asserts against the transcript. Once green, swap it for a *Critic*: a `claude -p` invocation running a scorecard prompt. Both modes run from the same test body, selected via fixture.

4. **Auditor and critic developed via ordinary TDD.** Both are Python code (the critic wraps `claude -p`); their behaviour is driven by unit tests.

5. **Agentic When step last.** Once the stubbed agent passes against both auditor and critic, swap the stub for an agentic When — `claude -p` driving real Red-Green-Refactor on the fixture — and run it through the same scenario.

6. **Framework emerges in refactoring.** The first scenario is written without abstractions. As subsequent scenarios reveal common shape, the framework code is extracted in green-only refactoring steps into an isolated `stagentic-play` Python module, structured so it can later be lifted into its own repository. The spikes under `./experiments/` are a source of ideas, not a target shape.

## Consequences

- Work begins immediately with pytest + `claude -p`; no upstream framework dependency.
- Each layer (stubbed agent, auditor, critic, agentic agent) is added only when the layer below is green. Regressions are bounded at the layer they occur.
- The auditor/critic split, swapped via fixturing, gives both a fast deterministic inner loop (auditor) and a behaviour-faithful slow loop (critic) from a single test body.
- The critic depends on the `claude` CLI being installed. Reproducibility of critic runs depends on the CLI surface staying stable; pinning strategy TBD.
- `stagentic-play`'s internal API will churn until two or three scenarios have driven its abstractions.
- All plugin code and the scenarios that drive it live in this repository. No second repository is created for spec content until `stagentic-play` is extracted.

## Alternatives considered

- **Adopt a Screenplay-style DSL from day one.** The spike under `./experiments/agentic-screenplay-spike/` already prototypes this shape. Rejected for the start: designing the DSL before real scenarios exist is speculative; better to let it emerge from concrete tests during refactoring.
- **Build the `stagentic-play` framework first, then write scenarios against it.** Same speculative-design risk; the framework should accrete from real call-site needs.
- **Start with an agentic When step.** Non-determinism and `claude -p` latency would slow the loop while the auditor/critic split is still being shaken out. Stubbing the agent first isolates harness correctness from agent behaviour.
- **Skip the auditor; start with the critic.** The critic is non-deterministic and slow and depends on `claude -p` being available. The auditor gives a fast deterministic check that harness wiring is correct before the critic is introduced.
- **Build a bespoke scenario runner (custom orchestrator, IPC, background transcribers) instead of using pytest.** Pytest already supplies per-test reporting, fixtures, parallel execution, and a familiar pass/fail contract. A custom runner is justified only when those features prove insufficient.
- **Drive the plugin using the tdab prototype.** Rejected: the prototype was built to validate the *approach*, not as a foundation for the *implementation*. Using it would leave no reusable artefacts for future development and would require migration to `stagentic-play` later.
