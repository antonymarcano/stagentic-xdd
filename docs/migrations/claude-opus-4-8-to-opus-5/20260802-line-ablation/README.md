# Line ablation — design

**Question:** what is the smallest `xdd-plugin/skills/xdd/SKILL.md` that
claude-opus-5 still needs?

The committed skill passes every critique, and a
[placeholder skill](SKILL-placeholder.md) that says only *"Apply Test-Driven
Development."* fails half of them. The gap is wide, so a wording that makes things
worse will show up as failures. This experiment finds the smallest wording that
keeps the committed skill's result.

## The units

Each snapshot is the committed skill with one thing removed. Everything else is
unchanged, and the remaining steps are renumbered so the document still reads
properly.

| arm | what it removes |
|---|---|
| [`SKILL-no-framing.md`](SKILL-no-framing.md) | the `# Model Corrections` heading and its sentence |
| [`SKILL-no-step1.md`](SKILL-no-step1.md) | *the test should always be written before any production code change, but don't run the test yet* |
| [`SKILL-no-step2.md`](SKILL-no-step2.md) | *change the production code so it fails for the right reason* |
| [`SKILL-no-step3.md`](SKILL-no-step3.md) | *then run the test* |
| [`SKILL-no-assertion.md`](SKILL-no-assertion.md) | the assertion-failure bullet under *Failing for the Right Reason* |
| [`SKILL-no-type.md`](SKILL-no-type.md) | the same-type bullet under *Failing for the Right Reason* |
| [`SKILL-no-fakeit.md`](SKILL-no-fakeit.md) | the *Making a Test Pass* section |

The `## Always Write the Test First` heading stays in every arm, so it is not
part of what is being measured.

## How a screen is run and read

```
bash scripts/verify-runs.sh .artefacts/20260802-line-ablation/<arm> 1 10
```

Ten runs, twenty critiques, no control arm and no early stop so counts stay
comparable.

- **One failure counts as a hit.** The committed skill passed 400 of 400
  critiques, so a single failure in twenty is strong evidence a line matters.
- **Read the failing characteristics, not just the pass count.** A characteristic
  maps to the line that addresses it, so a failure usually names its own cause.
  That is what removes the need to bisect.

## Sample size

A load-bearing line showed up at 5 failures in 20 — 25%. At twenty critiques the
chance of missing an effect that size is about 0.3%, so ten runs is adequate
power for the search. A clean twenty rules out a 25% effect; it does not rule out
a 5% one, which is why the final file is confirmed at 100 runs.

## Stage 1 — screen each unit

One unit removed at a time, to find any line that is needed on its own.

Removing one line asks whether it is needed *given all the others*. Where two
lines cover the same failure, neither looks needed alone, so a set of clean
single-unit screens does not mean the file is minimal — which is why stage 1 is a
starting point, not an answer.

## Stage 2 — remove the clean units together

Everything that screened clean is removed in one arm. Two outcomes:

- **Clean** — all of them go at once.
- **Fails** — the failing characteristics name which lines to put back. Restore
  only those, and screen the restored file.

Where a characteristic is addressed by more than one line, the attribution is
ambiguous, and the smaller candidate is worth one extra screen before settling.

## Stage 3 — greedy continuation

From the current candidate, remove one remaining unit at a time. A clean screen
makes the removal stick, and the next unit comes out of the already-smaller file.
A failure puts the unit back and marks it required.

This is what reaches a genuinely minimal file: each screen asks whether a line is
needed given only the lines still standing, rather than given all of them.

## Stage 4 — does motivation replace a correction?

The motivation was removed from the skill before this experiment began, so every
stage above reduces without it. It may still substitute for a correction once the
corrections are few.

Test it at the boundary, not with a second full sweep:

- Stage 3 stops at some removal that fails. Take **that exact file** and add the
  motivation back. One screen.
- **Passes** — the motivation substitutes for the correction that was removed,
  and there are now two candidate skills to compare on total size: fewer
  corrections with motivation, or more corrections without.
- **Fails** — the correction is needed regardless, and the motivation stays out.

One screen per stopping point. The extreme case — motivation with no corrections
at all — is measured as [`SKILL-motivation-only.md`](SKILL-motivation-only.md).

## Stage 5 — confirm once

Take the final file to 100 runs, alternating against the committed skill with
`compare-wordings.sh`. This single expensive run is what makes the provisional
twenty-run screens safe.

## What this design cannot see

- **A different minimal file.** Removing units in another order can leave a
  different set standing. The result is *a* minimal file, not *the* minimum.
- **Interactions other than the one in stage 4.** Any line may matter only in the
  presence of another; stage 4 tests that for the motivation alone.
