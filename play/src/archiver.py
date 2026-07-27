import shutil
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def current_timestamp():
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def should_archive(*, phase: str, tmp_path: Path | None, artefacts_dir: str | None) -> bool:
    return phase == "call"


def archive(*, phase, tmp_path, test_name, artefacts_dir, timestamp):
    if phase != "call" or artefacts_dir is None or tmp_path is None:
        return None
    dest = Path(artefacts_dir) / f"{timestamp}-{test_name}-{uuid.uuid4().hex[:8]}"
    shutil.copytree(tmp_path, dest, ignore=_avoiding_copy_tree_race_condition())
    return dest


def _avoiding_copy_tree_race_condition() -> Callable[[Any, list[str]], set[str]]:
    return shutil.ignore_patterns(
        ".venv",
        "__pycache__",
        ".pytest_cache"
    )
