from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import all_of, assert_that, contains_string, equal_to
from matchers import matching

from claude_session import ClaudeSession
from critic import Critic
from result import Failure, Success
from scorecard_results import ScorecardResults


class TestCritic:
    @pytest.fixture
    def working_dir(self): return Path("/workspace/coding_exercise")

    @pytest.fixture
    def evidence_source(self, working_dir): return working_dir / "transcript.md"

    @pytest.fixture
    def one_characteristic_scorecard(self): return [{"characteristic": "any", "failure": "n/a"}]

    @pytest.fixture
    def task_to_evaluate(self): return Path("/workspace/tasks/3-some-task")

    @pytest.fixture
    def session_that_passes(self):
        session = MagicMock(spec=ClaudeSession)
        session.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'
        return session

    class TestFails:
        def test_should_call_session_and_return_a_failure_for_failed_characteristics(self, evidence_source, working_dir, task_to_evaluate):
            session_that_fails = MagicMock(spec=ClaudeSession)
            session_that_fails.run.return_value = '[{"characteristic": "alpha", "status": "FAIL"}]'

            result = Critic(session=session_that_fails).evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir,
                evidence_source=evidence_source,
                should=[{"characteristic": "alpha", "failure": "alpha reason"}],
            )

            session_that_fails.run.assert_called_once_with(
                prompt=matching(all_of(
                    contains_string(f"Transcript: {evidence_source}\n"),
                    contains_string(f"Workspace: {working_dir}\n"),
                    contains_string("- alpha"),
                )),
                working_dir=working_dir,
                transcript_path=working_dir / "critique.md",
                additional_dirs=(task_to_evaluate / "scene",),
            )
            assert_that(result, equal_to(Failure(
                [{"characteristic": "alpha", "failure": "alpha reason"}])
            ))

        def test_should_return_only_the_failed_rows(self, evidence_source, working_dir, task_to_evaluate):
            session = MagicMock(spec=ClaudeSession)
            session.run.return_value = (
                '[{"characteristic": "alpha", "status": "PASS"},'
                ' {"characteristic": "beta", "status": "FAIL"}]'
            )

            result = Critic(session=session).evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir,
                evidence_source=evidence_source,
                should=[
                    {"characteristic": "alpha", "failure": "alpha reason"},
                    {"characteristic": "beta", "failure": "beta reason"},
                ],
            )

            assert_that(result, equal_to(Failure(
                [{"characteristic": "beta", "failure": "beta reason"}])
            ))

    class TestPasses:
        def test_should_return_success_with_the_scorecard_when_all_pass(self, evidence_source, working_dir, task_to_evaluate):
            session = MagicMock(spec=ClaudeSession)
            session.run.return_value = '[{"characteristic": "alpha", "status": "PASS"}]'

            result = Critic(session=session).evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir,
                evidence_source=evidence_source,
                should=[{"characteristic": "alpha", "failure": "alpha reason"}],
            )

            assert_that(result, equal_to(Success(ScorecardResults(
                should=[{"characteristic": "alpha", "failure": "alpha reason"}],
                results=[{"characteristic": "alpha", "status": "PASS"}],
            ))))

    class TestBuildsPrompt:
        def test_should_include_distinct_evidence_source_in_prompt(self, working_dir, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            evidence_source = Path("/workspace/other-run/transcript.md")

            Critic(session=session_that_passes).evaluate(
                evidence_source=evidence_source,
                task_to_evaluate=task_to_evaluate, workspace=working_dir, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                prompt=matching(contains_string(
                    f"Transcript: {evidence_source}\n"
                )),
                working_dir=ANY, transcript_path=ANY, additional_dirs=ANY,
            )

        def test_should_embed_working_dir_in_prompt(self, evidence_source, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            working_dir = Path("/workspace/embedded-in-prompt")

            Critic(session=session_that_passes).evaluate(
                workspace=working_dir,
                task_to_evaluate=task_to_evaluate, evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                prompt=matching(contains_string(
                    f"Workspace: {working_dir}\n"
                )),
                working_dir=ANY, transcript_path=ANY, additional_dirs=ANY,
            )

        def test_should_list_characteristic_names_in_prompt(self, evidence_source, working_dir, task_to_evaluate):
            session_that_passes = MagicMock(spec=ClaudeSession)
            session_that_passes.run.return_value = (
                '[{"characteristic": "first thing", "status": "PASS"},'
                ' {"characteristic": "second thing", "status": "PASS"}]'
            )

            Critic(session=session_that_passes).evaluate(
                should=[
                    {"characteristic": "first thing", "failure": "n/a"},
                    {"characteristic": "second thing", "failure": "n/a"},
                ],
                task_to_evaluate=task_to_evaluate, workspace=working_dir, evidence_source=evidence_source,
            )

            session_that_passes.run.assert_called_once_with(
                prompt=matching(contains_string(
                    "- first thing\n- second thing"
                )),
                working_dir=ANY, transcript_path=ANY, additional_dirs=ANY,
            )

        def test_should_present_reference_scene_for_equivalence(self, evidence_source, working_dir, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            Critic(session=session_that_passes).evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir, evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                prompt=matching(all_of(
                    contains_string(f"Reference scene: {task_to_evaluate / 'scene'}\n"),
                    contains_string(
                        "The reference scene is the canonical end-state; "
                        "for characteristics about the workspace, judge by equivalence to it."
                    ),
                )),
                working_dir=ANY, transcript_path=ANY, additional_dirs=ANY,
            )

    class TestCallsSession:
        def test_should_pass_working_dir_to_session(self, evidence_source, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            working_dir = Path("/workspace/passed-to-session")

            Critic(session=session_that_passes).evaluate(
                workspace=working_dir,
                task_to_evaluate=task_to_evaluate, evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                working_dir=working_dir,
                prompt=ANY, transcript_path=ANY, additional_dirs=ANY,
            )

        def test_should_derive_critique_path_from_working_dir(self, evidence_source, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            working_dir = Path("/workspace/derives-critique-path")

            Critic(session=session_that_passes).evaluate(
                workspace=working_dir,
                task_to_evaluate=task_to_evaluate, evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                transcript_path=working_dir / "critique.md",
                prompt=ANY, working_dir=ANY, additional_dirs=ANY,
            )

        def test_should_grant_the_session_access_to_the_reference_scene(self, evidence_source, working_dir, one_characteristic_scorecard, session_that_passes, task_to_evaluate):
            Critic(session=session_that_passes).evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir, evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                additional_dirs=(task_to_evaluate / "scene",),
                prompt=ANY, working_dir=ANY, transcript_path=ANY,
            )

    class TestErrors:
        def test_should_raise_when_the_scorecard_is_empty(self, evidence_source, working_dir, dummy, task_to_evaluate):
            with pytest.raises(ValueError) as excinfo:
                Critic(session=dummy).evaluate(
                    should=[],
                    task_to_evaluate=task_to_evaluate, workspace=working_dir, evidence_source=evidence_source,
                )

            assert_that(str(excinfo.value), equal_to(
                "scorecard must not be empty"
            ))
