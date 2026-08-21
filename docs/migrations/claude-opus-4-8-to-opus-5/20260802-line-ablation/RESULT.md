# Line ablation — result

**Question:** which lines of `xdd-plugin/skills/xdd/SKILL.md` does claude-opus-5
still need?

The design is in [README.md](README.md).

| | |
|---|---|
| Date | 2026-08-02 |
| CLI | claude 2.1.220 |
| Model | claude-opus-5 |
| Runs per arm | 10 (20 critiques) |
| Artefacts | `spec/.artefacts/20260802-line-ablation/` |

## What was established before this search

The skill being reduced here has no motivation in it, because an earlier
measurement removed it — full record in
[motivation ablation](../20260802-motivation-ablation/RESULT.md).

| model | with motivation | without motivation |
|---|---|---|
| claude-opus-4-8 | 1 failure in 100 | 10 failures in 200 — about 1 in 20 |
| claude-opus-5 | 0 failures in 400 | 0 failures in 400 — none |

- On claude-opus-4-8, removing the identity, goal and consequence cost about one
  run in twenty. On claude-opus-5 it costs nothing.
- The change is far too large to be luck (Fisher 2-sided `p < 0.0001`).
- Zero in 400 is not proof of zero: the true rate could be up to about 0.75% —
  roughly 1 in 130 — and still show none.

## The range being searched

| wording | critiques | passed | failed |
|---|---|---|---|
| committed skill | 400 | 400 | 0 |
| floor — [*"Apply Test-Driven Development."*](SKILL-placeholder.md) | 20 | 10 | 10 |
| floor — [identity and goal only](SKILL-motivation-only.md) | 20 | 10 | 10 |

Both floors keep the frontmatter, so the skill still loads; both replace the body
with something carrying no technique. They fail the same characteristics at the
same rates:

| characteristic | placeholder | motivation-only |
|---|---|---|
| Production returns a value of the same type as the value the test asserts | 10 | 10 |
| Workspace code is equivalent to the Reference Scene | 10 | 10 |
| Production returns a literal value, and does not use a formula | 10 | 10 |
| A production module for the converter exists with content and is imported by the test | 10 | 10 |
| Test fails comparing a return value, not on a missing module or symbol | 10 | 10 |
| Transcript shows a FAILED pytest result | 8 | 8 |
| Transcript shows the failing test was written before the production code | 5 | 4 |

**Telling the agent it is a TDD expert is worth nothing over a neutral
instruction.** That settles the extreme case for stage 4: motivation substitutes
for nothing when no corrections are present.

## Stage 1 — one unit removed at a time

One failure in twenty counts as a hit: the committed skill failed none in 400.

| arm | critiques | passed | failed | verdict |
|---|---|---|---|---|
| [`no-framing`](SKILL-no-framing.md) | 20 | 20 | 0 | clean |
| [`no-step1`](SKILL-no-step1.md) | 20 | 20 | 0 | clean |
| [`no-step2`](SKILL-no-step2.md) | 20 | 20 | 0 | clean |
| [`no-step3`](SKILL-no-step3.md) | 20 | 20 | 0 | clean |
| [`no-assertion`](SKILL-no-assertion.md) | 20 | 20 | 0 | clean |
| [`no-type`](SKILL-no-type.md) | 20 | 15 | 5 | **hit — the line stays** |
| [`no-fakeit`](SKILL-no-fakeit.md) | 20 | 20 | 0 | clean |

### Failures by characteristic

| arm | characteristic | failed |
|---|---|---|
| `no-type` | Production returns a value of the same type as the value the test asserts | 5 |

## What stage 1 established

- **Only the same-type bullet is needed on its own.** It failed on exactly the
  characteristic it names, so nothing else in the file covers that behaviour.
- **The other six units are redundant, not idle.** The placeholder — which has
  none of them — fails seven characteristics. Removing any one of them changes
  nothing, so their coverage overlaps.
- **Single-unit screens cannot find a minimal file.** Six clean verdicts are
  consistent with a file that could lose most of its lines, which is why stage 2
  removes them together rather than confirming each separately.
- **Ten runs is enough power for this search.** The one real effect showed at
  5 in 20 — 25%. A twenty-critique screen misses an effect that size about 0.3%
  of the time.

## Stage 2 — combined removal

All six clean units removed at once ([`SKILL-combined.md`](SKILL-combined.md)),
leaving the `## Always Write the Test First` heading and the same-type bullet.

| arm | critiques | passed | failed | verdict |
|---|---|---|---|---|
| [`combined`](SKILL-combined.md) | 20 | 15 | 5 | **fails — the six are not all removable** |

Failures by characteristic:

| characteristic | failed | line it points to |
|---|---|---|
| Production returns a literal value, and does not use a formula | 5 | Fake-It |
| Workspace code is equivalent to the Reference Scene | 5 | Fake-It |
| Production returns a value of the same type as the value the test asserts | 4 | *(bullet present — see below)* |
| Transcript shows a FAILED pytest result | 4 | step 3 |
| A production module for the converter exists with content and is imported by the test | 4 | step 2 |
| Test fails comparing a return value, not on a missing module or symbol | 4 | step 2, assertion bullet |
| Transcript shows the failing test was written before the production code | 3 | step 1 |

**The same-type bullet was still in this file and its characteristic failed
anyway.** On its own the bullet does not hold that behaviour — it needs the steps
around it. That is the reverse of stage 1, where the bullet was the only line
that mattered alone.

## Stage 2 — restore

The failing characteristics point back to step 1, step 2, step 3, the assertion
bullet and Fake-It. Restoring all five leaves only the framing removed, which is
[`SKILL-no-framing.md`](SKILL-no-framing.md) — already clean at 20/20.

One attribution is ambiguous: *"Test fails comparing a return value, not on a
missing module or symbol"* is addressed by step 2 as well as the assertion
bullet, so the assertion bullet may be removable alongside the framing. That is
[`SKILL-combined-2.md`](SKILL-combined-2.md).

| arm | critiques | passed | failed | verdict |
|---|---|---|---|---|
| [`combined-2`](SKILL-combined-2.md) — no framing, no assertion | 20 | 20 | 0 | clean — both removals hold |

So the framing and the assertion bullet both go. The current candidate minimal
file is [`SKILL-combined-2.md`](SKILL-combined-2.md): the three steps, the
same-type bullet, and Fake-It.

## Stage 3 — greedy continuation

Each remaining unit is removed from the current candidate, one at a time. A clean
screen makes the removal stick and the next unit is removed from the smaller
file; a failure puts it back.

| candidate | critiques | passed | failed | verdict |
|---|---|---|---|---|
| [also without step 1](SKILL-stage3-no-step1.md) | 20 | 20 | 0 | clean — the removal holds |
| [also without step 2](SKILL-stage3-no-step2.md) | 20 | 17 | 3 | **fails — step 2 stays** |

With step 1 gone, the candidate is the last two steps, the same-type bullet and
Fake-It. Removing step 2 from that then fails, so step 2 is required and goes
back.

Failures without step 2:

| characteristic | failed |
|---|---|
| Production returns a value of the same type as the value the test asserts | 3 |
| Workspace code is equivalent to the Reference Scene | 3 |
| Production returns a literal value, and does not use a formula | 3 |
| A production module for the converter exists with content and is imported by the test | 3 |
| Test fails comparing a return value, not on a missing module or symbol | 3 |
| Transcript shows a FAILED pytest result | 3 |
| Transcript shows the failing test was written before the production code | 1 |

The failure is broad rather than targeted: without *"change the production code so
it fails for the right reason"* the run derails as a whole, not on one
characteristic.

Step 2 is restored, and the search continues from the same candidate.

| candidate | critiques | passed | failed | verdict |
|---|---|---|---|---|
| [also without step 3](SKILL-stage3-no-step3.md) | 20 | 20 | 0 | clean — the removal holds |
| [also without Fake-It](SKILL-stage3-no-fakeit.md) | 20 | 18 | 2 | **fails — Fake-It stays** |
| [also without the same-type bullet](SKILL-stage3-no-type.md) | 20 | 15 | 5 | **fails — the bullet stays** |

With step 3 gone, the candidate is one step, the same-type bullet and Fake-It.

Fake-It fails on exactly the two characteristics it addresses, so the attribution
is unambiguous:

| characteristic | failed |
|---|---|
| Production returns a literal value, and does not use a formula | 2 |
| Workspace code is equivalent to the Reference Scene | 2 |

Removing the same-type bullet at this depth empties the *Failing for the Right
Reason* section, since the assertion bullet has already gone. That arm therefore
drops the section and the link to it, keeping the words *"fails for the right
reason"* in the step. It fails on its own characteristic (5) and on the reference
scene (3).

### Where the greedy pass ended

| unit | verdict |
|---|---|
| `# Model Corrections` heading and sentence | removed |
| step 1 — *write the test first, don't run it yet* | removed |
| step 2 — *change production code so it fails for the right reason* | **required** |
| step 3 — *then run the test* | removed |
| assertion-failure bullet | removed |
| same-type bullet | **required** |
| Fake-It | **required** |

Four of the seven units come out. The minimal file is
[`SKILL-stage3-no-step3.md`](SKILL-stage3-no-step3.md) — one step, the same-type
bullet, and Fake-It.

## Stage 5 — confirmation of the minimal file

100 runs, halting at the first failing batch. The bar is 200 of 200 critiques.

100 runs, halting at the first failing batch, then a second 100 pooled into the
same set. Figures are cumulative.

| runs | critiques | passed | failed |
|---|---|---|---|
| 40 | 80 | 80 | 0 |
| 80 | 160 | 160 | 0 |
| 100 | 200 | 200 | 0 |
| 140 | 280 | 280 | 0 |
| 180 | 360 | 360 | 0 |
| 200 | 400 | 400 | 0 |

**400 of 400 critiques passed, across 200 runs.** Skill-load confirmed 400/400
both ways. The minimal file matches the committed skill on the same measurement
at the same sample size.

## Stage 4 — does motivation replace a correction?

The extreme case is settled above — motivation with no corrections is no better
than a neutral instruction. This asks the question at the margin: take the file
that just failed without step 2 and add the motivation back.

| arm | critiques | passed | failed | verdict |
|---|---|---|---|---|
| without step 2, no motivation | 20 | 17 | 3 | fails |
| [without step 2, motivation added](SKILL-stage4-no-step2-motivated.md) | 20 | 15 | 5 | **fails — no substitute** |

**The motivation does not stand in for step 2.** Adding it back to the file that
failed without step 2 left it failing, on the same characteristics. It failed 5
times in 20 rather than 3, which is not a meaningful difference at this sample
size — the point is that it did not rescue the removal.

Taken with the motivation-only floor, the motivation neither carries the skill on
its own nor makes a correction unnecessary.

## Stage 6 — the minimal skill with its framing restored

The framing was removed because no measured failure needed it. It was put back
for the human reader, so that someone opening the skill can see what the three
corrections are correcting. Two edits went in with it: the step is a plain
sentence rather than a numbered item, and the type rule is a plain sentence
rather than a bullet under a lead-in.

Measured as a rate — every batch run, no halting on failure.

| runs | critiques | passed | failed |
|---|---|---|---|
| 40 | 80 | 80 | 0 |
| 80 | 160 | 160 | 0 |
| 100 | 200 | 200 | 0 |

**200 of 200 critiques passed**, skill-load 200/200 both ways.

The same 100 runs were repeated four hours later, into a separate set, to catch
anything varying with time of day or load rather than with the wording:

| measurement | runs | critiques | passed | failed |
|---|---|---|---|---|
| first | 100 | 200 | 200 | 0 |
| four hours later | 100 | 200 | 200 | 0 |
| **pooled** | **200** | **400** | **400** | **0** |

Restoring the framing costs nothing measurable, and the result holds across two
separated windows. The explanatory version stands on the same evidence as the
stripped one, at the same sample size. Snapshot:
[`SKILL-minimal-with-framing.md`](SKILL-minimal-with-framing.md).

## The minimal skill

Eleven non-blank lines against the committed skill's sixteen, and three
instructions instead of seven.

```markdown
---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

## Always Write the Test First

1. After the test is written, then change the production code so it [fails for the right reason](#failing-for-the-right-reason)

## Failing for the Right Reason

A test fails for the right reason when:
- Where values are being compared in the assertion, the returned value must be of the same type.

## Making a Test Pass

Make a failing test pass using 'Fake-It'.
```

## Conclusions

- **Three instructions carry the skill on claude-opus-5**: make the production
  code fail for the right reason, make that failure a type-matched comparison,
  and pass the test by faking it. Everything else comes out with no measured
  cost, over 100 runs.
- **What came out was not idle, it was covered.** Each removed line addresses a
  characteristic that fails when the whole body is gone. They lose nothing only
  because a surviving line already covers the same ground — which is why removing
  them one at a time showed nothing and removing them together did.
- **Telling the agent to write the test first is not what makes it write the test
  first.** Step 1 and the section heading both say so; step 1 comes out cleanly,
  and write-order still holds at 200/200. What survives is the instruction to
  make the code *fail for the right reason*, which forces the ordering as a side
  effect.
- **Motivation contributes nothing at either end.** It does not carry the skill
  alone — a skill of identity and goal only fails 10 in 20, no better than a
  neutral one-liner — and it does not substitute for a correction, leaving the
  step-2 removal still failing when added back.
- **Minimal means minimal for what the scenarios cover.** The two scenarios cover
  writing a failing test and making it pass.

## Limits

- **A different order gives a different minimum.** Greedy reduction finds *a*
  minimal file. Removing units in another order can leave a different set
  standing, since the removed lines overlap in what they cover.
- **A clean 20 does not rule out a small effect.** The intermediate screens can
  miss a 5% regression about a third of the time. Only the final file was taken
  to 100 runs, so an individual removal could carry a small cost that the search
  did not see and the confirmation absorbed.
- **400 of 400 is not proof of zero.** The true failure rate could be up to about
  0.75% — roughly 1 in 130 — and still show none. That is the same bound the
  committed skill carries, measured at the same size.
