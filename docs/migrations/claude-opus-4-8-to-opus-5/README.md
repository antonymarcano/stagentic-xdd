# claude-opus-4-8 → claude-opus-5

Each line in the xdd skill was driven in by a failure on a previous model.
Which misunderstandings a model holds is a property of that model, so moving the
pinned model version re-opens every wording decision the skill carries.

These are the experiments that re-established the minimal XDD skill for claude-opus-5.

| | |
|---|---|
| From | `claude-opus-4-8` |
| To | `claude-opus-5` |
| Measured on | CLI 2.1.220 |
| Date | August 2026 |

Every run covers both scenarios in `spec/tests/test_red_green_commit.py`, so one
run produces two critiques. Each folder keeps the `SKILL.md` snapshots its arms
measured, so a result can be re-run from the file that produced it.

## The experiments, in the order they were run

### 1. [Motivation ablation](20260802-motivation-ablation/RESULT.md)

*Does removing the skill's identity, goal and consequence still make the agent
worse?*

No. On claude-opus-4-8 their removal cost about one run in twenty; on
claude-opus-5 both arms passed 400 of 400 critiques. The motivation came out.

### 2. [Placeholder floor](20260802-placeholder-floor/RESULT.md)

*Does the scenario still fail when the skill says nothing useful?*

Yes — a body of *"Apply Test-Driven Development."* fails 10 of 20 critiques, and a
body of identity and goal only fails at the same rate on the same characteristics.

### 3. [Line ablation](20260802-line-ablation/RESULT.md)

*Which lines does claude-opus-5 still need?*

Three of seven lines result in the agent:
- making production code fail for the right reason,
- making that failure a type-matched comparison, and
- passing the test by faking it.

The reduced file passes 400 of 400 critiques across 200 runs, matching the
outgoing skill at the same sample size. The design of the search is in
[its README](20260802-line-ablation/README.md).
