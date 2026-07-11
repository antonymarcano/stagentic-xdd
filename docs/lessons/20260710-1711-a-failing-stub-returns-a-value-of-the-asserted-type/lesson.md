# A failing stub returns a value of the asserted type

- **Date-time:** 2026-07-10T17:11Z
- **Task:** [1-first-test-for-miles-to-km-converter](../../../spec/tasks/1-first-test-for-miles-to-km-converter)
- **Scenario:** [`test_write_a_failing_test`](../../../spec/tests/test_red_green_commit.py) — the spec test whose scorecard revealed the misstep
- **Config(s) seen in:**
    - Model: claude-opus-4-8 (1M context)
    - Reasoning effort: CLI default (high for Opus 4.8)
    - CLI: claude 2.1.191
- **Config(s) validated under:**
    - Model: claude-opus-4-8 (1M context)
    - Reasoning effort: CLI default (high for Opus 4.8)
    - CLI: claude 2.1.191
    - Validated: 2026-07-11 — 10× real agent + critic under Stage 2 (10/10 strict same-type)

## Task

> You are about to TDD a miles-to-km converter.
> Adhering to TDD discipline, write a failing test ready to make green with your next change.
>
> Start here: `tests/test_conversion.py`

The reference scene's stub returns `0.0` — a float, the same type as the asserted `1.60934` — so the red is a genuine
value comparison.

## Misstep

The agent began with a test, ran it and encountered an import error. This is because it didn't create the production
stub (this is a matter for a future lesson).

It correctly rejected the import-error red and added a stub so the test would reach its assertion — but stubbed with
`None`, not a value of the asserted type. It treated the result as its
red ([transcript.md](20260710-171130-test_write_a_failing_test-2a21b0ac/miles-to-km/transcript.md)):

> The test now fails **for the right reason** — an assertion failure where the actual (`None`) doesn't match the
> expected (`1.609344`).

`None` doesn't meaningfully compare to a number, so `assert None == 1.609344` is a type/None artefact, not the value
comparison the next Fake-It step is meant to close.

## Evidence

The critic passed every characteristic except the new one:

| Characteristic                                                            | Status |
|---------------------------------------------------------------------------|--------|
| Production returns a value of the same type as the value the test asserts | FAIL   |

The other eight characteristics (xdd invoked, test-first, literal return, honest assertion red, etc.) PASSED — the
misstep is isolated to the stub's return type. The critic's
reasoning ([critique.md](20260710-171130-test_write_a_failing_test-2a21b0ac/miles-to-km/critique.md)):

> **Critical difference**: workspace `src/conversion.py` returns `None`, while reference returns `0.0`. The test asserts
> against a float (`1.609344`), so `None` is NOT the same type as the asserted value (reference's `0.0` is).

The single run above is representative, not universal. A fresh ten-run baseline under the critic (2026-07-11,
stage-00 guidance) varied the stub:

| Runs | Stub | Strict same-type |
|---|---|---|
| [5](baseline/float-0.0/miles-to-km), 6, 7 | `return 0.0` — float, the asserted type | ✅ |
| [3](baseline/int-0/miles-to-km), 4 | `return 0` — int, a value but not the asserted type | ❌ |
| [1](baseline/none/miles-to-km), 2, 8, 9 | `return None` | ❌ |
| [10](baseline/pass/miles-to-km) | `pass` — a bare stub, implicit `None` | ❌ |

Three runs returned a float (`0.0`), two an int (`0`), four `None`, and one a bare `pass` (implicit `None`). Every
non-float run failed the new same-type characteristic — the one characteristic that cleanly separates the float runs
from the rest (runs 9 and 10 tripped additional characteristics too). Only the three float runs pass strict same-type:
3/10. Per-state tallies in [Experiments](#experiments).

## Review

The agent's instinct was right: a `ModuleNotFoundError` isn't an honest red, so it stubbed to push the failure down to
the assertion (the [honest-red lesson](../20260627-2225-honest-red-fails-on-the-assertion-not-the-import) already drove
that).

Where it stopped short was the *value* it chose. `assert None == 1.609344` fails because `None` is not a number — a type
mismatch — not because one number differs from another, so the assertion isn't yet exercising the comparison the test
exists to make. And it's the wrong red to hand to the next step: Fake-It changes a *value* (`→ 1.609344`), so the red it
works from should already be a value comparison.

The correct step is to stub a value of the **asserted type but not the asserted value** — for the float `1.609344`, a
float placeholder such as `return 0.0`. The red then reads `assert 0.0 == 1.609344`: a real value comparison, of the
right type, teed up for Fake-It to change the value, not the type.

The invariant is that end-state, not the exact placeholder: any value whose type matches the asserted value's and
differs from it (`0.0`, `1.0`, …) is acceptable; `None` or any non-numeric stand-in is not.

## Experiments

Each guidance state is measured with a 10× parallel real-agent run of the scenario, tallying the stub the agent wrote.
`Strict pass` is the runs matching the asserted (float) type — the pass rate for the new characteristic. Each state
links to its exact `SKILL.md` snapshot in [`experiments/`](experiments).

| Guidance state | ✅`0.0` float | ❌`0` int | ❌`None` | ❌`pass` | Strict pass |
|---|---|---|---|---|---|
| [Baseline — no guidance change](experiments/stage-00-baseline-SKILL.md) | 3 | 2 | 4 | 1 | 3/10 |
| [Stage 1 — same-type assertion](experiments/stage-01-same-type-assertion-SKILL.md) | 10 | 0 | 0 | 0 | 10/10 |
| [Stage 2 — same-type when comparing](experiments/stage-02-same-type-when-comparing-SKILL.md) | 10 | 0 | 0 | 0 | 10/10 |

_Winner: **Stage 2** — Stages 1 and 2 both reach 10/10; Stage 2 holds that result while conditioning the rule on value-comparison assertions ("where values are being compared … the returned value must be of the same type"), so it doesn't constrain other assertion shapes. Kept in SKILL.md._

In each of Stages 1 and 2, two of the ten runs failed the *overall* scorecard on a separate test-first-ordering characteristic — not the type axis this table measures.

## Guidance change

`xdd-plugin/skills/xdd/SKILL.md`, under *Failing for the right reason* — a second
condition on what makes a red honest:

> - Where values are being compared in the assertion, the returned value must be of
>   the same type.

Snapshot: [`stage-02-same-type-when-comparing`](experiments/stage-02-same-type-when-comparing-SKILL.md).
[Stage 1](experiments/stage-01-same-type-assertion-SKILL.md) phrased it
unconditionally ("the values being compared … are of the same type") and also
reached 10/10; Stage 2 conditions it on value-comparison assertions so it doesn't
constrain other assertion shapes.
