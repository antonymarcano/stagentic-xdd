from datetime import UTC
from unittest.mock import patch

import pytest
from hamcrest import assert_that, equal_to, is_, is_not, matches_regexp, starts_with
from stagentic.test.cases import case

from archiver import archive, current_timestamp, is_archivable


class TestCurrentTimestamp:
    def test_should_be_formatted_as_a_date_and_time(self):
        assert_that(current_timestamp(), matches_regexp(r"^\d{8}-\d{6}$"))

    def test_should_be_in_utc(self):
        with patch("archiver.datetime") as mock_datetime:
            current_timestamp()
        mock_datetime.now.assert_called_once_with(UTC)


class TestArchive:
    def test_should_copy_the_workspace_to_a_timestamped_folder(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("some content")
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert_that((dest / "transcript.md").read_text(), equal_to("some content"))

    @pytest.mark.parametrize("transient", [
        case("venv", transient=".venv"),
        case("pycache", transient="__pycache__"),
        case("pytest-cache", transient=".pytest_cache"),
    ])
    def test_should_exclude_transient_dirs(self, tmp_path, transient):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("keep me")
        (workspace / transient).mkdir()
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo",
                       artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert_that((dest / "transcript.md").exists(), is_(True))
        assert_that((dest / transient).exists(), is_(False))

    def test_should_return_the_destination_it_wrote(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("some content")
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        assert_that(dest.parent, equal_to(artefacts_dir))
        assert_that(dest.name, starts_with("20260527-101638-test_foo"))

    def test_should_use_a_short_uuid_suffix(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        artefacts_dir = tmp_path / ".artefacts"
        artefacts_dir.mkdir()

        dest = archive(tmp_path=workspace, test_name="test_foo",
                       artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        suffix = dest.name.rsplit("-", 1)[-1]
        assert_that(suffix, matches_regexp(r"^[0-9a-f]{8}$"))

    def test_should_not_collide_for_the_same_timestamp_and_test_name(self, tmp_path):
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

        assert_that(first, is_not(equal_to(second)))
        assert_that(first.exists(), is_(True))
        assert_that(second.exists(), is_(True))


class TestIsArchivable:
    def test_should_say_is_archivable_when_in_test_run_call_phase_with_a_workspace_and_an_artefacts_dir(self, tmp_path):
        should_archive = is_archivable(
            phase="call", tmp_path=tmp_path, artefacts_dir=str(tmp_path)
        )
        assert_that(should_archive, is_(True))

    def test_should_say_is_not_archivable_when_outside_test_run_call_phase(self, tmp_path):
        should_archive = is_archivable(
            phase="setup", tmp_path=tmp_path, artefacts_dir=str(tmp_path)
        )
        assert_that(should_archive, is_(False))

    def test_should_say_is_not_archivable_without_a_workspace(self):
        should_archive = is_archivable(
            phase="call", tmp_path=None, artefacts_dir="/tmp/artefacts"
        )
        assert_that(should_archive, is_(False))

    def test_should_say_is_not_archivable_without_an_artefacts_dir(self, tmp_path):
        should_archive = is_archivable(
            phase="call", tmp_path=tmp_path, artefacts_dir=None
        )
        assert_that(should_archive, is_(False))
