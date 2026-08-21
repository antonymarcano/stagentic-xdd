# Placeholder floor — result

**Question:** on claude-opus-5, does the scenario still fail when the xdd skill
says nothing useful?

**Answer:** yes, badly. Half the critiques failed in the first ten runs.

## What was run

`SKILL-placeholder.md` copied over `xdd-plugin/skills/xdd/SKILL.md`. It keeps
the frontmatter, so the skill still loads, and replaces the whole body with one
line:

```markdown
Apply Test-Driven Development.
```

- `scripts/verify-runs.sh --stop-on-fail`, set to four batches of ten runs.
- It stopped after batch 1, as designed — the first failing batch halts the run.
- Each run does both scenarios in `spec/tests/test_red_green_commit.py`, so ten
  runs gave twenty critiques.

| | |
|---|---|
| Date | 2026-08-02 |
| CLI | claude 2.1.220 |
| Model | claude-opus-5 |
| Runs | 10 |
| Critiques | 20 |
| Artefacts | `spec/.artefacts/20260802-placeholder-floor/` |

## Result

Two floors were measured, ten runs each. Both keep the frontmatter so the skill
still loads; both replace the body with something that carries no technique.

| body | critiques | passed | failed | skill loaded |
|---|---|---|---|---|
| [*"Apply Test-Driven Development."*](SKILL-placeholder.md) | 20 | 10 | 10 | 20/20 |
| [identity and goal only](SKILL-motivation-only.md) | 20 | 10 | 10 | 20/20 |

Failures by characteristic:

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
instruction.** The two floors fail the same characteristics at the same rates.

## What the numbers say

- **The gap is wide.** The committed skill passes 400 out of 400 critiques; the
  placeholder passes 10 out of 20. A wording that makes things worse will show up
  as failures.
- **Test-first is not free on this model.** Write-order failed 5 times in 20, so
  claude-opus-5 does not hold test-first order unaided.
- **The heaviest failures are elsewhere.** Fake-It and failing-for-the-right-
  reason each failed 10 in 20 — more than write-order.

## Which guidance each failure points to

| failed characteristic | section that addresses it |
|---|---|
| Same type as the asserted value | *Failing for the Right Reason* — the type clause |
| Fails comparing a return value, not a missing module | *Failing for the Right Reason* — the assertion clause, and step 2 |
| Production module exists with content, imported by the test | step 2 — change production code so it fails for the right reason |
| Returns a literal, not a formula | *Making a Test Pass* — Fake-It |
| Workspace equivalent to the Reference Scene | *Making a Test Pass* — Fake-It |
| Transcript shows a FAILED pytest result | step 3 — then run the test |
| Failing test written before production code | step 1 — test first, don't run it yet |

Every section of the committed body has a matching failure. The only content
without one is the framing above the first section:

```markdown
# Model Corrections

Your model has some misunderstandings of TDD, which you should override with the following:
```

## Limits

- **One batch, not a rate.** Twenty critiques stopped at the first failure. The
  counts show the failures are common and repeatable, not how common.
- **This shows coverage, not necessity.** A section having a matching failure
  does not mean it is the section fixing it. Fake-It alone might fix the type
  and module-content rows without *Failing for the Right Reason*.

## What to do next

- **Leave-one-out.** Remove one section at a time from the committed skill and
  measure each against this scenario. That answers which sections are individually
  necessary, which this run cannot.
- **The framing lines are the one cut this data supports** — no observed failure
  needs them.
