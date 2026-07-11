# {{Lesson name — the underlying principle, not the mechanical fix}}

- **Date-time:** {{YYYY-MM-DDThh:mmZ}}
- **Task:** [{{task name}}](../../../spec/tasks/{{N-slug}})
- **Scenario:** [`{{test_name}}`](../../../spec/tests/{{test_file}}.py) — the spec test whose scorecard revealed the misstep
- **Config(s) seen in:**
  - Model: {{model id, with context window if notable}}
  - Reasoning effort: {{level, or "CLI default (…)" if not explicitly set}}
  - CLI: {{claude version}}
- **Config(s) validated under:**
  - Model: {{model id, with context window if notable}}
  - Reasoning effort: {{level, or "CLI default (…)" if not explicitly set}}
  - CLI: {{claude version}}

## Task

{{The task given to the agent, quoted verbatim as a block quote, then a concise note on the reference scene (the canonical end-state). Never link back here from the task folder.}}

> {{verbatim task given to the agent}}

## Misstep

{{What the agent did, in a sentence or two, with the single most telling line — e.g. the failure it treated as its red. Link to the preserved artefact for the full evidence (`transcript.md`, the test file, the workspace) rather than inlining it.}}

## Evidence

{{The critic's verdict as a trimmed PASS/FAIL scorecard, with a link to `critique.md` for the full critique.}}

| Characteristic | Status |
|---|---|
| {{characteristic}} | {{PASS / FAIL}} |

## Review

{{The corrective feedback, authored together by the coach and a context-aware agent and composed from the transcript after the run. Anchor it in the agent's own stated rationale, name why that reasoning stopped short, and give the correct step. Where more than one disciplined path reaches the same end-state, list the acceptable alternatives; the invariant is the end-state, not the path. Keep the framings tried — what it took to correct the misstep — in Experiments.}}

## Experiments

{{The guidance/guardrail/gateway mechanisms (ADR [0004](../../architecture/decisions/0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)) tried to correct the misstep, and which individual choice or combination won and why. One entry per attempt: the mechanism, what was tried, and the outcome.}}

- **{{mechanism — e.g. prose `SKILL.md` / Promptbook / hook / gateway / sub-agent}}:** {{what was tried, and the outcome}}
- **Winner:** {{the choice or combination that corrected the misstep, and why}}

## Guidance change

{{The change that resolved it: which file, and what was added or removed.}}
