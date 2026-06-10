from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import has_item, has_items, is_not
from matchers import matching
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    class TestSucceeds:
        def test_should_submit_the_full_command_and_return_stdout(self, tmp_path):
            subprocess = MagicMock(
                side_effect=StubbedSubprocess(
                    returncode=0, stdout="run complete\n"
                )
            )

            result = ClaudeCli(subprocess=subprocess)(
                "evaluate this",
                workspace=tmp_path,
                session_id="abc-123"
            )

            subprocess.assert_called_once_with(
                ["claude", "--permission-mode", "acceptEdits",
                 "--session-id", "abc-123",
                 "--add-dir", str(tmp_path),
                 "-p", "evaluate this"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )
            assert result == "run complete\n"

        def test_should_return_stdout(self):
            successful = StubbedSubprocess(
                returncode=0, stdout="PASS\n"
            )

            result = ClaudeCli(subprocess=successful)("any prompt")

            assert result == "PASS\n"

    class TestBuildsCommand:
        @pytest.fixture
        def subprocess_that_succeeds(self):
            return MagicMock(side_effect=StubbedSubprocess(returncode=0))

        def test_should_include_the_prompt(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("another prompt")

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_item("another prompt")),
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_include_the_session_id(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)(
                "any prompt", session_id="xyz-789"
            )

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_items("--session-id", "xyz-789")),
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_omit_the_session_id_when_not_provided(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("any prompt")

            subprocess_that_succeeds.assert_called_once_with(
                matching(is_not(has_item("--session-id"))),
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_pass_the_workspace_as_add_dir_and_cwd(self, tmp_path, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)(
                "any prompt",
                workspace=tmp_path
            )

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_items("--add-dir", str(tmp_path))),
                cwd=tmp_path,
                capture_output=ANY, text=ANY,
            )

        def test_should_omit_the_workspace_when_not_provided(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("any prompt")

            subprocess_that_succeeds.assert_called_once_with(
                matching(is_not(has_item("--add-dir"))),
                cwd=None,
                capture_output=ANY, text=ANY,
            )

    class TestErrors:
        def test_should_raise_RuntimeError_when_subprocess_fails(self):
            failing = StubbedSubprocess(
                returncode=1, stderr="something went wrong"
            )

            with pytest.raises(RuntimeError, match="something went wrong"):
                ClaudeCli(subprocess=failing)("any prompt")
