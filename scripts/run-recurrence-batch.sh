#!/usr/bin/env bash
# Run a spec scenario N× in parallel against the real agent, preserving each
# run's artefacts in spec/.artefacts.
#
# Interim tooling for measuring how often a lesson's misstep recurs; superseded
# by the play N× gateway (NEXT.md item 2).
#
# Usage: run-recurrence-batch.sh [pytest-node] [count] [artefacts-dir]
#   pytest-node    scenario to run (default: the write-order scenario)
#   count          number of parallel runs (default: 10)
#   artefacts-dir  where runs are archived, relative to spec/ — name a subfolder
#                  per batch to keep them separate, e.g. .artefacts/my-batch
#                  (default: .artefacts)
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

node="${1:-tests/test_red_green_commit.py::TestRedGreenCommit::test_write_a_failing_test}"
count="${2:-10}"
artefacts="${3:-.artefacts}"

echo "Running ${count}× real-agent into ${artefacts}: ${node}"

# Stagger launches by 100ms — the shortest stagger that avoids the archive
# copytree race under parallel runs (100ms clean at 30 runs; 50ms flakes ~2/30).
for _ in $(seq "$count"); do
  uv run --directory spec pytest "$node" --agent=real --.artefacts-dir "$artefacts" -n0 &
  sleep 0.1
done
wait
