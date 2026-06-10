from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import assert_that, equal_to

from agent import Agent
from claude_session import ClaudeSession
from result import Success

_TASK_NAME = "my-task"


class TestAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(prompt="do the thing", name=_TASK_NAME):
            task = tasks_root / name
            task.mkdir()
            (task / "TASK.md").write_text(prompt)
        return make

    @pytest.fixture
    def session_spy(self):
        return MagicMock(spec=ClaudeSession)

    def test_should_call_claude_session_and_make_transcript_available(self, tasks_root, create_test_task_with, session_spy):
        task_prompt = "do the thing"
        working_dir = Path("/work")
        transcript_path = working_dir / "transcript.md"
        create_test_task_with(prompt=task_prompt, name=_TASK_NAME)

        agent = Agent(
            tasks_root=tasks_root,
            session=session_spy,
        )
        result = agent.perform(
            task=_TASK_NAME,
            working_dir=working_dir,
        )

        session_spy.run.assert_called_once_with(
            prompt=task_prompt,
            working_dir=working_dir,
            transcript_path=transcript_path,
        )
        assert_that(
            result, equal_to(Success(transcript_path))
        )

    class TestCallsSession:
        def test_prompt_should_be_read_from_the_named_task(self, tasks_root, create_test_task_with, dummy, session_spy):
            task_name = "another-task"
            task_prompt = "the prompt"
            create_test_task_with(prompt=task_prompt, name=task_name)

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                task=task_name,
                working_dir=dummy,
            )

            session_spy.run.assert_called_once_with(
                prompt=task_prompt,
                working_dir=ANY, transcript_path=ANY,
            )

        def test_working_dir_should_be_passed_to_session(self, tasks_root, create_test_task_with, session_spy):
            create_test_task_with("dummy prompt")

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                working_dir=Path("/other/dir"),
                task=_TASK_NAME,
            )

            session_spy.run.assert_called_once_with(
                working_dir=Path("/other/dir"),
                prompt=ANY, transcript_path=ANY,
            )

        def test_transcript_path_should_be_inside_working_dir(self, tasks_root, create_test_task_with, session_spy):
            create_test_task_with("dummy prompt")

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                working_dir=Path("/other/dir"),
                task=_TASK_NAME,
            )

            session_spy.run.assert_called_once_with(
                transcript_path=Path("/other/dir") / "transcript.md",
                prompt=ANY, working_dir=ANY,
            )

    class TestReturnsTranscript:
        def test_transcript_should_be_returned_wrapped_in_success(self, tasks_root, create_test_task_with, session_spy):
            create_test_task_with("dummy prompt")
            working_dir = Path("/other/dir")

            agent = Agent(
                tasks_root=tasks_root,
                session=session_spy,
            )

            result = agent.perform(
                working_dir=working_dir,
                task=_TASK_NAME,
            )

            assert_that(
                result, equal_to(Success(working_dir / "transcript.md"))
            )
