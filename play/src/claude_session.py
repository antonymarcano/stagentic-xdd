import uuid
from pathlib import Path

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_transcriber import ClaudeTranscriber


class ClaudeSession:
    def __init__(
            self, *,
            claude: ClaudeCli,
            transcriber: ClaudeTranscriber,
            home: Path
    ):
        self._call_claude_with = claude
        self._transcribe_using = transcriber
        self._home = home

    def run(
            self, *,
            prompt: str,
            working_dir: Path,
            transcript_path: Path
    ) -> str:
        session_id = _new_session_id()
        result = self._call_claude_with(
            prompt=prompt,
            workspace=working_dir,
            session_id=session_id
        )
        self._transcribe_using(
            jsonl_path=_jsonl_path_for(self._home, working_dir, session_id),
            output_path=transcript_path
        )
        return result


def _new_session_id() -> str:
    return str(uuid.uuid4())


def _jsonl_path_for(
        home: Path,
        working_dir: Path,
        session_id: str
) -> ClaudeJsonlPath:
    return ClaudeJsonlPath(
        home=home,
        working_dir=working_dir,
        session_id=session_id
    )
