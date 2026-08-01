#!/usr/bin/env bash
# Validate the current live SKILL.md at scale, single-arm and fail-fast. Runs up
# to B batches of M parallel real-agent runs (no SKILL swapping — whatever is live
# is what's measured), tallying the cumulative artefacts after each batch and
# stopping the moment any run fails any scorecard characteristic.
#
#   Fail-fast   a cumulative full-pass count below the total means a run failed;
#               the ladder stops after that batch and prints the tally.
#   Clean       completing all batches means every run passed its full scorecard.
#
# No SKILL.md swap, no git-clean gate — the working-tree wording is the thing under
# test. Point it at a FRESH artefacts-dir; it appends, so a dirty dir taints the
# tally.
#
# Usage: run-until-fail.sh <artefacts-dir> [batches] [runs] [pytest-node]
#   artefacts-dir  parent folder relative to spec/, e.g. .artefacts/distilled-100
#   batches        max sequential batches (default: 10)
#   runs           parallel runs per batch (default: 10)
#   pytest-node    scenario (default: the whole file => both scenarios)
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

artefacts="${1:?artefacts-dir required, e.g. .artefacts/distilled-100}"
batches="${2:-10}"
runs="${3:-10}"
node="${4:-tests/test_red_green_commit.py}"

tally="$repo_root/scripts/tally-recurrence-batch.sh"
abs="$repo_root/spec/$artefacts"

for b in $(seq -w 1 "$batches"); do
  echo "=== batch $b/$batches ($runs runs) ==="
  bash scripts/run-recurrence-batch.sh "$node" "$runs" "$artefacts/batch-$b"

  out="$(bash "$tally" "" "$abs" 2>/dev/null)"
  fp="$(sed -n 's/^Full-pass.*: \([0-9]*\)\/[0-9]*/\1/p' <<<"$out")"
  tot="$(sed -n 's/^Full-pass.*: [0-9]*\/\([0-9]*\)/\1/p' <<<"$out")"
  echo "--- cumulative full-pass: ${fp:-?}/${tot:-?} ---"

  if [ "${fp:-0}" != "${tot:-0}" ]; then
    echo "=== STOP: a run failed its full scorecard (full-pass ${fp}/${tot}) after batch $b ==="
    bash "$tally" "" "$abs"
    exit 1
  fi
done

echo "=== DONE: ${tot}/${tot} full-pass across $batches batches into $artefacts ==="
bash "$tally" "" "$abs"
