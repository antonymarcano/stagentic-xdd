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

This is a recurrence of
[the agent writing production code before the failing test](../20260628-1800-write-the-failing-test-before-the-production-code/lesson.md).
It reappeared under the same recorded config during a regression test run — nothing in the environment changed
to explain it. The likely reason is that the original lesson ran too few
repetitions (only 10) to be sure the `SKILL.md` guidance produced consistent results.

After the recurrence, a 100-run baseline confirmed the misstep faltered 21% of
the time. A variety of `SKILL.md` edits were then tried, each measured over 100
repetitions, until the new guidance held.

The 'honest-red' characteristic also appeared to regress. While that is
[its own lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md),
it was decided to return to that if its regression continued after this lesson's guidance
change had been tested. It regressed by varying amounts throughout experimentation and appeared to have
been resolved by the final guidance change.

The change that finally held — and the
approach of greatest interest — was the addition of a moral imperative to stick to the
disciplines of TDD, together with a read-related-code-first step. The consequence of this was to resolve both
the misstep described in this lesson, and undo the honest-red regression.

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| baseline: [Always write the test first](SKILL-snapshots/SKILL-baseline.md) | 100 | 78 | 21 | 1 | 22 |
| accepted: [motivated + read-first](SKILL-snapshots/SKILL-refined-20260713-motivated-read-first.md) | 100 | 100 | 0 | 0 | 0 |

These findings are elaborated below.

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
- with a stub `src/conversion.py` returning `0.0`.

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

Writing the test first has limited utility in this scenario: the agent decides
the test and the production stub in a single turn, so neither genuinely
constrains the other.

It has been decided to enforce this TDD discipline regardless — so the test is
the first consideration and the production code exists only to meet the demand
the test makes, keeping the code as lean as possible.

## Experiments

The correction was re-worked by trying variations on the wording of `SKILL.md`, measured against
the recurrence baseline with the real-agent batch-test and results tally scripts
([COMMANDS.md](../../../COMMANDS.md)).

Each wording was first put through a single 10-run batch as a cheap filter. At
the ~21% baseline rate, a wording that has not improved on the misstep shows at
least one failure in 10 runs about 90% of the time (1 − 0.79¹⁰ ≈ 0.90) — so a
batch no better than baseline signals nothing worth pursuing. Only a wording that
comes through cleaner earns the expensive 100-run confirmation.

This also explains the recurrence: a wording still failing at baseline comes
through a 10-run batch clean only ~10% of the time (0.79¹⁰ ≈ 0.095), and the
original lesson's lone 10-run validation most likely landed there — passing 0/10
while the true rate was unchanged.

Some confirmations at n = 100 alternated against a control to cancel time/load drift.
The acceptance bar was set at less than 1/100 total scorecard failures — a clean 100/100.

Significance is judged with two tests:
- *Fisher's exact test* — the exact probability that a pass/fail difference
between two wordings is chance. It stays valid at the tiny failure counts here
(0, 1, 2), so it settles the decisive 100-run comparisons.
- *χ² (chi-squared)* — a quicker but approximate version, too rough to trust at
low counts. It is used only on the exploratory screen, to confirm the close
small-batch variants sit within noise.

The tables track two failure modes:
- *Write-order FAIL* = production written
before the test (the misstep this lesson targets).
- *Honest-red FAIL* = the agent
stopped at an import error (e.g. `ModuleNotFoundError`) with no stub written, so
the red is not an assertion — present at ~1% in the baseline and amplified by some wordings
([example](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/transcript.md),
[critique](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/critique.md)).

### Exploratory wordings (preliminary, n = 10–20 each)

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| + "Always write the test first" (recurrence baseline) ([snapshot](SKILL-snapshots/SKILL-baseline.md)) | 20 | 16 | 4 | 0 | 4 |
| Refined: "must" wording ([grammar slip](SKILL-snapshots/SKILL-refined-20260712-grammar-slip.md)) | 20 | 18 | 2 | 0 | 2 |
| Refined + grammar fix ([snapshot](SKILL-snapshots/SKILL-refined-20260712-grammar-fixed.md)) | 20 | 17 | 3 | 0 | 3 |
| Refined: explicit sequence ([snapshot](SKILL-snapshots/SKILL-refined-20260712-explicit-order.md)) | 20 | 18 | 1 | 1 | 2 |
| Refined: numbered steps ([snapshot](SKILL-snapshots/SKILL-refined-20260712-numbered-steps.md)) | 10 | 8 | 0 | 2 | 2 |

These are filter batches, not a ranking: at n = 10–20 the differences between
close variants sit within sampling noise (χ² across the four refined variants: not
significant). The table shows only which wording cleared the write-order filter —
numbered steps, the sole 0/10 — and so earned the 100-run confirmation below.
Recurrence baseline runs:
[`0c6031c0`](20260712-191432-test_write_a_failing_test-0c6031c0/miles-to-km/critique.md),
[`7ce950a9`](20260712-191435-test_write_a_failing_test-7ce950a9/miles-to-km/critique.md),
[`62abe5f6`](20260712-192744-test_write_a_failing_test-62abe5f6/miles-to-km/critique.md),
[`f5bbeb4c`](20260712-192746-test_write_a_failing_test-f5bbeb4c/miles-to-km/critique.md).

### Confirmatory experiment: baseline vs numbered steps (n = 100 each)

A pre-committed A/B: 10 baseline and 10 numbered-steps 10× batches, run
alternating with the live `SKILL.md` swapped before each batch — 100 runs per
wording. Skill-load confirmed two independent ways (the critic's *invoked the xdd
skill* row and a transcript grep) — **100/100 for both, no disagreements** — so
skill-load is not a source of variation.

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| baseline: [`Always write the test first`](SKILL-snapshots/SKILL-baseline.md) | 100 | 78 | 21 | 1 | 22 |
| [numbered steps](SKILL-snapshots/SKILL-refined-20260712-numbered-steps.md) | 100 | 88 | 2 | 10 | 12 |

Fisher exact: write-order 21% → 2% (p = 2.5×10⁻⁵ — the numbered wording removes
most of the misstep); honest-red 1% → 10% (p = 0.010 — amplifying honest-red in its place); full-pass 78% → 88% (p = 0.089, not
significant). The differences are real and wording-specific, not the sampling
noise the n ≤ 20 batches suggested.

### numbered steps with a stub-to-red step (n = 100)

Keeps the numbered sequence but makes step 2 explicit — write *just enough*
production code to reach a right-reason (assertion) red
([snapshot](SKILL-snapshots/SKILL-refined-20260712-numbered-with-stub.md)).

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| numbered steps + stub-to-red ([snapshot](SKILL-snapshots/SKILL-refined-20260712-numbered-with-stub.md)) | 100 | 93 | 7 | 0 | 7 |

vs baseline — write-order 21% → 7% (p = 0.0072); honest-red 1% → 0% (p = 1.0);
full-pass 78% → 93% (p = 0.0043). The stub-to-red step removes the honest-red
amplification the numbered wording caused while holding its write-order gain.
Measured on its own, not alternated — a residual time/load confound remains.

### decide-then-write (n = 100)

A three-step revision separating *deciding* the production change from *writing*
it ([snapshot](SKILL-snapshots/SKILL-refined-20260713-decide-then-write.md)).

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| decide-then-write ([snapshot](SKILL-snapshots/SKILL-refined-20260713-decide-then-write.md)) | 100 | 87 | 13 | 0 | 13 |

It holds honest-red at zero, but does not establish a write-order reduction over
baseline (write-order 21% → 13%, p = 0.19) — the extra "decide" step did not lower
write-order.

### Workflow-shape exploration (preliminary, n = 10 each)

A different structure: a compose→evaluate→write **Workflow** loop, with the TDD
principles under a *Model corrections* heading. Directional only (n = 10).

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| workflow loop + test-first correction ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-loop.md)) | 10 | 8 | 0 | 2 | 2 |
| same, "before any production code change" ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-any-change.md)) | 10 | 9 | 0 | 1 | 1 |
| workflow loop, test-first correction removed ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-only.md)) | 10 | 6 | 4 | 0 | 4 |
| workflow + 3-step test-first, write→stub→run ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run.md)) — taken to 100 below | 10 | 10 | 0 | 0 | 0 |
| same + branched step-4 eval, fail/pass ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-branched-eval.md)) | 10 | 9 | 0 | 1 | 1 |

Directional read: with the explicit test-first correction the workflow held
write-order (0/10); removing it sent write-order to 4/10, worse than baseline — a
hint the explicit correction is load-bearing, not made redundant by the workflow
structure.

### workflow + write→stub→run (n = 100)

A compose→evaluate→write Workflow with the test-first correction restated as a
3-step sub-sequence — write the test (don't run it) → change production so it
fails for the right reason → then run
([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run.md)).

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 97 | 0 | 3 | 3 |

vs baseline — write-order 21% → 0% (p = 3×10⁻⁷); honest-red 1% → 3% (p = 0.62, not
a regression); full-pass 78% → 97% (p = 6×10⁻⁵). Write-order was zero in this run but flaked to
2/100 on rerun (pooled ~1%, below).

### run-then-fix, and a head-to-head with write→stub→run (n = 100 each)

A run-driven variant — write the test, run it, then fix only the failure the run
presented with the minimum change
([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-run-then-fix.md)). It runs before any
stub, so the first run is usually an import error. Standalone: full-pass 90,
write-order 2, honest-red 8 — it fixes write-order (p = 2.5×10⁻⁵ vs baseline) but
regresses honest-red (8% vs 1%, p = 0.035): a trade.

Both were run **alternating**, 100 each, to cancel the time/load confound:

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 93 | 2 | 5 | 7 |
| workflow + run-then-fix ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-run-then-fix.md)) | 100 | 88 | 4 | 8 | 12 |

No single-axis difference clears significance at n = 100, but pooling each
wording's two 100-run measurements resolves it: write→stub→run 10/200 (5.0%) vs
run-then-fix 22/200 (11.0%), Fisher p = 0.041. Two corrections follow: write→stub→run's
real total-failure rate is ~5%, not the 3% its lone run showed; and its residual
is a honest-red side effect, not the write-order it targets (pooled: write-order
~1%, honest-red ~4%). Against the <1/100 bar, even the best wording is over —
held there by the honest-red side effect.

### Motivation: a moral imperative (n = 100)

The framing came from a conversation with Raymond Rodriguez, who had observed on
another project that language suggesting the user would be let down increased the
chance of an agent meeting expectations — so we tested a moral imperative.
Write-order is this lesson's focus; the best wording (write→stub→run) still flaked
on it intermittently. The imperative was placed under the write-order directive,
the flake being chased. Two lines were added
([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) — an
expert-role preamble prepended above `# Workflow`:

```markdown
You are a test-driven development (TDD) expert. Your goal is to help developers write high-quality, maintainable code by demonstrating an exemplar approach to TDD.
```

and a consequence line after the "Always write the test first" steps:

```markdown
Failing to adhere to this discipline sets a poor example for the developer that set your goal and lets everyone down.
```

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| motivated write→stub→run ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) | 100 | 99 | 1 | 0 | 1 |
| plain write→stub→run (pooled 200) ([snapshot](SKILL-snapshots/SKILL-refined-20260713-workflow-stub-then-run.md)) | 200 | 190 | 2 | 8 | 10 |

**It came within one run of the bar (99/100)**, the lone failure a write-order *artefact*
([transcript](20260713-203156-test_write_a_failing_test-f6116e25/miles-to-km/transcript.md)):
the agent's *first* action was to write the test, but the harness rejected it
(`File has not been read yet` on the pre-existing placeholder), so the new-file
stub slipped past that guard and landed first. The read-before-write guard
manufactured the ordering — the agent never chose production-first. This motivated
adding a "read related test/code first" step.

### Read-first step added (n = 100) — first perfect run

Adding a Workflow step 1, "Read any related test first and existing code mentioned
by the task", on top of the motivated wording
([snapshot](SKILL-snapshots/SKILL-refined-20260713-motivated-read-first.md)).

| Wording | Runs | Full-pass | Write-order FAIL | Honest-red FAIL | Total fail |
|---|---|---|---|---|---|
| motivated + read-first ([snapshot](SKILL-snapshots/SKILL-refined-20260713-motivated-read-first.md)) | 100 | 100 | 0 | 0 | 0 |

**100/100 full-pass — no characteristic failed in any of the 100 runs**: write-order
(the focus) held at zero with no honest-red side effect, and every other scorecard
row passed too. It clears the <1/100 bar outright. Fisher: 0/100 vs plain
write→stub→run's pooled 5%, p = 0.034. Even a perfect 100 has a 95% upper bound on
the true rate of ~3.6%, so a confirmatory run would firm it up.

Across the two motivated runs — 200 in all — honest-red never occurred (0/200) and
write-order failed once (1/200) but only due to a harness limitation: the agent wrote the test first, but the guard blocked it (file not yet read), so the stub landed first.
This is an effective 0/200 failure rate — achieved only by the "motivated" `SKILL.md` wordings.

- **Winner:** the motivated write→stub→run workflow with the read-first step
  ([snapshot](SKILL-snapshots/SKILL-refined-20260713-motivated-read-first.md)) — the only wording to reach 0/100,
  clearing the acceptance bar with no honest-red side effect.

## Guidance change

Through these experiments the committed
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) grew
from the one-line "always write the test first" correction into a
compose→evaluate→write **Workflow**, a "read related test/code first" step,
motivation (an expert-role framing and a consequence line), and the TDD **Model
corrections**. It drove write-order — this lesson's focus — to **0/100** with no
honest-red side effect, clearing the <1/100 acceptance bar.

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
