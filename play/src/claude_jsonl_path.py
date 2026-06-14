from pathlib import Path


class ClaudeJsonlPath(Path):
    def __init__(self, *, home, working_dir, session_id):
        super().__init__(
            home, ".claude", "projects", _claude_encoded(working_dir), f"{session_id}.jsonl"
        )


def _claude_encoded(path):
    return str(path).replace("/", "-").replace("_", "-")
