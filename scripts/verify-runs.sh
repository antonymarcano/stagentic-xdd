#!/usr/bin/env bash
# Verify a spec scenario over many real-agent runs, single-arm: whatever is live
# in the working tree is what is measured (no file swapping). Runs B batches of
# M parallel runs, tallying the cumulative artefacts after each batch.
#
# Two modes:
#   --stop-on-fail   halt at the end of the first batch containing a failed run
#                    — a gate, for confirming a wording holds.
#   (default)        run all B batches whatever happens — a measurement, for
#                    establishing a failure rate.
#
# Usage: verify-runs.sh [--stop-on-fail] <artefacts-dir> [batches] [runs] [pytest-node]
#   artefacts-dir  parent folder relative to spec/, e.g. .artefacts/my-check.
#                  Point at a FRESH dir; runs accumulate, so a dirty dir taints
#                  the tally.
#   batches        sequential batches (default: 10)
#   runs           parallel runs per batch (default: 10)
#   pytest-node    scenario (default: the whole red-green-commit file, i.e. both
#                  scenarios)
#
# Exit: mirrors tally.sh — 0 every run clean; 1 a run failed; 2 nothing to
#       evaluate.
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

stop_on_fail=0
if [ "${1:-}" = "--stop-on-fail" ]; then stop_on_fail=1; shift; fi

artefacts="${1:?artefacts-dir required, e.g. .artefacts/my-check}"
batches="${2:-10}"
runs="${3:-10}"
node="${4:-tests/test_red_green_commit.py}"

tally="$repo_root/scripts/tally.sh"
abs="$repo_root/spec/$artefacts"

for b in $(seq -w 1 "$batches"); do
  echo "=== batch $b/$batches ($runs runs) ==="
  bash scripts/run-batch.sh "$node" "$runs" "$artefacts/batch-$b"

  out="$(bash "$tally" "" "$abs" 2>/dev/null)"; status=$?
  grep '^Full-pass' <<<"$out" | sed 's/^/--- cumulative /'

  if [ "$stop_on_fail" -eq 1 ] && [ "$status" -ne 0 ]; then
    echo "=== STOP: tally is not clean after batch $b ==="
    bash "$tally" "" "$abs"
    exit "$status"
  fi
done

echo "=== all $batches batches run into $artefacts ==="
bash "$tally" "" "$abs"
