#!/usr/bin/env bash
# SessionStart hook: inject verbatim the docs the agent must apply literally.
# A CLAUDE.md pointer is advisory; injecting the literal text removes the
# read-but-not-applied / applied-as-paraphrase failure mode.
set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

python3 - "$project_dir" <<'PY'
import json
import pathlib
import sys

project_dir = pathlib.Path(sys.argv[1])
docs = [
    (
        "docs/working-practices.md",
        "Below is the project's working practices, injected verbatim from "
        "docs/working-practices.md. Apply it literally — do not rely on a "
        "paraphrase or a remembered summary.",
    ),
]
context = "\n\n".join(
    preamble + "\n\n" + (project_dir / rel).read_text() for rel, preamble in docs
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
PY
