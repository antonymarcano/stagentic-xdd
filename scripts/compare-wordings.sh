#!/usr/bin/env bash
# Compare two wordings of a guidance file over many real-agent runs, alternating
# arm A and arm B wave by wave.
#
# Alternating is the point: run all of A then all of B and any drift in model
# load or latency lands entirely on one arm. Pairing the waves cancels it.
#
# The target file is swapped before each arm's batch and restored on ANY exit,
# so an interrupted run does not leave a snapshot in the working tree.
#
# Usage: compare-wordings.sh <artefacts-dir> <fileA> <labelA> <fileB> <labelB> [waves] [runs]
#   artefacts-dir  parent folder relative to spec/, e.g. .artefacts/my-experiment.
#                  Point at a FRESH dir; runs accumulate.
#   fileA/labelA   snapshot and label for arm A (by convention the baseline)
#   fileB/labelB   snapshot and label for arm B (the candidate)
#   waves          paired waves (default: 10)
#   runs           parallel runs per arm per wave (default: 10)
#
# Environment:
#   NODE             pytest node (default: the whole red-green-commit file)
#   TARGET           file the snapshots are copied over
#                    (default: xdd-plugin/skills/xdd/SKILL.md)
#   STOP_ON_A_FAIL   set to 1 when arm A is a known-clean control: any failure
#                    in it means the window is contaminated, so stop. Leave
#                    unset when arm A is a baseline expected to fail sometimes.
#
# Exit: 0 completed; 1 stopped on arm-A contamination; 2 an arm produced nothing
#       to evaluate.
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

artefacts="${1:?artefacts-dir required, e.g. .artefacts/my-experiment}"
fileA="${2:?fileA snapshot path required}"; labelA="${3:?labelA required}"
fileB="${4:?fileB snapshot path required}"; labelB="${5:?labelB required}"
waves="${6:-10}"
runs="${7:-10}"

node="${NODE:-tests/test_red_green_commit.py}"
target="${TARGET:-xdd-plugin/skills/xdd/SKILL.md}"
stop_on_a_fail="${STOP_ON_A_FAIL:-0}"

tally="$repo_root/scripts/tally.sh"
absA="$repo_root/spec/$artefacts/$labelA"
absB="$repo_root/spec/$artefacts/$labelB"

for f in "$fileA" "$fileB" "$target"; do
  [ -f "$f" ] || { echo "[compare] ABORT: no such file: $f"; exit 2; }
done
if diff -q "$fileA" "$fileB" >/dev/null; then
  echo "[compare] ABORT: the two snapshots are identical — nothing to compare"; exit 2
fi

# Restore whatever the target was before we started, on any exit.
original="$(mktemp)"
cp "$target" "$original"
trap 'cp "$original" "$target"; rm -f "$original"; echo "[compare] restored $target"' EXIT

run_arm() {  # $1 label  $2 snapshot  $3 wave
  cp "$2" "$target"
  echo "=== [$1] wave $3/$waves ($runs runs; $target swapped) ==="
  bash scripts/run-batch.sh "$node" "$runs" "$artefacts/$1"
}

cumulative() {  # $1 abs-dir -> sets tally_full_pass ("<full-pass>/<total>") and tally_status
  local out; out="$(bash "$tally" "" "$1" 2>/dev/null)"; tally_status=$?
  tally_full_pass="$(sed -n 's/^Full-pass.*: \([0-9]*\/[0-9]*\)/\1/p' <<<"$out")"
}

for w in $(seq -w 1 "$waves"); do
  run_arm "$labelA" "$fileA" "$w"
  run_arm "$labelB" "$fileB" "$w"

  cumulative "$absA"; a="$tally_full_pass"; a_status=$tally_status
  cumulative "$absB"; b="$tally_full_pass"; b_status=$tally_status
  echo "--- after wave $w — $labelA: ${a:-?} full-pass, $labelB: ${b:-?} full-pass"

  if [ "$stop_on_a_fail" = "1" ] && [ "$a_status" -ne 0 ]; then
    echo "=== STOP: $labelA is the control and is no longer clean — window contaminated ==="
    echo "--- $labelA ---"; bash "$tally" "" "$absA"
    echo "--- $labelB ---"; bash "$tally" "" "$absB"
    exit 1
  fi
done

echo "=== $waves waves complete: $labelA vs $labelB into $artefacts ==="
echo "--- $labelA ---"; bash "$tally" "" "$absA"; a_status=$?
echo "--- $labelB ---"; bash "$tally" "" "$absB"; b_status=$?
echo "Compare the two rates for significance with scripts/fisher.sh"
if [ "$a_status" -eq 2 ] || [ "$b_status" -eq 2 ]; then exit 2; fi
exit 0
