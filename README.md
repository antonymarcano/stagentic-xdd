# stagentic-xdd

A planned Claude plugin for language-agnostic Behaviour-Driven Development (BDD) / Test-Driven Development (TDD).

## A work in progress

One inner-loop scenario currently runs green against a fake agent,
selectable against either a deterministic auditor or an agentic critic.

The critic wraps `claude -p` running a scorecard prompt over the
agent's transcript and resulting workspace state, judging each
characteristic without deterministic assertions.

The harness is designed so both sides grow via fixture configuration —
without rewriting the test:

- `Agent` is implemented but `--agent=real` is not yet wired into the
  fixtures — the `agent` fixture exposes only `FakeAgent` until the xdd
  skill has its first passing scenario.

For an illustrative sketch of the eventual fixture-config matrix
(real-Claude vs stubbed agent × auditor vs critic), see
[`experiments/agentic-screenplay-spike/screenplay/tests/test_scenarios.py`](experiments/agentic-screenplay-spike/screenplay/tests/test_scenarios.py)
— a prototype shape, not a target architecture.

See [`NEXT.md`](NEXT.md) for the current focus and
[`docs/architecture/decisions/`](docs/architecture/decisions/) for the
architectural direction.

# Why "XDD"

Both BDD and TDD, in their original form, encompass an outer loop (customer scenarios / customer tests) and an inner loop (Red-Green-Refactor). The mainstream diluted both — TDD to just the inner loop, BDD to just customer tests — but the underlying practice is the same.

For the longer argument, see [What almost everyone gets wrong about TDD/BDD](https://open.substack.com/pub/antonymarcano/p/what-almost-everyone-gets-wrong-about-c05).

Whether you call it TDD, BDD, or eXample-Driven Development — substitute the X with T, B, or whatever you prefer — you can apply the same working practice. What you call it isn't important; doing it well is. This plugin is a skill that aims to help Claude do it well.

## The outer and inner loops

The **outer loop** defines each new product behaviour as an executable customer scenario (or customer test), observes it fail, then evolves the guidance — skills, prompts, and checkpoints — until it passes reliably.

What accumulates is not just working code but a suite of living specifications that catch regressions whenever something changes.

The **inner loop** is the familiar Red-Green-Refactor loop: spec a new internal behaviour (write a failing unit test), make it pass with the minimum code change, then improve the structure without changing behaviour.

![The outer and inner feedback loops in TDD](docs/assets/tdd-outer-inner-loops.png)

*(From "Growing Object-Oriented Software, Guided by Tests" by Nat Pryce and Steve Freeman)*

## Scope

The initial focus is the inner loop, guiding an AI agent through a Red-Green-Refactor loop one behavioural increment at a time. Specifying and validating the skill itself via the outer loop is planned.

Out of scope for now is the outer loop.

## Language adapters

Today, only Python is supported, because the code that facilitates the skill is written in Python. Beyond that, language support will be provided through adapters — the skill itself is language-agnostic. Adapters will provide build and test commands, with linters, mutation testing and customisable tool-chain integration.

## Prerequisites

This project requires Claude Code CLI **2.1.191**. Auto-updates are disabled by `.claude/settings.json` — do not run `claude update` without first validating the suite against the candidate version.

Check your current version:

```
claude --version
```

If you already have Claude Code installed, switch to the required version:

```
claude install 2.1.191
```

If you are installing Claude Code for the first time, install the required version directly via npm:

```
npm install -g @anthropic-ai/claude-code@2.1.191
```

## Development

This plugin is being developed using a pattern created by Antony Marcano called [TDAB](https://substack.com/@antonymarcano/note/c-252213610) — Test-Driven Agentic Behaviours. This is essentially BDD/TDD for agentic behaviours, driving new or improved agent behaviour one scenario at a time.

Each behaviour is specified as a scenario, with fixture code forming the basis of a small, scoped exercise, validated end-to-end in both the result and the approach to achieving it — before the guidance is considered done.

A key problem this pattern solves is that agent behaviours are non-deterministic and cannot be asserted using traditional methods. Instead, a rubric, or scorecard, is used to evaluate non-deterministic agent behaviours.

### Running the skill locally

Launch Claude Code with the plugin loaded from this repo:

```
claude --plugin-dir xdd-plugin
```

The skill then appears as `stagentic-xdd:xdd`.

See [`COMMANDS.md`](COMMANDS.md) for key development commands (test runners, linter).

## License

See [LICENSE](LICENSE).
