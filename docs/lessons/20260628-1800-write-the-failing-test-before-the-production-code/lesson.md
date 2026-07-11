# The failing test is written before the production code

- **Date-time:** 2026-06-28T18:00Z
- **Task:** [1-first-test-for-miles-to-km-converter](../../../spec/tasks/1-first-test-for-miles-to-km-converter)
- **Scenario:** [`test_write_a_failing_test`](../../../spec/tests/test_red_green_commit.py) — the spec test whose scorecard revealed the misstep
- **Config(s) seen in:**
  - Model: claude-opus-4-8[1m] (1M context window)
  - Reasoning effort: CLI default (high for Opus 4.8), not explicitly set
  - CLI: claude 2.1.191
- **Config(s) validated under:**
  - Model: claude-opus-4-8[1m] (1M context window)
  - Reasoning effort: CLI default (high for Opus 4.8), not explicitly set
  - CLI: claude 2.1.191

## Task

> You are about to TDD a miles-to-km converter.
> Adhering to TDD discipline, write a failing test ready to make green with your
> next change.
>
> Start here: `tests/test_conversion.py`

## Reference scene

This [reference scene](../../../spec/tasks/1-first-test-for-miles-to-km-converter/scene)
is the canonical end-state:
- a test asserting `miles_to_km(1) == 1.60934`
- with a stub `src/conversion.py` returning `0`.

## Misstep

The agent wrote the production stub
([`src/conversion.py`](20260628-180031-test_write_a_failing_test-b5a8c5c8/miles-to-km/src/conversion.py),
a `miles_to_km` returning `0.0`) **before** it wrote the failing test
([`tests/test_conversion.py`](20260628-180031-test_write_a_failing_test-b5a8c5c8/miles-to-km/tests/test_conversion.py)),
then ran pytest and reached an honest assertion red (`assert 0.0 == 1.609344`).

It announced the inverted order in one line, reasoning from the honest-red
principle:

> I'll set up so the test fails for the right reason (an assertion failure, not
> a collection/import error). **First the source stub, then the failing test.**

The red it reached was correct; the *sequence* that produced it was not.

Full run: [`transcript.md`](20260628-180031-test_write_a_failing_test-b5a8c5c8/miles-to-km/transcript.md).

## Evidence

The critic scored the run 6 PASS / 1 FAIL
([`critique.md`](20260628-180031-test_write_a_failing_test-b5a8c5c8/miles-to-km/critique.md)):

| Characteristic                                                               | Status   |
|------------------------------------------------------------------------------|----------|
| Production module exists at src/conversion.py with content                   | PASS     |
| Workspace closely matches the Reference scene                                | PASS     |
| Production returns a literal value, and does not use a formula               | PASS     |
| Transcript shows the agent ran pytest                                        | PASS     |
| Transcript shows a FAILED pytest result                                      | PASS     |
| Test fails comparing a return value, not on a missing module or symbol       | PASS     |
| **Transcript shows the failing test was written before the production code** | **FAIL** |

## Review

Note: **This was not caused by the 'failing for the right reason' rule**
([prior lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md)):
the same inverted order was seen in a real-agent run captured *before* the xdd
skill existed.

Red-Green-Refactor is ordered: the failing test exists *first*, and the production
code is the change that answers it.

Disciplined sequences that all keep the test first:

1. Write the failing test; run it. If it errors on the missing import, add the
   minimal stub (returning a wrong value) so the next run fails on the
   assertion — the stub is authored *after* the test.
2. Write the failing test first, then — knowing a stub is needed to reach the
   assertion — add the stub returning a wrong literal.

Either way the stub follows the test. The misstep is doing the two correct
actions in the wrong order, not doing a wrong action.

It can be argued that the order in which the test and code was written for a
coding agent is not as important as the order in which they are executed.
And, in this case, the test still failed in the same way regardless of the order
in which code was created. However, this small amount of context preserves
the purity of the approach at virtually no cost.

## Experiments

The model already writes the test first in most runs, so the gap is an ordering
invariant it applies inconsistently, not a concept it lacks — a single sentence
stating the invariant should be enough (cf. ADR
[0018](../../architecture/decisions/0018-build-the-xdd-skill-as-a-corrective-skill.md)).

- **Prose `SKILL.md` correction:** added a `# Always write the test first`
  section stating the ordering invariant directly:

  ```markdown
  # Always write the test first

  The test should always be written before the production code that makes it pass.
  ```

  Placed above the existing `# Failing for the right reason` section. The
  write-order characteristic went FAIL → PASS.

- **Winner:** the prose correction — one sentence naming the invariant the model
  was applying inconsistently.

Measured on this task, same config (`claude-opus-4-8[1m]`, default high effort,
CLI 2.1.191), 10 runs each:

| Skill | Runs | Full-scorecard pass | Write-order FAIL |
|---|---|---|---|
| Honest-red rule only (before) | 10 | 7 | 3 |
| + "Always write the test first" (after) | 10 | 10 | 0 |

Ten clean runs is a real shift from the ~30% failure rate, not proof the misstep
is now impossible; it is validated only for this task and this config.

## Guidance change

Added a `# Always write the test first` section to
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md),
above the `# Failing for the right reason` section from the prior lesson. The
committed file in full:

```markdown
Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:

# Always write the test first

The test should always be written before the production code that makes it pass.

# Failing for the right reason

A test fails for the right reason when it has an assertion failure where the actual
result is not matching the expected result.
```
