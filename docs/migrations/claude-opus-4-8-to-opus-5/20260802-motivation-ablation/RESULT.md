# Motivation ablation — result

**Question:** on claude-opus-5, does removing the xdd skill's motivation still
make the agent worse?

**Answer:** no. On claude-opus-4-8 removing it caused failures. On
claude-opus-5 it causes none.

## Failure rate, with and without the motivation

| model | with motivation | without motivation |
|---|---|---|
| claude-opus-4-8 | 1 failure in 100 | 10 failures in 200 — about **1 in 20** |
| claude-opus-5 | 0 failures in 400 | 0 failures in 400 — **none** |

- Taking the motivation out of claude-opus-4-8 meant roughly one run in twenty
  went wrong.
- Taking it out of claude-opus-5 changed nothing.
- Going from "1 in 20" to "none in 400" is far too big a change to be luck
  (Fisher 2-sided `p < 0.0001`).

## What was compared

Two snapshots of `xdd-plugin/skills/xdd/SKILL.md`, swapped over the live file
before each arm's runs:

- **arm A, `SKILL-current.md`** — the committed wording.
- **arm B, `SKILL-no-motivation.md`** — the same file with three lines removed:
  - the identity — *"You are a test-driven development (TDD) expert."*
  - the goal — *"Your goal is to help developers write high-quality,
    maintainable code…"*
  - the consequence — *"Failing to adhere to this discipline sets a poor example
    …and lets everyone down."*

All three come out together, because the consequence refers back to the goal.

## How it was run

- `scripts/compare-wordings.sh`, alternating arm A and arm B twenty times.
- Ten runs per arm each time — 200 runs per arm in total.
- Each run does both scenarios in `spec/tests/test_red_green_commit.py`, so each
  run produces two critiques. 200 runs = 400 critiques.

| | |
|---|---|
| Date | 2026-08-02 |
| CLI | claude 2.1.220 |
| Model | claude-opus-5 |
| Artefacts | `spec/.artefacts/20260802-1317-motivation-ablation/` |

## Result on claude-opus-5

| arm | critiques | passed | failed | skill loaded (critic / grep) |
|---|---|---|---|---|
| `current` | 400 | 400 | 0 | 400/400 · 400/400 |
| `no-motivation` | 400 | 400 | 0 | 400/400 · 400/400 |

Fisher 2-sided `p = 1.0000` — the two arms are the same.

## The claude-opus-4-8 result it is compared against

From [the recurrence
lesson](../../../lessons/20260712-1855-write-the-failing-test-before-the-production-code-RECURRED/lesson.md),
measured on claude-opus-4-8 under CLI 2.1.191. That scenario ran
`test_write_a_failing_test` on its own, so one run gave one critique.

| wording | critiques | passed | write-order FAIL | honest-red FAIL | failed |
|---|---|---|---|---|---|
| no motivation (pooled) | 200 | 190 | 2 | 8 | 10 (5.0%) |
| motivated | 100 | 99 | 1 | 0 | 1 (1.0%) |
| motivated + read-first (accepted) | 100 | 100 | 0 | 0 | 0 |

The motivation was kept because the motivated wording reached the acceptance bar
of under 1 failure in 100. The gap between the two wordings on that model was
not large enough to be certain of on its own (Fisher 2-sided `p = 0.107`).

## What the numbers say

- **The old failure rate is gone.** 5.0% of 400 critiques would be about 20
  failures. Arm B had none. Comparing the two — `[[10,190],[0,400]]` — gives
  Fisher 2-sided `p < 0.0001`.
- **Zero failures is not proof of zero.** With 0 in 400, the true rate could
  still be as high as about 0.75% — roughly 1 in 130 — and we would probably
  still see none. Anything rarer than that, this test cannot see.
- **This test can only show harm, not help.** Arm A passed everything too, so
  there were no failures for the motivation to prevent. It can show that taking
  the motivation out does not hurt. It cannot show how much keeping it helps.

The plain reading: claude-opus-5 writes the test first without being told why it
matters.

## Two things that weaken the comparison

- **The two unmotivated wordings are not the same file.** Arm B is today's
  wording minus three lines, so it still has the read-first step and the
  workflow. The claude-opus-4-8 "no motivation" wording had neither. Treat the
  cross-model number as a guide, not a like-for-like test.
- **The runs cover different work.** The claude-opus-4-8 runs did one scenario;
  these do two. Both tables count critiques, but these 400 cover more ground.

## What to do next

- **The measured wording can be adopted as it stands.**
  `SKILL-no-motivation.md` is a complete `SKILL.md`; copying it over
  `xdd-plugin/skills/xdd/SKILL.md` adopts the file these runs measured. Any
  further edit to it needs its own measurement.
- **The answer only holds for claude-opus-5 on CLI 2.1.220.** Per ADR
  [0003](../../../architecture/decisions/0003-pin-model-versions.md),
  guidance is measured against the pinned pair. Change the pin and the question
  is open again.
- **Do not split the three elements on this model.** Both arms pass everything,
  so testing identity, goal and consequence separately has nothing to separate.
  It is worth doing only against a scenario this model still fails.
