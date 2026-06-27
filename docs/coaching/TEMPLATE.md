# {{Lesson name — the underlying principle, not the mechanical fix}}

- **Date-time:** {{YYYY-MM-DDThh:mmZ}}
- **Task:** [{{task name}}](../../spec/tasks/{{N-slug}})
- **Model(s) seen in:**
  - {{model id(s) the misstep appeared under}}
- **Model(s) validated under:**
  - {{model id(s) the corrective guidance was confirmed under}}
- **Coach:** {{name of coach}}

## Task

{{Summary of the coding exercise the agent was given, with a link to the TASK.md and/or start / end-scene folders. Never link back here from the task folder.}}

## Misstep

{{What the agent did, captured as its actual manifestation — verbatim transcript or output evidence from the run, not a paraphrase. The committed green state preserves only the corrected behaviour, so this evidence survives nowhere else.}}

```text
{{verbatim transcript / output excerpt showing the misstep}}
```

## Why was the misstep a problem

{{The reasoning, distilled from the coaching dialogue.}}

## The correct step

{{What should have happened.}}

## Coaching dialogue

{{The actual exchange that corrected the misstep, verbatim — not a paraphrase. Separate each turn with a blank line. This is what it took to get the agent to re-articulate the correct behaviour; like the misstep manifestation, it is lost once the session is gone.}}

**Coach:** {{observation or question}}

**Agent:** {{response}}

**Coach:** {{follow-up}}

## Experiments

{{The guidance/guardrail/gateway mechanisms (ADR [0004](../architecture/decisions/0004-structure-agent-control-with-guidance-guardrails-and-gateways.md)) tried to correct the misstep, and which individual choice or combination won and why. One entry per attempt: the mechanism, what was tried, and the outcome.}}

- **{{mechanism — e.g. prose `SKILL.md` / Promptbook / hook / gateway / sub-agent}}:** {{what was tried, and the outcome}}
- **Winner:** {{the choice or combination that corrected the misstep, and why}}

## Guidance change

{{The change that resolved it: which file, and what was added or removed.}}
