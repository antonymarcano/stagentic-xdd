#!/usr/bin/env bash
# Alternating A/B experiment between two xdd SKILL wordings.
#
# Runs N batches of each wording, alternating (A, B, A, B, …), swapping the live
# SKILL.md before each batch so every run in a batch loads the intended wording.
# Alternating removes the time/load confound between the two wordings.
# Self-contained so it runs unattended with no per-command permission prompts.
# The live SKILL.md is restored on exit.
#
# Usage:
#   run-alternating-experiment.sh <experiment> <refA> <nameA> <refB> <nameB> [batches-each] [runs-per-batch]
#     experiment      subfolder under .artefacts/experiment (e.g. stub-vs-runfix)
#     refA / nameA    snapshot file and label for wording A
#     refB / nameB    snapshot file and label for wording B
#     batches-each    batches of EACH wording (default: 10)
#     runs-per-batch  parallel runs per batch (default: 10)
#
# Artefacts:
#   spec/.artefacts/experiment/<experiment>/<nameA>/batch-NN
#   spec/.artefacts/experiment/<experiment>/<nameB>/batch-NN
# Tally each wording by pointing tally-recurrence-batch.sh at its folder.
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

experiment="${1:?experiment name required, e.g. stub-vs-runfix}"
refA="${2:?refA snapshot path required}"; nameA="${3:?nameA label required}"
refB="${4:?refB snapshot path required}"; nameB="${5:?nameB label required}"
batches="${6:-10}"
runs="${7:-10}"

live_skill="xdd-plugin/skills/xdd/SKILL.md"
node="tests/test_red_green_commit.py::TestRedGreenCommit::test_write_a_failing_test"

# Restore whatever the live SKILL.md was before we started, on any exit.
orig_skill="$(mktemp)"
cp "$live_skill" "$orig_skill"
trap 'cp "$orig_skill" "$live_skill"; rm -f "$orig_skill"' EXIT

run_batch() {  # $1 wording-name  $2 ref-file  $3 batch-number
  local name="$1" ref="$2" n="$3"
  cp "$ref" "$live_skill"
  echo "=== [$name] batch $n/$batches (SKILL swapped) ==="
  bash scripts/run-recurrence-batch.sh "$node" "$runs" ".artefacts/experiment/$experiment/$name/batch-$n"
}

for i in $(seq -w 1 "$batches"); do
  run_batch "$nameA" "$refA" "$i"
  run_batch "$nameB" "$refB" "$i"
done

echo "=== experiment '$experiment' complete: $((batches*runs)) $nameA + $((batches*runs)) $nameB runs ==="
