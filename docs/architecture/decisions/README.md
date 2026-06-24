---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# Architecture Decisions

Architecture Decision Records (ADRs) capture the *why* behind significant design choices in stagentic-tdd. Each ADR records the context, the decision, and the alternatives considered.

See [0000](0000-use-adrs-to-record-decisions.md) for more on ADRs, the rationale, the format, statuses, and conventions.

## How to add an ADR

1. Copy `TEMPLATE.md` to `NNNN-short-slug.md` (next available number).
2. Fill in the sections.
3. Set status to `Proposed`.
4. Add a row in the index below.

## Index

| # | Title | Status |
|---|---|---|
| [0000](0000-use-adrs-to-record-decisions.md) | Use ADRs to record decisions | Proposed |
| [0001](0001-start-with-tdab-and-vanilla-pytest.md) | Start development by applying the TDAB pattern with vanilla pytest | Proposed |
| [0002](0002-pin-claude-code-cli-version.md) | Pin the Claude Code CLI version; treat upgrades as deliberate migrations | Accepted |
| [0003](0003-pin-model-versions.md) | Pin model versions; treat upgrades as deliberate migrations | Accepted |
| [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md) | Structure agent control through guidance, guardrails, and gateways | Proposed |
| [0005](0005-periodic-cli-version-update-checking.md) | Periodic Claude Code CLI version update checking | Proposed |
| [0006](0006-use-native-installer-for-pinned-cli.md) | Use the Claude Code native installer for the pinned CLI version | Proposed |
| [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md) | Structure inner-loop scenarios as a task chain audited by a scorecard | Accepted |
| [0008](0008-run-the-agent-with-cwd-at-the-workspace-root.md) | Run the agent with cwd at the workspace root | Proposed |
| [0009](0009-select-inspector-and-agent-per-run-via-pytest-cli-options.md) | Select inspector and agent per run via pytest CLI options | Accepted |
| [0010](0010-adopt-mutation-testing-with-a-staged-rollout.md) | Adopt mutation testing with a staged rollout | Accepted |
| [0011](0011-adopt-pyhamcrest-for-declarative-assertions.md) | Adopt PyHamcrest for declarative test assertions | Accepted |
| [0012](0012-adopt-path-source-packages-for-cross-project-code.md) | Adopt path-source packages for cross-project code | Accepted |
| [0013](0013-agents-and-inspectors-return-a-result-value.md) | Agents and inspectors return a Result value rather than state or exceptions | Accepted |
| [0014](0014-separate-claude-jsonl-translation-from-the-transcriber.md) | Separate Claude jsonl translation from the transcriber | Proposed |
