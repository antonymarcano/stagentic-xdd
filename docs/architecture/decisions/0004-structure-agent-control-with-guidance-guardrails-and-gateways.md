---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0004 — Structure agent control through guidance, guardrails, and gateways

**Status:** Proposed

## Context

The stagentic plugin guides an AI agent through Red-Green-Refactor. For the
agent to behave reliably — staying in the inner loop, making one small change
at a time, not cleaning up when the task is "make it pass" — the plugin must
constrain what the agent can do and how it does it.

The instinct is to express constraints as instructions: tell the agent "never
do X", "always do Y". But instructions are guidance — they provide direction
and create no barrier. An agent that reasons it can achieve its goal more
efficiently by a different route may rationalise past a guideline that is not
technically enforced.

Three distinct mechanisms are available for constraining agent behaviour
(see [What we all got wrong about agent guardrails](https://antonymarcano.substack.com/p/what-we-all-got-wrong-about-agent)):

- **Guidance** — prompts, CLAUDE.md, AGENTS.md: provide direction but remain
  suggestions the agent can reason around.
- **Guardrails** — deny lists in settings.json, tool restrictions: create
  technical barriers the agent cannot cross without active circumvention.
- **Gateways** — narrowly scoped tools and entry points: channel the agent
  toward approved solutions by making the right path the easy path.

Relying solely on guidance is the common failure mode: an instruction like
"never skip a failing test" is a direction, not an enforcement mechanism.

## Decision

Structure agent-facing control in stagentic using all three mechanisms, applied
at the appropriate layer:

### Guidance
Express intent and context in `CLAUDE.md` and system prompts. Guidance explains
*why* a constraint exists and what the agent is trying to achieve. It is the
appropriate layer for nuance, rationale, and preference — but not for anything
that must be enforced.

### Guardrails
Enforce hard prohibitions via `permissions.deny` in `settings.json`. Each entry
names a tool and an optional pattern:

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf*)",
      "Bash(python3:*)"
    ]
  }
}
```

An action in the deny list cannot be taken by the agent at all — it cannot
reason past it. Use guardrails for actions that must never occur regardless of
the agent's reasoning: modifying test files during a Green step, running the
full test suite during a Red step, and so on.

### Gateways
Where the agent needs to perform a controlled operation, expose a narrowly
scoped console-script entry point that encodes the only permitted approach.
Allow only that entry point in `permissions.allow`:

```json
{
  "permissions": {
    "allow": [
      "Bash(run-tests *)"
    ]
  }
}
```

The entry point is a Python console script (declared in `pyproject.toml` under
`[project.scripts]`) that validates inputs, enforces preconditions, and
performs the operation correctly. The agent gets a single, named, approvable
action; the implementation detail is hidden inside it.

### Concrete mechanisms (non-exhaustive)

The three roles describe the *kind* of control. They are realised through
concrete vehicles — this list will grow and is not a limit:

- prose `SKILL.md` / `CLAUDE.md` — guidance
- a Promptbook (PlantUML + DSL) diagram — structured guidance
- `permissions.deny` in `settings.json` — guardrail
- a narrowly scoped console-script or bundled MCP server — gateway
- hooks — guardrail (`PreToolUse` block) or guidance (`PostToolUse` nudge,
  `SessionStart` inject)
- sub-agents — a structural layer that channels a sub-task through a scoped agent

A single vehicle may serve more than one role depending on how it is used.

## Consequences

- Prohibited actions require active circumvention to violate, not merely a
  decision to ignore a guideline.
- Gateways create a stable interface between the plugin and the agent; changes
  to permitted behaviour change the gateway implementation, not scattered
  instructions.
- TDAB scenarios can test guardrails and gateways directly — "can the agent
  take a prohibited action?" is a checkable property, not just an observed
  tendency.
- Adding guardrails and gateways is higher-effort than writing guidance alone;
  the payoff is reliability that survives model changes and reasoning-path
  variation.
- Console-script gateways must be installed in the agent's environment to be
  available. The plugin's installation step is responsible for this.

## Alternatives considered

- **Guidance alone.** Lower effort. Insufficient: an agent that reasons its way
  to a shortcut reads "don't do X" as a preference rather than a constraint.
  Rejected as the sole mechanism.
- **Guardrails without gateways.** Blocking a tool without providing a scoped
  alternative leaves the agent without a compliant path, driving workarounds
  rather than approved behaviour. Rejected as incomplete.
- **Framework-enforced sequencing only.** An outer harness that calls the agent
  only at specific steps enforces sequencing but cannot prevent disallowed
  actions within a step. Useful as a structural layer; insufficient on its own.
