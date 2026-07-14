#!/usr/bin/env bash
# Run the current live SKILL.md through B batches of M parallel real-agent runs,
# all archived under one artefacts folder. For retesting a single wording at
# scale, unattended (no SKILL swapping — whatever is live is what's measured).
# Superseded by the play N× gateway (NEXT.md item 2).
#
# Usage: run-repeated-batches.sh <artefacts-dir> [batches] [runs] [pytest-node]
#   artefacts-dir  parent folder relative to spec/, e.g. .artefacts/experiment/my-run
#   batches        number of sequential batches (default: 10)
#   runs           parallel runs per batch (default: 10)
#   pytest-node    scenario (default: the write-order scenario)
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

artefacts="${1:?artefacts-dir required, e.g. .artefacts/experiment/my-run}"
batches="${2:-10}"
runs="${3:-10}"
node="${4:-tests/test_red_green_commit.py::TestRedGreenCommit::test_write_a_failing_test}"

for b in $(seq -w 1 "$batches"); do
  echo "=== batch $b/$batches ==="
  bash scripts/run-recurrence-batch.sh "$node" "$runs" "$artefacts/batch-$b"
done

echo "=== done: $((batches*runs)) runs into $artefacts ==="
