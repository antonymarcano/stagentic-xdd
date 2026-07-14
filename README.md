# stagentic-xdd

A future Claude Code plugin for language-agnostic Behaviour-Driven Development (BDD) / Test-Driven Development (TDD).

These practices express examples of a problem as tests/scenarios; taken one at a time, each example drives one or more changes to the solution. With each new example, the code must evolve to satisfy the new aspect of the problem illustrated by that example.

**A WORK IN PROGRESS**

## Outer and inner loops of example-driven practices

The **outer loop** defines each new product behaviour as an executable customer scenario (or customer test), observes it fail, then evolves the guidance — skills, prompts, and checkpoints — until it passes reliably.

What accumulates is not just working code but a suite of living specifications that catch regressions whenever something changes.

The **inner loop** is the familiar Red-Green-Refactor loop: spec a new internal behaviour (write a failing unit test), make it pass with the minimum code change, then improve the structure without changing behaviour.

![The outer and inner feedback loops](docs/assets/tdd-outer-inner-loops.png)

*(From "Growing Object-Oriented Software, Guided by Tests" by Nat Pryce and Steve Freeman)*

## Why "XDD"

Both BDD and TDD, in their original form, encompassed both customer scenarios / customer tests and unit tests.

The mainstream diluted TDD to just Red-Green-Refactor with unit tests and BDD to be about customer tests — but the underlying practice actually started out the same. Ultimately, BDD was framed as a re-articulation of TDD, not as a separate practice (see [What almost everyone gets wrong about TDD/BDD](https://open.substack.com/pub/antonymarcano/p/what-almost-everyone-gets-wrong-about-c05)).

This plugin is called XDD so that users can mentally replace the X with 'T' or 'B' based on their naming preferences.

What the practice is called isn't important; doing it well is. This plugin is a skill that aims to help Claude do it well.

## Scope

The initial focus is the inner loop, guiding an AI agent through a Red-Green-Refactor loop one behavioural increment at a time. Specifying and validating the skill itself via the outer loop is planned.

Out of scope for now is the outer loop.

## Current status: a work in progress

Currently, a basic Red→Green chain is implemented. Refactoring is yet to be implemented.
Immediate developments are documented in [`NEXT.md`](NEXT.md).

This plugin is being used as the test-subject to help drive out a framework for applying
BDD/TDD to AI skills; that framework is grown in-repo (`play/` and `stagentic-test/`) and
will later be extracted into separate repositories.

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

For an illustrative sketch of the vision, see
[`experiments/agentic-screenplay-spike/screenplay/tests/test_scenarios.py`](experiments/agentic-screenplay-spike/screenplay/tests/test_scenarios.py).
This is a prototype shape, not a target architecture.

See [`docs/architecture/decisions/`](docs/architecture/decisions/) for decisions made so far.

### Running the skill locally

Launch Claude Code with the plugin loaded from this repo:

```
claude --plugin-dir xdd-plugin
```

The skill then appears as `stagentic-xdd:xdd`.

See [`COMMANDS.md`](COMMANDS.md) for key development commands (test runners, linter).

## License

See [LICENSE](LICENSE).
