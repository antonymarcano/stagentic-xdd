# An honest red fails on the assertion, not the import

- **Date-time:** 2026-06-27T22:25Z
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

The agent replaced the placeholder with a real failing test
([`tests/test_conversion.py`](20260627-222609-test_write_a_failing_test/miles-to-km/tests/test_conversion.py)),
ran `uv run pytest`, and got a collection-phase **ERROR** —
`ModuleNotFoundError: No module named 'conversion'` — because it never created
`src/`.

The agent treated that import error as its red, declared the failing test in
place, and stopped to ask if it could make the test green.

Full run: [`transcript.md`](20260627-222609-test_write_a_failing_test/miles-to-km/transcript.md).

## Evidence

The critic scored the run against the reference scene — 2 PASS / 4 FAIL
([`critique.md`](20260627-222609-test_write_a_failing_test/miles-to-km/critique.md)):

| Characteristic | Status |
|---|---|
| Production module exists at src/conversion.py with content | FAIL |
| Workspace closely matches the Reference scene | FAIL |
| Production returns a literal value, and does not use a formula | FAIL |
| Transcript shows the agent ran pytest | PASS |
| Transcript shows a FAILED pytest result | PASS |
| Test fails comparing a return value, not on a missing module or symbol | FAIL |

## Review

The agent's rationale for stopping when it did:

> It fails for the right reason: `ModuleNotFoundError: No module named
> 'conversion'`. The module doesn't exist yet (`pyproject.toml` puts `src` on
> the path, so the next change is `src/conversion.py` with a `miles_to_km`
> function).
>
> **The next change to go green** is the minimal implementation:
>
> ```python
> def miles_to_km(miles):
>     return miles * 1.609344
> ```
>
> Want me to make it green?

A ModuleNotFoundError is the test failing for a good reason to start with. However, it isn't the
immediate step before adding/changing code to make the test pass. Therefore, it is not yet failing for 'the right reason'.

Acceptable alternatives would be either:

1. Create a file and add only what's needed to remove the import error, run the
  test again, repeat until the last failure is an assertion error due to the
  expectation not matching the actual result;
2. Create a file with the code that causes the assertion error due to the expectation
  not matching the actual result.

For a human developer using an IDE, approach 1 would not be necessary.
A modern IDE would show the import error in the editor, and the developer could fix it
using a keyboard shortcut or a code action. There is no need for a coding agent to mimic this approach.

For a coding agent, approach 2 would be preferred. This would require a corrected understanding of 'failing for the right reason'.

## Experiments

Having observed that the agent's rationale included the concept of 'failing for the right reason' it was clear that its approach was grounded in some TDD principles. However, its understanding of 'the right reason' was incorrect.

As a result, it was decided to address only the agent's misunderstanding rather than be prescriptive about how to do TDD.

That leans on its built-in 'understanding' of TDD, reducing the amount of guidance required to avoid this misstep.

The corrective `SKILL.md` carried only that one clarification:

```markdown
# Failing for the right reason

A test fails for the right reason when it has an assertion failure where the actual
result is not matching the expected result.
```

Combined with a brief introductory wording (see below), the experiment held and resolved this
misstep — the *"fails comparing a return value, not on a missing module or
symbol"* characteristic went FAIL → PASS.

The validating run scored 6 PASS / 1 FAIL — up from 2 PASS / 4 FAIL. The lone
remaining FAIL is the write-order characteristic, which traces to its own lesson:

| Characteristic | Status |
|---|---|
| Production module exists at src/conversion.py with content | PASS |
| Workspace closely matches the Reference scene | PASS |
| Production returns a literal value, and does not use a formula | PASS |
| Transcript shows the agent ran pytest | PASS |
| Transcript shows a FAILED pytest result | PASS |
| Test fails comparing a return value, not on a missing module or symbol | PASS |
| Transcript shows the failing test was written before the production code | FAIL |

### Intro-wording variations

The intro line was then varied while the corrective `# Failing for the right
reason` section beneath it stayed fixed, to test whether the framing moved the
pass rate. To isolate the framing, the *"failing test written before the
production code"* characteristic was excluded from scoring — a separate misstep
with its own lesson, no rule of its own, that dominates the pass/fail and that no
intro wording governs. Each wording was then run 10 times.

The intro sentence varied only in its opening:

**(no "overriding" line)**

```text
Apply the disciplines of TDD for adding or changing code
```

**…overriding your understanding…**

```text
Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:
```

**Strictly …overriding…**

```text
Strictly apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:
```

**…code, overriding… (comma)**

```text
Apply the disciplines of TDD for adding or changing code,
overriding your understanding with the following principles:
```

| Intro wording | No. Runs | Pass | Pass rate |
|---|---|---|---|
| (no "overriding" line) | 10 | 10 | 100% |
| …overriding your understanding… | 10 | 10 | 100% |
| Strictly …overriding… | 10 | 10 | 100% |
| …code, overriding… (comma) | 10 | 10 | 100% |

With the write-order characteristic excluded, every wording passes 10/10 — there is no difference between them.

The intro framing does not move this lesson's misstep; it was kept because it reads more clearly to a human.

## Guidance change

The chosen approach — correct the one misunderstood concept rather than prescribe
the procedure — is the decision recorded in ADR
[0018](../../architecture/decisions/0018-build-the-xdd-skill-as-a-corrective-skill.md).

The change added a `# Failing for the right reason` section beneath the intro
line. The committed
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) in
full:

```markdown
Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:

# Failing for the right reason

A test fails for the right reason when it has an assertion failure where the actual
result is not matching the expected result.
```
