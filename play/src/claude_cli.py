import subprocess
from collections.abc import Callable
from pathlib import Path


class ClaudeCli:
    def __init__(self, runner: Callable = subprocess.run):
        self._runner = runner

    def __call__(
            self, prompt: str, *,
            workspace: Path,
            session_id: str,
            additional_dirs: tuple[Path, ...] = (),
    ) -> str:
        result = _submit_to(
            self._runner,
            prompt,
            workspace,
            session_id,
            additional_dirs,
        )
        _raise_if(
            _is_not_successful(result),
            raising_error=RuntimeError,
            with_message=result.stderr,
        )
        return result.stdout


def _submit_to(
        runner: Callable,
        prompt: str,
        workspace: Path,
        session_id: str,
        additional_dirs: tuple[Path, ...],
) -> subprocess.CompletedProcess:
    return runner(
        _command(
            prompt,
            workspace,
            session_id,
            additional_dirs
        ),
        cwd=workspace,
        capture_output=True,
        text=True
    )


def _command(
        prompt: str,
        workspace: Path,
        session_id: str,
        additional_dirs: tuple[Path, ...]
) -> list[str]:
    cmd = ["claude", "-p", prompt]
    cmd += ["--permission-mode", "acceptEdits"]
    cmd += ["--session-id", session_id]
    for directory in (workspace, *additional_dirs):
        cmd += ["--add-dir", str(directory)]
    return cmd


def _is_not_successful(result: subprocess.CompletedProcess) -> bool:
    return result.returncode != 0


def _raise_if(
        condition: bool, *,
        raising_error: type[Exception],
        with_message: str,
) -> None:
    if condition:
        raise raising_error(with_message)
