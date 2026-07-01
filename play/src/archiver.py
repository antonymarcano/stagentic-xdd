import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path


def current_timestamp():
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def archive(*, phase, tmp_path, test_name, artefacts_dir, timestamp):
    if phase != "call" or artefacts_dir is None or tmp_path is None:
        return
    dest = Path(artefacts_dir) / f"{timestamp}-{test_name}-{uuid.uuid4().hex[:8]}"
    shutil.copytree(tmp_path, dest)
    return dest
