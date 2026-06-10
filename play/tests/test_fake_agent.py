import subprocess

import pytest
from hamcrest import assert_that, equal_to

from fake_agent import FakeAgent
from result import Success

_TASK_NAME = "my-task"


class TestFakeAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def working_dir(self, tmp_path):
        path = tmp_path / "workspace"
        path.mkdir()
        return path

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(script, name=_TASK_NAME):
            task = tasks_root / name
            task.mkdir()
            (task / "fake-task.sh").write_text(script)
        return make

    def test_should_run_the_task_script_and_make_the_transcript_available(self, tasks_root, working_dir, create_test_task_with):
        sentinel_file = "sentinel.txt"
        create_test_task_with(script=f"touch {sentinel_file}\n", name=_TASK_NAME)

        agent = FakeAgent(tasks_root=tasks_root)
        result = agent.perform(
            task=_TASK_NAME,
            working_dir=working_dir,
        )

        assert_that(
            (working_dir / sentinel_file).exists(), equal_to(True)
        )
        assert_that(
            result, equal_to(Success(working_dir / "transcript.md"))
        )

    class TestRunsScript:
        def test_should_run_the_named_task(self, tasks_root, working_dir, create_test_task_with):
            task_name = "another-task"
            sentinel_file = "sentinel.txt"
            create_test_task_with(script=f"touch {sentinel_file}\n", name=task_name)

            FakeAgent(tasks_root=tasks_root).perform(
                task=task_name, working_dir=working_dir,
            )

            assert_that(
                (working_dir / sentinel_file).exists(), equal_to(True)
            )

    class TestReturnsTranscript:
        def test_should_be_wrapped_in_success(self, tasks_root, working_dir, create_test_task_with):
            create_test_task_with(script="true\n")

            agent = FakeAgent(tasks_root=tasks_root)
            result = agent.perform(task=_TASK_NAME, working_dir=working_dir)

            assert_that(result, equal_to(Success(working_dir / "transcript.md")))

    class TestErrors:
        def test_should_raise_when_the_task_script_fails(self, tasks_root, working_dir, create_test_task_with):
            create_test_task_with(script="exit 1\n")

            agent = FakeAgent(tasks_root=tasks_root)

            with pytest.raises(subprocess.CalledProcessError):
                agent.perform(task=_TASK_NAME, working_dir=working_dir)
