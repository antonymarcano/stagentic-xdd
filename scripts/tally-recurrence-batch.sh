#!/usr/bin/env bash
# Tally a real-agent batch of archived runs: skill-load, full-pass, any-FAIL, a
# per-characteristic failure breakdown, the count for one named characteristic,
# and (optionally) snapshot integrity. Self-contained so a whole tally is one
# allowlisted call — no ad-hoc inline commands needed.
#
# Interim tooling; superseded by the play N× gateway (NEXT.md item 2).
#
# Usage: tally-recurrence-batch.sh [characteristic] [artefacts-dir] [snapshot-marker]
#   characteristic   critic characteristic to count FAILs of
#                    (default: the write-order characteristic)
#   artefacts-dir    dir of archived runs (default: spec/.artefacts)
#   snapshot-marker  optional literal string; counts runs whose transcript
#                    contains it (snapshot-integrity check)
#
# Tallies every run currently in the artefacts dir (cumulative across batches).
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

characteristic="${1:-Transcript shows the failing test was written before the production code}"
artefacts_dir="${2:-$repo_root/spec/.artefacts}"
marker="${3:-}"

skill_char="Transcript shows the agent invoked the xdd skill"
mapfile -t critiques < <(find "$artefacts_dir" -name critique.md 2>/dev/null | sort)

fails=(); disagree=()
crit_loaded=0; grep_loaded=0; marker_present=0
fullpass=0; anyfail=0
declare -A charfail
for c in "${critiques[@]}"; do
  folder="$(basename "$(dirname "$(dirname "$c")")")"
  transcript="$(dirname "$c")/transcript.md"

  # skill-load, checked two independent ways
  cL=0; gL=0
  grep -Fq "\"characteristic\": \"$skill_char\", \"status\": \"PASS\"" "$c" && cL=1
  grep -Fq "Launching skill: stagentic-xdd:xdd" "$transcript" 2>/dev/null && gL=1
  crit_loaded=$((crit_loaded+cL)); grep_loaded=$((grep_loaded+gL))
  [ "$cL" -ne "$gL" ] && disagree+=("$folder (critic=$cL grep=$gL)")

  # snapshot integrity
  if [ -n "$marker" ]; then
    grep -Fq "$marker" "$transcript" 2>/dev/null && marker_present=$((marker_present+1))
  fi

  # named-characteristic FAIL
  grep -Fq "\"characteristic\": \"$characteristic\", \"status\": \"FAIL\"" "$c" && fails+=("$folder")

  # any-FAIL + per-characteristic breakdown
  runfails="$(grep -o '"characteristic": "[^"]*", "status": "FAIL"' "$c" | sed 's/.*characteristic": "//; s/", "status.*//')"
  if [ -z "$runfails" ]; then
    fullpass=$((fullpass+1))
  else
    anyfail=$((anyfail+1))
    while IFS= read -r ch; do
      [ -n "$ch" ] && charfail["$ch"]=$(( ${charfail["$ch"]:-0} + 1 ))
    done <<< "$runfails"
  fi
done

total=${#critiques[@]}
echo "Artefacts dir:  $artefacts_dir"
echo "Evaluable runs: $total"
echo "Skill loaded (critic): $crit_loaded/$total"
echo "Skill loaded (grep):   $grep_loaded/$total"
[ "${#disagree[@]}" -gt 0 ] && { echo "Skill-load DISAGREEMENTS (critic vs grep):"; printf '  %s\n' "${disagree[@]}"; }
[ -n "$marker" ] && echo "Snapshot marker present: $marker_present/$total"
echo "Full-pass (no characteristic failed): $fullpass/$total"
echo "Runs with any FAIL:                   $anyfail/$total"
if [ "$anyfail" -gt 0 ]; then
  echo "Failed characteristics (runs failing each):"
  for ch in "${!charfail[@]}"; do echo "  ${charfail[$ch]}x  $ch"; done
fi
echo "Named characteristic: $characteristic"
echo "  FAIL: ${#fails[@]}"
[ "${#fails[@]}" -gt 0 ] && printf '  %s\n' "${fails[@]}"
