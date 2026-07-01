from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import assert_that, equal_to, has_item, has_items
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
            prompt = "evaluate this"

            result = ClaudeCli(runner=subprocess)(
                prompt,
                workspace=tmp_path,
                session_id="abc-123"
            )

            subprocess.assert_called_once_with(
                ["claude", "-p", prompt,
                 "--permission-mode", "acceptEdits",
                 "--session-id", "abc-123",
                 "--add-dir", str(tmp_path)],
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )
            assert_that(result, equal_to("run complete\n"))

        def test_should_return_stdout(self, tmp_path):
            successful = StubbedSubprocess(
                returncode=0, stdout="PASS\n"
            )

            result = ClaudeCli(runner=successful)(
                "any prompt",
                workspace=tmp_path,
                session_id="any session id"
            )

            assert_that(result, equal_to("PASS\n"))

    class TestBuildsCommand:
        @pytest.fixture
        def subprocess_that_succeeds(self):
            return MagicMock(side_effect=StubbedSubprocess(returncode=0))

        def test_should_include_the_prompt(self, tmp_path, subprocess_that_succeeds):
            prompt = "another prompt"

            ClaudeCli(runner=subprocess_that_succeeds)(
                prompt,
                workspace=tmp_path,
                session_id="any session id"
            )

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_item(prompt)),
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_include_the_session_id(self, tmp_path, subprocess_that_succeeds):
            ClaudeCli(runner=subprocess_that_succeeds)(
                "any prompt", session_id="xyz-789", workspace=tmp_path
            )

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_items("--session-id", "xyz-789")),
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_pass_the_workspace_as_add_dir_and_cwd(self, tmp_path, subprocess_that_succeeds):
            ClaudeCli(runner=subprocess_that_succeeds)(
                "any prompt",
                workspace=tmp_path,
                session_id="any session id"
            )

            subprocess_that_succeeds.assert_called_once_with(
                matching(has_items("--add-dir", str(tmp_path))),
                cwd=tmp_path,
                capture_output=ANY, text=ANY,
            )

        def test_should_add_the_additional_dir(self, tmp_path, subprocess_that_succeeds):
            scene = tmp_path / "scene"

            ClaudeCli(runner=subprocess_that_succeeds)(
                "any prompt",
                additional_dirs=(scene,),
                workspace=tmp_path,
                session_id="any session id",
            )

            subprocess_that_succeeds.assert_called_once_with(
                ["claude", "-p", "any prompt",
                 "--permission-mode", "acceptEdits",
                 "--session-id", "any session id",
                 "--add-dir", str(tmp_path),
                 "--add-dir", str(scene)],
                cwd=ANY, capture_output=ANY, text=ANY,
            )

        def test_should_add_the_plugin_dir(self, tmp_path, subprocess_that_succeeds):
            plugin = tmp_path / "plugin"

            ClaudeCli(runner=subprocess_that_succeeds, plugin_dir=plugin)(
                "any prompt",
                workspace=tmp_path,
                session_id="any session id",
            )

            subprocess_that_succeeds.assert_called_once_with(
                ["claude", "-p", "any prompt",
                 "--permission-mode", "acceptEdits",
                 "--session-id", "any session id",
                 "--add-dir", str(tmp_path),
                 "--plugin-dir", str(plugin)],
                cwd=ANY, capture_output=ANY, text=ANY,
            )

    class TestErrors:
        # noinspection PyArgumentList
        # - because we're protecting against changes that make it optional.
        def test_should_require_a_workspace(self, dummy):
            with pytest.raises(TypeError):
                ClaudeCli(runner=dummy)("any prompt", session_id="xyz-789")

        # noinspection PyArgumentList
        # - because we're protecting against changes that make it optional.
        def test_should_require_a_session_id(self, tmp_path, dummy):
            with pytest.raises(TypeError):
                ClaudeCli(runner=dummy)("any prompt", workspace=tmp_path)

        def test_should_raise_RuntimeError_when_subprocess_fails(self, tmp_path):
            failing = StubbedSubprocess(
                returncode=1, stderr="something went wrong"
            )

            with pytest.raises(RuntimeError, match="something went wrong"):
                ClaudeCli(runner=failing)(
                    "any prompt", workspace=tmp_path, session_id="any session id"
                )
