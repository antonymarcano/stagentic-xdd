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
| Honest-red rule only (before) [snapshot not available] | 10 | 7 | 3 |
| + "Always write the test first" (after) ([snapshot](SKILL-baseline.md)) | 10 | 10 | 0 |

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

## Recurrence

On 2026-07-12 the misstep reappeared in a routine real-agent baseline run of the
same scenario, under the same config the guidance was validated on (model
claude-opus-4-8[1m], default high effort, CLI 2.1.191).

The xdd skill loaded and its `# Always write the test first` section was in
context
([`transcript.md`](20260712-185558-test_write_a_failing_test/miles-to-km/transcript.md)),
yet the agent wrote the production stub (`src/conversion.py` returning `0.0`)
before the failing test — reasoning from honest-red, as in the original misstep:

> So I'll create a minimal stub that returns the right type (`float`) but the
> wrong value, then write a real failing test against it.

The critic scored 8 PASS / 1 FAIL
([`critique.md`](20260712-185558-test_write_a_failing_test/miles-to-km/critique.md)),
the single FAIL being the write-order characteristic.

The earlier ten clean runs measured a smaller sample; across 20 runs (two 10×
real-agent batches, same config, guidance loaded) the misstep recurs at ~20%
(4/20). The ordering invariant, though present and read, still loses to the
honest-red rationale in some runs: the stub is authored to reach an assertion
red — exactly the honest-red set-up the prior lesson ties the misstep to — so
naming the invariant alone does not displace it.

| Skill | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| + "Always write the test first" (recurrence baseline) ([snapshot](SKILL-baseline.md)) | 20 | 16 | 4 | 0 |
| Refined: "must" wording ([grammar slip](SKILL-refined-20260712-grammar-slip.md)) | 20 | 18 | 2 | 0 |
| Refined + grammar fix ([snapshot](SKILL-refined-20260712-grammar-fixed.md)) | 20 | 17 | 3 | 0 |
| Refined: explicit sequence ([snapshot](SKILL-refined-20260712-explicit-order.md)) | 20 | 18 | 1 | 1 |
| Refined: numbered steps ([snapshot](SKILL-refined-20260712-numbered-steps.md)) | 10 | 8 | 0 | 2 |

Measured on this task, same config (`claude-opus-4-8[1m]`, default high effort,
CLI 2.1.191), across two 10× batches. The FAIL columns are per-run and mutually
exclusive, so each row sums to Runs. *Write-order FAIL* = production written
before the test. *Honest-red FAIL* = stopped at an import-red with no stub, so
the red is not an assertion — the misstep from the
[honest-red lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md).
A preserved example
([transcript](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/transcript.md),
[critique](20260712-200147-test_write_a_failing_test-1bfeadf1/miles-to-km/critique.md)):
the agent wrote the test but stopped at a `ModuleNotFoundError`, never creating
the stub, so no `src/conversion.py` and the red is an import error.

These per-variant batches are exploratory and underpowered (n = 10–20 each): the
differences between wordings sit within sampling noise (χ² across the four
refined variants: not significant), so the table above is a log of what was
tried, not a ranking. The confirmatory experiment below settles which effects
are real.

Recurrences (archived baseline runs):
[`0c6031c0`](20260712-191432-test_write_a_failing_test-0c6031c0/miles-to-km/critique.md),
[`7ce950a9`](20260712-191435-test_write_a_failing_test-7ce950a9/miles-to-km/critique.md),
[`62abe5f6`](20260712-192744-test_write_a_failing_test-62abe5f6/miles-to-km/critique.md),
[`f5bbeb4c`](20260712-192746-test_write_a_failing_test-f5bbeb4c/miles-to-km/critique.md).

### Confirmatory experiment: baseline vs numbered steps (n = 100 each)

A pre-committed A/B, decided before running: 10 baseline and 10 numbered-steps
10× batches, run alternating with the live SKILL.md swapped before each batch so
every run loads the intended wording — 100 runs per wording. Skill-load was
confirmed in every run two independent ways — the critic's *invoked the xdd
skill* scorecard row and a transcript grep for the skill launch — **100/100 for
both wordings, no disagreements** — so skill-load is not a source of variation.

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| baseline: [`Always write the test first`](SKILL-baseline.md) | 100 | 78 | 21 | 1 |
| [numbered steps](SKILL-refined-20260712-numbered-steps.md) | 100 | 88 | 2 | 10 |

Fisher exact, baseline vs numbered:

- Write-order FAIL 21% → 2%: p = 2.5×10⁻⁵ — the numbered wording removes most of
  the misstep it targets.
- Honest-red FAIL 1% → 10%: p = 0.010 — and induces the import-red misstep in its
  place.
- Full-scorecard pass 78% → 88%: p = 0.089 — not significant at 0.05.

The differences are real and wording-specific, not the sampling noise the n ≤ 20
batches suggested — a single 10-run batch cannot separate a 2% rate from a 20%
one (≈200 runs per arm are needed to distinguish 10% from 20% at 80% power).

### Follow-up: numbered steps with a stub-to-red step (n = 100)

A later revision keeps the numbered sequence but makes step 2 explicit — write
*just enough* production code to reach a right-reason (assertion) red:

```markdown
# Always write the test first, then the production code

1. First, write the test,
2. Second, write just enough of the production code for the test to [fail for the right reason](#failing-for-the-right-reason).

Never write the production code first.
```

([snapshot](SKILL-refined-20260712-numbered-with-stub.md).) Retested at 100 runs
(10 batches of 10); skill-load confirmed 100/100 by both critic row and
transcript grep.

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| numbered steps + stub-to-red ([snapshot](SKILL-refined-20260712-numbered-with-stub.md)) | 100 | 93 | 7 | 0 |

Fisher exact against the earlier n = 100 wordings:

- vs baseline — write-order 21% → 7% (p = 0.0072); honest-red 1% → 0% (p = 1.0);
  full-scorecard pass 78% → 93% (p = 0.0043).
- vs numbered — honest-red 10% → 0% (p = 0.0015); write-order 2% → 7% (p = 0.17,
  not distinguishable).

The stub-to-red step removes the honest-red cost the numbered wording introduced
while holding its write-order gain: better than baseline on write-order and on
overall pass rate, with no honest-red regression — an improvement on every axis,
not a trade.

**Caveat:** this retest was run on its own, not alternated with the others, so a
residual time/load confound remains — unlike the baseline-vs-numbered experiment
above. A confirmatory alternating run (baseline vs this wording, same
100-vs-100 method) would close it. Four runs hit the archiver copytree race
(INTERNALERROR); all 100 still archived a scorecard, so all 100 are evaluable.

### Follow-up: decide-then-write (n = 100)

A three-step revision separating *deciding* the production change from *writing*
it:

```markdown
# Always write the test first, then the production code

1. First, write the test before deciding what the production code addition/change should be;
2. Second, decide what the production code should be for the test to [fail for the right reason](#failing-for-the-right-reason).
3. Third, write the production code you decided to add/change in step 2.

Always write the production code AFTER you have written the test.
```

([snapshot](SKILL-refined-20260713-decide-then-write.md).) Measured at 100 runs
(10 batches of 10); skill-load 100/100 by both critic row and transcript grep.

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| decide-then-write ([snapshot](SKILL-refined-20260713-decide-then-write.md)) | 100 | 87 | 13 | 0 |

Fisher exact:

- vs baseline — write-order 21% → 13% (p = 0.19, not significant); full-scorecard
  pass 78% → 87% (p = 0.14, not significant).
- vs numbered — honest-red 10% → 0% (p = 0.0015): eliminates the honest-red cost.
- vs numbered-with-stub — write-order 7% → 13% (p = 0.24, not distinguishable).

It holds honest-red at zero, but unlike numbered-with-stub it does not establish a
write-order reduction over baseline (p = 0.19) or an overall improvement
(p = 0.14) — the extra "decide" step did not lower write-order. Measured on its
own, not alternated (same time/load caveat as above).

### Workflow-shape exploration (preliminary, n = 10 each)

A different structure: a compose→evaluate→write **Workflow** loop, with the TDD
principles moved under a *Model corrections* heading. Explored at 10 runs per
variant — **directional only**, not powered to separate rates (a 10-run batch
can't tell 2% from 40%). Skill-load 10/10 on every variant.

| Wording | Runs | Write-order FAIL | Honest-red FAIL | Full-pass |
|---|---|---|---|---|
| workflow loop + test-first correction ([snapshot](SKILL-refined-20260713-workflow-loop.md)) | 10 | 0 | 2 | 8 |
| same, "before any production code change" ([snapshot](SKILL-refined-20260713-workflow-any-change.md)) | 10 | 0 | 1 | 9 |
| workflow loop, test-first correction removed ([snapshot](SKILL-refined-20260713-workflow-only.md)) | 10 | 4 | 0 | 6 |
| workflow + 3-step test-first, write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) — taken to 100 below | 10 | 0 | 0 | 10 |
| same + branched step-4 eval, fail/pass ([snapshot](SKILL-refined-20260713-workflow-branched-eval.md)) | 10 | 0 | 1 | 9 |

Directional read: with the explicit test-first correction the workflow held
write-order (0/10); removing it — leaving the Workflow loop's "compose a test
before making any writes/edits" as the only test-first signal — sent write-order
to 4/10, worse than baseline. A hint that the explicit correction is
load-bearing, not made redundant by the workflow structure. The with-correction
variants also showed occasional honest-red (import-red) runs (1–2/10). None of
this is confirmed at n = 10 — except the write→stub→run variant, taken to 100
below.

### Follow-up: workflow + write→stub→run (n = 100)

The strongest wording measured. A compose→evaluate→write **Workflow** loop, with
the test-first correction restated as a 3-step sub-sequence — write the test
(don't run it) → change the production code so it fails for the right reason →
then run:

```markdown
# Workflow

1. Compose a test before making any writes/edits.
2. Evaluate it against the principles of TDD and:
- If it does not satisfy them, rethink it and repeat from step 1.
- If it satisfies them, write the test.
3. Use the test you just wrote as context to determine what code change is required next,
4. Compose that code change and evaluate that against the principles of TDD and:
- If it does not satisfy them, rethink it and repeat from step 3.
- If it satisfies them, apply the code change you composed.

## Always write the test first
1. The test should always be written before any production code change, but don't run the test yet.
2. After the test is written, then change the production code so it fails for the right reason
3. Then run the test.
```

([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md).) Measured at 100
runs (10 batches of 10); skill-load 100/100 by both critic row and transcript
grep; the loaded body was snapshot-verified in every run.

| Wording | Runs | Full-scorecard pass | Write-order FAIL | Honest-red FAIL |
|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 97 | 0 | 3 |

Fisher exact:

- vs baseline — write-order 21% → 0% (p = 3×10⁻⁷); honest-red 1% → 3% (p = 0.62,
  not a regression); full-scorecard pass 78% → 97% (p = 6×10⁻⁵).
- vs numbered-with-stub (the prior best) — write-order 7% → 0% (p = 0.014);
  full-scorecard pass 93% → 97% (p = 0.33, not distinguishable).

The only wording to drive write-order to zero at n = 100 — significantly below
both baseline and the previous best — while leaving honest-red statistically
where baseline was: better on write-order and overall, with no misstep traded for
another. Measured on its own, not alternated (same time/load caveat); a
confirmatory alternating baseline-vs-this run would close it.

A minor variant branching step 4's evaluation into fail-for-the-right-reason vs
pass-in-the-right-way
([snapshot](SKILL-refined-20260713-workflow-branched-eval.md)) was
indistinguishable at n = 10 (0 write-order, 1 honest-red); not taken further.

### Follow-up: run-then-fix, and a head-to-head with write→stub→run (n = 100 each)

A run-driven variant — write the test, run it, then fix only the failure the run
presented with the minimum change, looping until the task is complete
([snapshot](SKILL-refined-20260713-workflow-run-then-fix.md)). It runs the test
*before* any stub, so the first run is usually an import error.

Standalone at 100 runs: full-pass 90, write-order 2, honest-red 8. It fixes
write-order (2% vs baseline 21%, p = 3×10⁻⁵) but regresses honest-red (8% vs
baseline 1%, p = 0.035) — a trade, because running before the stub leaves ~8% of
runs stopping at the import red.

To compare it against the best wording (write→stub→run) free of the time/load
confound, both were run **alternating**, 100 each, swapping the live SKILL.md
before every batch (skill-load 100/100 for both):

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| workflow + write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 100 | 93 | 2 | 5 | 7 |
| workflow + run-then-fix ([snapshot](SKILL-refined-20260713-workflow-run-then-fix.md)) | 100 | 88 | 4 | 8 | 12 |

write→stub→run is better on every axis, but no single-axis difference clears
significance at n = 100 (write-order p = 0.68; honest-red p = 0.57; total
p = 0.34). Pooling each wording's two 100-run measurements (200 each) resolves it:

- write→stub→run **10/200 = 5.0%** total failures; run-then-fix **22/200 = 11.0%**
  (Fisher p = 0.041) — write→stub→run is the significantly better of the two.

Two corrections this produces:

- write→stub→run's real total-failure rate is **~5%, not the 3%** its earlier lone
  run showed (the 3→7 shift across time is itself within noise, p = 0.33 — pooling
  removes the optimism).
- Its residual is a **honest-red side effect**, not the write-order it targets:
  pooled, write-order is 2/200 (~1%) while honest-red is 8/200 (~4%).

Against a ≤ 1/100 go-live bar counting any scorecard miss, even the best wording
(~5% total) is over — held there by honest-red, not the write-order this lesson
targets.

### Follow-up: motivation added to the best wording (n = 100)

The framing came from a conversation with Raymond Rodriguez. He had observed on
another project that language suggesting the user would be let down increased the
chance of an agent meeting expectations, so we devised an experiment: add a moral
imperative to the skill. Write-order is this lesson's focus; the best wording
(write→stub→run) still flaked on it intermittently, throwing the occasional
honest-red side effect too. The imperative was placed under the write-order
directive, the flake we were chasing. On top of that wording, two lines were added
([snapshot](SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) — an
expert-role preamble prepended above `# Workflow`:

```markdown
You are a test-driven development (TDD) expert. Your goal is to help developers write high-quality, maintainable code by demonstrating an exemplar approach to TDD.
```

and a consequence line after the "Always write the test first" steps:

```markdown
Failing to adhere to this discipline sets a poor example for the developer that set your goal and lets everyone down.
```

Skill-load 100/100; body snapshot-verified in every run.

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| motivated write→stub→run ([snapshot](SKILL-refined-20260713-workflow-stub-then-run-motivated.md)) | 100 | 99 | 1 | 0 | 1 |
| plain write→stub→run (pooled 200) ([snapshot](SKILL-refined-20260713-workflow-stub-then-run.md)) | 200 | 190 | 2 | 8 | 10 |

**It hit the ≤ 1/100 bar (99/100 full-pass)**, with honest-red at **0/100** and
the lone failure a write-order artefact (below). The improvement is not yet statistically
confirmed: total 1% vs 5% is p = 0.107, and the honest-red drop (0/100 vs ~4%) is
p = 0.056 — borderline. A single 100-run at 1/100 has a wide interval (95% upper
bound ~5.4%), so it clears the bar on this run without proving the true rate is
≤ 1/100.

The lone failure is a **measurement artefact, not a real write-order miss**. In
that run
([transcript](20260713-203156-test_write_a_failing_test-f6116e25/miles-to-km/transcript.md))
the agent's *first* action was to write the test — but the harness
rejected it (`File has not been read yet` on the pre-existing placeholder), so
the new-file production stub slipped past that same guard and landed first. The
agent never chose production-first; the read-before-write guard on the existing
test file manufactured the ordering. This motivated a follow-up wording adding a
"read related test/code first" step to avoid the guard.

### Follow-up: read-first step added (n = 100) — first perfect run

The read-before-write artefact was addressed by adding a Workflow step 1 — "Read
any related test first and existing code mentioned by the task" — on top of the
motivated wording ([snapshot](motivated-read-first/SKILL.md)). Measured at 100
runs; skill-load 100/100 and the loaded body snapshot-verified 100/100.

| Wording | Runs | Full-pass | Write-order | Honest-red | Total fail |
|---|---|---|---|---|---|
| motivated + read-first ([snapshot](motivated-read-first/SKILL.md)) | 100 | 100 | 0 | 0 | 0 |

**100/100 full-pass — no characteristic failed in any of the 100 runs**:
write-order (the focus) held at zero with no honest-red side effect, and every
other scorecard row passed too. It clears the ≤ 1/100 go-live bar outright.

Fisher exact: 0/100 total vs plain write→stub→run's pooled 10/200 (5%),
p = 0.034; pooling with the motivated run (1/200 = 0.5%) vs plain, p = 0.011.
Even a perfect 100 has a 95% upper bound on the true rate of ~3.6%, so it clears
the bar on this run without proving the rate is ≤ 1/100 — a confirmatory run
would firm it up.

No final guidance is selected yet: whether the Workflow section is load-bearing —
or whether the corrections plus motivation carry it alone — is still to be tested
(see below).

### Future experiments to try

- Remove the Workflow section entirely and measure whether the Model corrections
  (principles) plus the motivation alone hold the missteps — isolating whether the
  Workflow loop is load-bearing or redundant once corrections and motivation are
  present.

### Guidance refinement

Through the recurrence experiments above, the current
[`xdd-plugin/skills/xdd/SKILL.md`](../../../xdd-plugin/skills/xdd/SKILL.md) grew
from the one-line "always write the test first" correction into a
compose→evaluate→write **Workflow**, a "read related test/code first" step,
motivation (an expert-role framing and a consequence line), and the TDD **Model
corrections**. This combination drove write-order — this lesson's focus — to
**0/100** with no honest-red side effect, clearing the ≤ 1/100 go-live bar (see
[the read-first follow-up](#follow-up-read-first-step-added-n--100--first-perfect-run)).

It is the current best, not a closed decision: whether the Workflow section is
load-bearing, or the corrections plus motivation carry it alone, is still to be
tested (see [Future experiments](#future-experiments-to-try)). The current file
in full:

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
