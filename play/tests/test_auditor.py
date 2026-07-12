from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import assert_that, equal_to
from stagentic.test.cases import case

from auditor import Auditor
from result import Failure, Success
from scorecard_results import ScorecardResults


class TestAuditor:
    @pytest.fixture
    def evidence_source(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    @pytest.fixture
    def task_to_evaluate(self): return Path("/workspace/tasks/3-some-task")

    class TestFails:
        def test_should_call_verify_and_return_a_failure_for_failed_characteristics(self, tmp_path, task_to_evaluate):
            evidence_text = "hello agent"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            working_dir = tmp_path / "workspace"
            verify = MagicMock(return_value=False)

            result = Auditor().evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=working_dir,
                evidence_source=transcript,
                should=[
                    {"characteristic": "my characteristic",
                     "verify": verify,
                     "failure": "my failure message"},
                ],
            )

            verify.assert_called_once_with(evidence_text, working_dir, task_to_evaluate / "scene")
            assert_that(result, equal_to(Failure([
                {"characteristic": "my characteristic", "failure": "my failure message"}
            ])))

        def test_should_return_only_the_failed_rows_as_entries(self, evidence_source, dummy_path, task_to_evaluate):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": "first characteristic",
                     "verify": lambda transcript, working_dir, reference_scene: False,
                     "failure": "first failure"},
                    {"characteristic": "middle characteristic",
                     "verify": lambda transcript, working_dir, reference_scene: True,
                     "failure": "middle failure"},
                    {"characteristic": "third characteristic",
                     "verify": lambda transcript, working_dir, reference_scene: False,
                     "failure": "third failure"},
                ],
                task_to_evaluate=task_to_evaluate, workspace=dummy_path, evidence_source=evidence_source,
            )

            assert_that(result, equal_to(Failure([
                {"characteristic": "first characteristic", "failure": "first failure"},
                {"characteristic": "third characteristic", "failure": "third failure"},
            ])))

    class TestSucceeds:
        @pytest.mark.parametrize("characteristic, failure", [
            case("alpha", characteristic="alpha", failure="alpha reason"),
            case("beta", characteristic="beta", failure="beta reason"),
        ])
        def test_should_return_success_with_the_scorecard_when_all_pass(self, characteristic, failure, evidence_source, dummy_path, task_to_evaluate):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": characteristic,
                     "verify": lambda transcript, working_dir, reference_scene: True,
                     "failure": failure},
                ],
                task_to_evaluate=task_to_evaluate, workspace=dummy_path, evidence_source=evidence_source,
            )

            assert_that(result, equal_to(Success(ScorecardResults(
                should=[{"characteristic": characteristic, "failure": failure}],
                results=[{"characteristic": characteristic, "status": "PASS"}],
            ))))

    class TestCallsVerify:
        def test_should_pass_evidence_text(self, tmp_path, dummy_path, task_to_evaluate):
            evidence_text = "different transcript"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                evidence_source=transcript,
                task_to_evaluate=task_to_evaluate, workspace=dummy_path,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
            )

            verify.assert_called_once_with(evidence_text, ANY, ANY)

        def test_should_pass_working_dir(self, evidence_source, task_to_evaluate):
            working_dir = Path("/some/other/dir")
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                workspace=working_dir,
                task_to_evaluate=task_to_evaluate, evidence_source=evidence_source,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
            )

            verify.assert_called_once_with(ANY, working_dir, ANY)

        def test_should_pass_reference_scene(self, evidence_source, dummy_path, task_to_evaluate):
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                task_to_evaluate=task_to_evaluate,
                workspace=dummy_path, evidence_source=evidence_source,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
            )

            verify.assert_called_once_with(ANY, ANY, task_to_evaluate / "scene")

    class TestErrors:
        def test_should_raise_when_the_scorecard_is_empty(self, dummy_path, task_to_evaluate):
            with pytest.raises(ValueError) as excinfo:
                Auditor().evaluate(
                    should=[],
                    task_to_evaluate=task_to_evaluate, workspace=dummy_path, evidence_source=dummy_path,
                )

            assert_that(str(excinfo.value), equal_to("scorecard must not be empty"))
