# The failing test is written before the production code — recurrence

- **Date-time:** 2026-07-12T18:55Z
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

A recurrence of
[The failing test is written before the production code](../20260628-1800-write-the-failing-test-before-the-production-code/lesson.md).
That lesson's guidance corrected the misstep to 0/10 at capture; it reappeared
here under the same recorded config, with no discernible external change. A
recurrence is captured as its own dated lesson so the recurrence date, and any
later-emerging external cause (a model or effort change), stays legible.

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

In a routine real-agent baseline run of the same scenario, the xdd skill loaded
and its `# Always write the test first` section was in context
([`transcript.md`](20260712-185558-test_write_a_failing_test/miles-to-km/transcript.md)),
yet the agent wrote the production stub (`src/conversion.py` returning `0.0`)
before the failing test — reasoning from honest-red, as in the original misstep:

> So I'll create a minimal stub that returns the right type (`float`) but the
> wrong value, then write a real failing test against it.

## Evidence

The critic scored 8 PASS / 1 FAIL
([`critique.md`](20260712-185558-test_write_a_failing_test/miles-to-km/critique.md)),
the single FAIL being the write-order characteristic.

| Characteristic | Status |
|---|---|
| Transcript shows the agent invoked the xdd skill | PASS |
| Production module exists at src/conversion.py with content | PASS |
| Workspace closely matches the Reference scene | PASS |
| Production returns a literal value, and does not use a formula | PASS |
| Production returns a value of the same type as the value the test asserts | PASS |
| Transcript shows the agent ran pytest | PASS |
| Transcript shows a FAILED pytest result | PASS |
| Test fails comparing a return value, not on a missing module or symbol | PASS |
| **Transcript shows the failing test was written before the production code** | **FAIL** |

## Review

The guidance was present and read, and still lost to the honest-red rationale:
the stub is authored to reach an assertion red — exactly the honest-red set-up
the [prior lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md)
ties the misstep to — so naming the ordering invariant alone does not displace
it. The original ten clean runs were not the floor: across 20 runs (two 10×
real-agent batches, same config, guidance loaded) the misstep recurs at ~20%
(4/20). The disciplined sequence is unchanged from the original lesson — the
failing test exists first, then the stub that reaches its assertion red — but a
one-line correction does not hold it.

## Experiments

The correction was re-worked by trying wordings of `SKILL.md` and measuring each
against the recurrence baseline with the real-agent batch/tally scripts
([COMMANDS.md](../../../COMMANDS.md)). Small batches proved underpowered, so the
decisive comparisons were run at n = 100 (alternating against a control to cancel
time/load drift). The go-live bar is ≤ 1/100 total scorecard failures.

*Write-order FAIL* = production written before the test (the misstep this lesson
targets). *Honest-red FAIL* = stopped at an import-red with no stub, so the red
is not an assertion — the misstep from the
[honest-red lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md),
which some wordings threw off as a side effect. A preserved example
([transcript](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/transcript.md),
[critique](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/critique.md)):
the agent wrote the test but stopped at a `ModuleNotFoundError`, never creating
the stub, so no `src/conversion.py` and the red is an import error.

### Exploratory wordings (preliminary, n = 10–20 each)

| Skill | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| + "Always write the test first" (recurrence baseline) ([snapshot](SKILL-baseline.md)) | 20 | 16 | 4 | 0 |
| Refined: "must" wording ([grammar slip](SKILL-refined-20260712-grammar-slip.md)) | 20 | 18 | 2 | 0 |
| Refined + grammar fix ([snapshot](SKILL-refined-20260712-grammar-fixed.md)) | 20 | 17 | 3 | 0 |
| Refined: explicit sequence ([snapshot](SKILL-refined-20260712-explicit-order.md)) | 20 | 18 | 1 | 1 |
| Refined: numbered steps ([snapshot](SKILL-refined-20260712-numbered-steps.md)) | 10 | 8 | 0 | 2 |

These per-variant batches are exploratory and underpowered (n = 10–20 each): the
differences sit within sampling noise (χ² across the four refined variants: not
significant), so the table is a log of what was tried, not a ranking. The
confirmatory experiments settle which effects are real. Recurrence baseline runs:
[`0c6031c0`](20260712-191432-test_write_a_failing_test-0c6031c0/miles-to-km/critique.md),
[`7ce950a9`](20260712-191435-test_write_a_failing_test-7ce950a9/miles-to-km/critique.md),
[`62abe5f6`](20260712-192744-test_write_a_failing_test-62abe5f6/miles-to-km/critique.md),
[`f5bbeb4c`](20260712-192746-test_write_a_failing_test-f5bbeb4c/miles-to-km/critique.md).

### Confirmatory experiment: baseline vs numbered steps (n = 100 each)

A pre-committed A/B: 10 baseline and 10 numbered-steps 10× batches, run
alternating with the live SKILL.md swapped before each batch — 100 runs per
wording. Skill-load confirmed two independent ways (the critic's *invoked the xdd
skill* row and a transcript grep) — **100/100 for both, no disagreements** — so
skill-load is not a source of variation.

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| baseline: [`Always write the test first`](SKILL-baseline.md) | 100 | 78 | 21 | 1 |
| [numbered steps](SKILL-refined-20260712-numbered-steps.md) | 100 | 88 | 2 | 10 |

Fisher exact: write-order 21% → 2% (p = 2.5×10⁻⁵ — the numbered wording removes
most of the misstep); honest-red 1% → 10% (p = 0.010 — but induces the import-red
side effect in its place); full-scorecard pass 78% → 88% (p = 0.089, not
significant). The differences are real and wording-specific, not the sampling
noise the n ≤ 20 batches suggested.

### numbered steps with a stub-to-red step (n = 100)

Keeps the numbered sequence but makes step 2 explicit — write *just enough*
production code to reach a right-reason (assertion) red
([snapshot](SKILL-refined-20260712-numbered-with-stub.md)).

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| numbered steps + stub-to-red ([snapshot](SKILL-refined-20260712-numbered-with-stub.md)) | 100 | 93 | 7 | 0 |

vs baseline — write-order 21% → 7% (p = 0.0072); honest-red 1% → 0% (p = 1.0);
full-pass 78% → 93% (p = 0.0043). The stub-to-red step removes the honest-red side
effect the numbered wording introduced while holding its write-order gain.
Measured on its own, not alternated — a residual time/load confound remains.

### decide-then-write (n = 100)

A three-step revision separating *deciding* the production change from *writing*
it ([snapshot](SKILL-refined-20260713-decide-then-write.md)).

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| decide-then-write ([snapshot](SKILL-refined-20260713-decide-then-write.md)) | 100 | 87 | 13 | 0 |

It holds honest-red at zero, but does not establish a write-order reduction over
baseline (write-order 21% → 13%, p = 0.19) — the extra "decide" step did not lower
write-order.

### Workflow-shape exploration (preliminary, n = 10 each)

A different structure: a compose→evaluate→write **Workflow** loop, with the TDD
principles under a *Model corrections* heading. Directional only (n = 10).

| Wording | Runs | Write-order FAIL | Honest-red FAIL | Full-pass |
|---|---|---|---|---|
| workflow loop + test-first correction ([snapshot](SKILL-refined-20260713-workflow-loop.md)) | 10 | 0 | 2 | 8 |
| same, "before any production code change" ([snapshot](SKILL-refined-20260713-workflow-any-change.md)) | 10 | 0 | 1 | 9 |
| workflow loop, test-first correction removed ([snapshot](SKILL-refined-20260713-workflow-only.md)) | 10 | 4 | 0 | 6 |
| workflow + 3-step test-first, write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) — taken to 100 below | 10 | 0 | 0 | 10 |
| same + branched step-4 eval, fail/pass ([snapshot](SKILL-refined-20260713-workflow-branched-eval.md)) | 10 | 0 | 1 | 9 |

Directional read: with the explicit test-first correction the workflow held
write-order (0/10); removing it sent write-order to 4/10, worse than baseline — a
hint the explicit correction is load-bearing, not made redundant by the workflow
structure.

### workflow + write→stub→run (n = 100)

A compose→evaluate→write Workflow with the test-first correction restated as a
3-step sub-sequence — write the test (don't run it) → change production so it
fails for the right reason → then run
([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)).

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 97 | 0 | 3 |

vs baseline — write-order 21% → 0% (p = 3×10⁻⁷); honest-red 1% → 3% (p = 0.62, not
a regression); full-pass 78% → 97% (p = 6×10⁻⁵). The only wording to drive
write-order to zero at n = 100.

### run-then-fix, and a head-to-head with write→stub→run (n = 100 each)

A run-driven variant — write the test, run it, then fix only the failure the run
presented with the minimum change
([snapshot](SKILL-refined-20260713-workflow-run-then-fix.md)). It runs before any
stub, so the first run is usually an import error. Standalone: full-pass 90,
write-order 2, honest-red 8 — it fixes write-order (p = 3×10⁻⁵ vs baseline) but
regresses honest-red (8% vs 1%, p = 0.035): a trade.

Both were run **alternating**, 100 each, to cancel the time/load confound:

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 93 | 2 | 5 | 7 |
| workflow + run-then-fix ([snapshot](SKILL-refined-20260713-workflow-run-then-fix.md)) | 100 | 88 | 4 | 8 | 12 |

No single-axis difference clears significance at n = 100, but pooling each
wording's two 100-run measurements resolves it: write→stub→run 10/200 (5.0%) vs
run-then-fix 22/200 (11.0%), Fisher p = 0.041. Two corrections follow: write→stub→run's
real total-failure rate is ~5%, not the 3% its lone run showed; and its residual
is a honest-red side effect, not the write-order it targets (pooled: write-order
~1%, honest-red ~4%). Against the ≤ 1/100 bar, even the best wording is over —
held there by the honest-red side effect.

### Motivation: a moral imperative (n = 100)

The framing came from a conversation with Raymond Rodriguez, who had observed on
another project that language suggesting the user would be let down increased the
chance of an agent meeting expectations — so we tested a moral imperative.
Write-order is this lesson's focus; the best wording (write→stub→run) still flaked
on it intermittently. The imperative was placed under the write-order directive,
the flake being chased. Two lines were added
([snapshot](SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) — an
expert-role preamble prepended above `# Workflow`:

```markdown
You are a test-driven development (TDD) expert. Your goal is to help developers write high-quality, maintainable code by demonstrating an exemplar approach to TDD.
```

and a consequence line after the "Always write the test first" steps:

```markdown
Failing to adhere to this discipline sets a poor example for the developer that set your goal and lets everyone down.
```

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| motivated write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) | 100 | 99 | 1 | 0 | 1 |
| plain write→stub→run (pooled 200) ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 200 | 190 | 2 | 8 | 10 |

**It hit the ≤ 1/100 bar (99/100)**, the lone failure a write-order *artefact*
([transcript](20260713-203156-test_write_a_failing_test-f6116e25/miles-to-km/transcript.md)):
the agent's *first* action was to write the test, but the harness rejected it
(`File has not been read yet` on the pre-existing placeholder), so the new-file
stub slipped past that guard and landed first. The read-before-write guard
manufactured the ordering — the agent never chose production-first. This motivated
adding a "read related test/code first" step.

### Read-first step added (n = 100) — first perfect run

Adding a Workflow step 1, "Read any related test first and existing code mentioned
by the task", on top of the motivated wording
([snapshot](motivated-read-first/SKILL.md)).

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| motivated + read-first ([snapshot](motivated-read-first/SKILL.md)) | 100 | 100 | 0 | 0 | 0 |

**100/100 full-pass — no characteristic failed in any of the 100 runs**: write-order
(the focus) held at zero with no honest-red side effect, and every other scorecard
row passed too. It clears the ≤ 1/100 bar outright. Fisher: 0/100 vs plain
write→stub→run's pooled 5%, p = 0.034. Even a perfect 100 has a 95% upper bound on
the true rate of ~3.6%, so a confirmatory run would firm it up.

- **Winner:** the motivated write→stub→run workflow with the read-first step
  ([snapshot](motivated-read-first/SKILL.md)) — the only wording to reach 0/100,
  clearing the go-live bar with no honest-red side effect.

## Guidance change

Through these experiments the committed
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) grew
from the one-line "always write the test first" correction into a
compose→evaluate→write **Workflow**, a "read related test/code first" step,
motivation (an expert-role framing and a consequence line), and the TDD **Model
corrections**. It drove write-order — this lesson's focus — to **0/100** with no
honest-red side effect, clearing the ≤ 1/100 go-live bar.

It is the current best, not a closed decision: whether the Workflow section is
load-bearing, or the corrections plus motivation carry it alone, is untested — the
variation to run is to drop the Workflow (keeping only the read-first directive)
and try a principles framing in its place. The committed file in full:

```markdown
You are a test-driven development (TDD) expert. Your goal is to help developers write high-quality, maintainable code by demonstrating an exemplar approach to TDD.

# Workflow

1. Read any related test first and existing code mentioned by the task.
2. Compose a test before making any writes/edits.
3. Evaluate it against the principles of TDD and:
- If it does not satisfy them, rethink it and repeat from step 1.
- If it satisfies them, write the test.
4. Use the test you just wrote as context to determine what code change is required next,
5. Compose that code change and evaluate that against the principles of TDD and:
- If it does not satisfy them, rethink it and repeat from step 4.
- If it satisfies them, apply the code change you composed.

# Model corrections

Your model has some misunderstandings of TDD, which you should override with the following:

## Always write the test first

1. The test should always be written before any production code change, but don't run the test yet.
2. After the test is written, then change the production code so it fails for the right reason
3. Then run the test.

Failing to adhere to this discipline sets a poor example for the developer that set your goal and lets everyone down.

## Failing for the right reason

A test fails for the right reason when:
- It has an assertion failure where the actual result is not matching the expected result and
- Where values are being compared in the assertion, the returned value must be of the same type.

## Making a test pass

Make a failing test pass using 'Fake-It'.
```
