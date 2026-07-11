# Fake it until you triangulate it

- **Date-time:** 2026-07-01T06:35Z
- **Task:** [2-make-the-failing-test-pass](../../../spec/tasks/2-make-the-failing-test-pass)
- **Scenario:** [`test_make_the_failing_test_pass`](../../../spec/tests/test_red_green_commit.py) — the spec test whose scorecard revealed the misstep
- **Config(s) seen in:**
  - Model: claude-opus-4-8[1m] (1M context window)
  - Reasoning effort: CLI default (high for Opus 4.8), not explicitly set
  - CLI: claude 2.1.191
- **Config(s) validated under:**
  - Model: claude-opus-4-8[1m] (1M context window)
  - Reasoning effort: CLI default (high for Opus 4.8), not explicitly set
  - CLI: claude 2.1.191

## Task

> You are continuing to TDD a miles-to-km converter.
> Adhering to TDD discipline, make the failing test pass with your next change.
>
> Start here: `tests/test_conversion.py`

This [reference scene](../../../spec/tasks/2-make-the-failing-test-pass/scene)
is the canonical end-state: the failing test unchanged, and a `src/conversion.py`
whose `miles_to_km` returns the literal `1.60934` — the minimal green for the
single assertion. The opening scene is task 1's end-state: the same failing
test with a stub returning `0`.

## Misstep

This lesson's misstep is that the agent picks from two strategies to make the test
pass, neither of which is necessarily wrong, but with no rationale for its choice.
Sticking with one strategy, though, may be more likely to lead to a better outcome.

The task gives the agent one failing test (`miles_to_km(1) == 1.60934`) and a
stub that returns `0`. There are two ways to make it pass, and both are named
TDD strategies from Kent Beck:

- **Fake-It** — return exactly what the one test asks for: `return 1.60934`.
  This is the smallest change that goes green. It leaves a constant in place, so
  a *second* test (say `miles_to_km(2) == 3.21868`) would later force that
  constant into the real formula. Driving the general solution out with a second
  example is **Triangulation**. Fake-It example:
  [`…-e813c4a4`](20260709-135353-test_make_the_failing_test_pass-e813c4a4/miles-to-km/transcript.md)
  (the skill loaded; the agent named the *"fake it"* step and hard-coded `1.60934`).
- **Obvious Implementation** — skip faking it and write the general formula
  straight away: `return miles * 1.60934`. It also passes the one test, but it
  generalises before any test asks for it, so there is nothing left to
  triangulate. Two Obvious Implementation transcripts, each revealing something different:
  - [`…-9b6bd6a2`](20260709-135342-test_make_the_failing_test_pass-9b6bd6a2/miles-to-km/transcript.md)
    — the current, skill-loaded baseline. The agent describes the formula as *the
    minimal change*:

    > Now I'll make **the minimal change** to make the failing test pass:
    > `return miles * 1.60934`
  - [`…-b0c60ce0`](20260701-063539-test_make_the_failing_test_pass-b0c60ce0/miles-to-km/transcript.md)
    — from the earlier, pre-invocation runs. Here the agent names the strategy
    outright, so it plainly *knows* it — which is why the fix is a correction, not
    teaching (ADR [0018](../../architecture/decisions/0018-build-the-xdd-skill-as-a-corrective-skill.md)):

    > …I'll make it pass with **the obvious implementation** … multiply miles by
    > the conversion factor.

From the same task and the same prompt, the agent does not always pick the same
one — on some runs it fakes it, on others it jumps to Obvious Implementation.

## Evidence

Initial runs produced a finding that compromised their validity: the skill was
never loading. After fixing that (see ADR
[0020](../../architecture/decisions/0020-drive-skill-invocation-from-the-frontmatter-description.md)),
the runs were rebaselined — still with no "making a test pass" guidance in the
skill's body.

Rebaselined, the agent picks either strategy on its own: it fakes it (returns the
literal) in about **6 of 10** runs and writes the general formula in the other **4**.

Neither run gives a rationale for the choice. The agent does not weigh Fake-It
against Obvious Implementation; it lands on one and names it in passing — *"the
minimal change"* on a formula run
([`…-9b6bd6a2`](20260709-135342-test_make_the_failing_test_pass-9b6bd6a2/miles-to-km/transcript.md)),
*"the simplest change"* on a Fake-It run
([`…-e813c4a4`](20260709-135353-test_make_the_failing_test_pass-e813c4a4/miles-to-km/transcript.md)) —
though the formula is not, in fact, minimal: the literal would be smaller still.

This project's scorecard passes the Fake-It runs and fails the formula ones: a
Fake-It run scores all-PASS, while the formula run's verdict is
([`critique.md`](20260709-135342-test_make_the_failing_test_pass-9b6bd6a2/miles-to-km/critique.md)):

| Characteristic | Status |
|---|---|
| Transcript shows the agent invoked the xdd skill | PASS |
| Production module exists at src/conversion.py with content | PASS |
| **Workspace closely matches the Reference scene** | **FAIL** |
| **Production returns a literal value, and does not use a formula** | **FAIL** |
| Transcript shows the agent ran pytest | PASS |
| Transcript shows a PASSED pytest result | PASS |

The skill was invoked (top row PASS), yet the agent still wrote the formula — the
two FAILs are the same choice seen twice: the production code is a formula where
the reference is a literal, so the workspace diverges from the reference scene.

## Review

The Obvious Implementation isn't *wrong* — it's one of Beck's three legitimate
strategies:
- Obvious Implementation
- Fake-It
- Triangulate

Obvious Implementation has upsides and downsides.

**Upsides**
- Faster — one step, not two.
- No throwaway intermediate constant.
- Genuinely fine when the code is trivial and you are sure of it.

**Downsides**
- Choosing Obvious Implementation over Fake-It is a per-case judgement — "is it
  obvious enough?" — made every time. It's reasoning overhead, it needs a rule for
  when Obvious Implementation is allowed, and the agent applies it unreliably; it's
  also hard to audit from a log whether it got the call right.
- It leaves weaker mutation coverage: the general code carries behaviour no test
  pins, so a regression slips past — a `weight * 2` term mistyped as `weight + 5`
  survives because the one test uses a weight of 5 and `5 + 5 == 5 * 2`.
- Coverage added afterwards is written against code that already works, so those
  tests are never seen to fail — they haven't earned their trust.

Due to these downsides, Obvious Implementation is rejected in favour of
**Fake-It, then Triangulate** — even when the general code seems obvious.

Return the literal the one test pins (`1.60934`), then let a second, differing test
(`miles_to_km(2) == 3.21868`) force the formula. Then the regression protection
falls out of the same process that drives the design, every test earns its trust
by failing first, and the work is mechanical — no judgement call to make or
audit. The occasional redundant step is a small price for that.

For these reasons, rather than addressing the agent's lack of rationale for choosing
either strategy, it has been decided never to use the Obvious Implementation strategy.

## Experiments

Guidance mechanisms (ADR
[0004](../../architecture/decisions/0004-structure-agent-control-with-guidance-guardrails-and-gateways.md))
tried to correct the misstep, measured on this task as the pass rate: the share of
runs that hard-code the value the test asserts (Fake-It) rather than write the
general implementation (Obvious Implementation). Higher is better; each rate is a
batch of 10 runs or more (n per row), individually noisy — kept candidates were
confirmed at higher n.

The experiments below hold invocation fixed at 10/10 (the ADR
[0020](../../architecture/decisions/0020-drive-skill-invocation-from-the-frontmatter-description.md)
fix; see Evidence) and vary only the body's guidance on making a test pass. An
earlier body-wording ladder here predates that fix and so is invalid; it is kept
with ADR 0020 as that decision's evidence, not this lesson's. Each stage links to its exact `SKILL.md` snapshot in
[`experiments/`](experiments); a stage without a snapshot is not kept.

| Stage | Body guidance (snapshot) | n | Invocation | Fake-It (literal) | Obvious Implementation (formula) |
|---|---|---|---|---|---|
| 0 | [none](experiments/stage-00-no-body-guidance-SKILL.md) (baseline) | 10 | 10/10 | 6/10 | 4/10 |
| 1 | [one line + Fake-It / Triangulation / Obvious Implementation sub-sections](experiments/stage-01-subsections-SKILL.md) | 10 | 10/10 | 10/10 | 0/10 |
| 2 | [one line only, sub-sections dropped](experiments/stage-02-one-line-SKILL.md) | 40 | 40/40 | 40/40 | 0/40 |
| 3 | [one line, "do not use Obvious Implementation" dropped](experiments/stage-03-no-oi-prohibition-SKILL.md) | 10 | 10/10 | 10/10 | 0/10 |
| 4 | [one line, Triangulation dropped — Fake-It only](experiments/stage-04-fake-it-only-SKILL.md) — **kept** | 40 | 40/40 | 40/40 | 0/40 |

**Invocation** is held at 10/10 by the `description` change and is not the variable
here; **Fake-It (literal)** is the share that hard-code the literal (this project's
scored pass); **Obvious Implementation (formula)** the share that write the general
formula; **n** is the run count (the two kept candidates confirmed at 40). Stage 0
is the rebaseline: invocation fixed, no body guidance on making a test pass — an
example Stage-0 formula run is
[`…-9b6bd6a2`](20260709-135342-test_make_the_failing_test_pass-9b6bd6a2/miles-to-km/transcript.md),
where the skill loaded but, with no body guidance, the agent wrote
`return miles * 1.60934`.

From Stage 1 the correction sweeps, and every dial-back holds — 10/10 Fake-It, zero
formula runs at each step. Stage 3 shows the *"do not use Obvious Implementation"*
prohibition is not load-bearing; Stage 4 shows the same for the *Triangulation*
clause — but only because this single-test task never triangulates, so the metric
cannot defend keeping it. The bare minimum kept is **Stage 4**; whether
Triangulation — or any other correction — needs stating is left to a future
scenario that actually exercises it.

- **Winner:** Stage 4 — `Make a failing test pass using 'Fake-It'.` (40/40 Fake-It,
  zero formula runs). The smallest correction that holds.

## Guidance change

Added a `# Making a test pass` section to
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) — the one
line that took the formula rate from 4/10 to 0/40 once the body was read:

```markdown
# Making a test pass

Make a failing test pass using 'Fake-It'.
```

The skill's `description` — which names the red-green-refactor steps so the skill is
invoked at all — is the invocation prerequisite, decided separately in ADR
[0020](../../architecture/decisions/0020-drive-skill-invocation-from-the-frontmatter-description.md);
it is not part of this lesson's correction.

The resulting
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) in full:

```markdown
---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:

# Always write the test first

The test should always be written before the production code that makes it pass.

# Failing for the right reason

A test fails for the right reason when it has an assertion failure where the actual
result is not matching the expected result.

# Making a test pass

Make a failing test pass using 'Fake-It'.
```
