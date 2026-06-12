from pathlib import Path
from unittest.mock import ANY, MagicMock, call, patch

from hamcrest import assert_that, equal_to

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_session import ClaudeSession
from transcriber import Transcriber

_FAKE_SESSION_ID = "fake-sid"
_ANOTHER_FAKE_SESSION_ID = "another-fake-sid"


class TestClaudeSession:
    @patch("claude_session.uuid.uuid4", return_value=_FAKE_SESSION_ID)
    def test_should_call_the_cli_and_transcriber_and_return_the_cli_result(self, _uuid):
        prompt = "my prompt"
        working_dir = Path("/some_work_dir")
        claude_home = Path("/some/claude_home")
        transcript_path = Path("/output/transcript.md")
        cli_result = "cli result"
        expected_jsonl_path = ClaudeJsonlPath(
            home=claude_home,
            working_dir=working_dir,
            session_id=_FAKE_SESSION_ID,
        )
        claude_spy = MagicMock(spec=ClaudeCli(), return_value=cli_result)
        transcriber_spy = MagicMock(spec=Transcriber())

        result = ClaudeSession(
            claude=claude_spy,
            transcriber=transcriber_spy,
            home=claude_home,
        ).run(
            prompt=prompt,
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        claude_spy.assert_called_once_with(
            prompt=prompt,
            workspace=working_dir,
            session_id=_FAKE_SESSION_ID,
        )
        transcriber_spy.assert_called_once_with(
            jsonl_path=expected_jsonl_path,
            output_path=transcript_path,
        )
        assert_that(result, equal_to(cli_result))

    class TestCallsClaudeCli:
        def test_should_pass_the_prompt(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy, home=dummy,
            ).run(
                prompt="another prompt",
                working_dir=dummy, transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                prompt="another prompt",
                workspace=ANY, session_id=ANY,
            )

        def test_should_pass_the_working_dir(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy, home=dummy,
            ).run(
                working_dir=Path("/another/dir"),
                prompt=dummy, transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                workspace=Path("/another/dir"),
                prompt=ANY, session_id=ANY,
            )

        @patch(
            "claude_session.uuid.uuid4",
            side_effect=[_FAKE_SESSION_ID, _ANOTHER_FAKE_SESSION_ID],
        )
        def test_should_pass_a_unique_session_id_on_each_run(self, _uuid, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())
            session = ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy, home=dummy,
            )

            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)
            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)

            assert_that(claude_cli_spy.call_count, equal_to(2))
            claude_cli_spy.assert_has_calls([
                call(prompt=dummy, workspace=dummy, session_id=_FAKE_SESSION_ID),
                call(prompt=dummy, workspace=dummy, session_id=_ANOTHER_FAKE_SESSION_ID),
            ], any_order=False)

        def test_should_return_the_result(self, dummy):
            claude_cli_stub = MagicMock(spec=ClaudeCli(), return_value="another cli result")

            result = ClaudeSession(
                claude=claude_cli_stub,
                transcriber=dummy, home=dummy,
            ).run(
                prompt=dummy, working_dir=dummy, transcript_path=dummy
            )

            assert_that(result, equal_to("another cli result"))

    class TestCallsTranscriber:
        @patch("claude_session.uuid.uuid4", return_value=_ANOTHER_FAKE_SESSION_ID)
        def test_should_build_the_jsonl_path_from_home_working_dir_and_session_id(self, _uuid, dummy):
            transcriber_spy = MagicMock(spec=Transcriber())
            home = Path("/another/home")
            working_dir = Path("/another/dir")
            expected_jsonl_path = ClaudeJsonlPath(
                home=home, working_dir=working_dir, session_id=_ANOTHER_FAKE_SESSION_ID
            )

            ClaudeSession(
                transcriber=transcriber_spy, home=home,
                claude=dummy,
            ).run(
                working_dir=working_dir,
                prompt=dummy, transcript_path=dummy,
            )

            transcriber_spy.assert_called_once_with(
                jsonl_path=expected_jsonl_path,
                output_path=ANY,
            )

        def test_should_pass_the_transcript_path(self, dummy):
            transcriber_spy = MagicMock(spec=Transcriber())

            ClaudeSession(
                transcriber=transcriber_spy,
                claude=dummy, home=dummy,
            ).run(
                transcript_path=Path("/another/output.md"),
                prompt=dummy, working_dir=dummy,
            )

            transcriber_spy.assert_called_once_with(
                output_path=Path("/another/output.md"),
                jsonl_path=ANY,
            )
