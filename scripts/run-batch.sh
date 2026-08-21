#!/usr/bin/env bash
# Run a spec scenario N× in parallel against the real agent, preserving each
# run's artefacts in spec/.artefacts.
#
# The primitive the other runners are built from; usable directly for a one-off
# batch. It launches and archives — it does not tally. Read the result with
# tally.sh, or use verify-runs.sh to do both.
#
# Usage: run-batch.sh [pytest-node] [count] [artefacts-dir]
#   pytest-node    scenario to run (default: the whole red-green-commit file,
#                  i.e. both scenarios)
#   count          number of parallel runs (default: 10)
#   artefacts-dir  where runs are archived, relative to spec/ — name a subfolder
#                  per batch to keep them separate, e.g. .artefacts/my-batch
#                  (default: .artefacts)
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

node="${1:-tests/test_red_green_commit.py}"
count="${2:-10}"
artefacts="${3:-.artefacts}"

echo "Running ${count}× real-agent into ${artefacts}: ${node}"

for _ in $(seq "$count"); do
  uv run --directory spec pytest "$node" --agent=real --.artefacts-dir "$artefacts" -n0 &
done
wait
