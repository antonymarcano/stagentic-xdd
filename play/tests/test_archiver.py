import re
from datetime import UTC
from unittest.mock import patch

import pytest
from stagentic.test.cases import case

from archiver import archive, current_timestamp, is_archivable


class TestArchiver:
    def test_current_timestamp_format(self):
        assert re.fullmatch(r"\d{8}-\d{6}", current_timestamp())

    def test_current_timestamp_is_in_utc(self):
        with patch("archiver.datetime") as mock_datetime:
            current_timestamp()
        mock_datetime.now.assert_called_once_with(UTC)

    def test_archive_copies_workspace_to_timestamped_folder(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("some content")
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert (dest / "transcript.md").read_text() == "some content"

    @pytest.mark.parametrize("transient", [
        case("venv", transient=".venv"),
        case("pycache", transient="__pycache__"),
        case("pytest-cache", transient=".pytest_cache"),
    ])
    def test_should_exclude_transient_dirs_from_the_archive(self, tmp_path, transient):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("keep me")
        (workspace / transient).mkdir()
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo",
                       artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert (dest / "transcript.md").exists()
        assert not (dest / transient).exists()

    def test_archive_returns_the_destination_it_wrote(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("some content")
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert dest.parent == artefacts_dir
        assert dest.name.startswith("20260527-101638-test_foo")

    def test_should_use_a_short_uuid_suffix(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo",
                       artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        suffix = dest.name.rsplit("-", 1)[-1]
        assert re.fullmatch(r"[0-9a-f]{8}", suffix)

    def test_archive_does_not_collide_for_same_timestamp_and_test_name(self, tmp_path):
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        def workspace_named(name):
            ws = tmp_path / name
            ws.mkdir()
            (ws / "transcript.md").write_text(name)
            return ws

        first = archive(tmp_path=workspace_named("run-a"), test_name="test_foo",
                        artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")
        second = archive(tmp_path=workspace_named("run-b"), test_name="test_foo",
                         artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert first != second
        assert first.exists() and second.exists()


class TestIsArchivable:
    def test_should_say_is_archivable_when_in_test_run_call_phase_with_a_workspace_and_an_artefacts_dir(self, tmp_path):
        should_archive = is_archivable(
            phase="call", tmp_path=tmp_path, artefacts_dir=str(tmp_path)
        )
        assert should_archive is True

    def test_should_say_is_not_archivable_when_outside_test_run_call_phase(self, tmp_path):
        should_archive = is_archivable(
            phase="setup", tmp_path=tmp_path, artefacts_dir=str(tmp_path)
        )
        assert should_archive is False

    def test_should_say_is_not_archivable_without_a_workspace(self):
        should_archive = is_archivable(
            phase="call", tmp_path=None, artefacts_dir="/tmp/artefacts"
        )
        assert should_archive is False

    def test_should_say_is_not_archivable_without_an_artefacts_dir(self, tmp_path):
        should_archive = is_archivable(
            phase="call", tmp_path=tmp_path, artefacts_dir=None
        )
        assert should_archive is False
