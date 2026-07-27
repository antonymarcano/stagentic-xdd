import shutil
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def current_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def is_archivable(*,
                  phase: str,
                  tmp_path: Path | None,
                  artefacts_dir: str | None
                  ) -> bool:
    return (
            phase == "call"
            and tmp_path is not None
            and artefacts_dir is not None
        )


def archive(*,
            tmp_path: Path,
            test_name: str,
            artefacts_dir: str,
            timestamp: str
            ) -> Path:
    at_destination = _destination_for(
        artefacts_dir, test_name, timestamp
    )
    _archive_content_for(tmp_path, at_destination)
    return at_destination


def _destination_for(artefacts_dir: str, test_name: str, timestamp: str) -> Path:
    return Path(artefacts_dir) / f"{timestamp}-{test_name}-{uuid.uuid4().hex[:8]}"


def _archive_content_for(tmp_path: Path, dest: Path):
    shutil.copytree(
        tmp_path,
        dest,
        ignore=_avoiding_copy_tree_race_condition()
    )


def _avoiding_copy_tree_race_condition() -> Callable[[Any, list[str]], set[str]]:
    return shutil.ignore_patterns(
        ".venv",
        "__pycache__",
        ".pytest_cache",
    )
