from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest
from hamcrest import assert_that, equal_to

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

    class TestSucceeds:
        def test_should_call_verify_with_evidence_text_and_working_dir(self, tmp_path):
            evidence_text = "hello agent"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            working_dir = tmp_path / "workspace"
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                evidence_source=transcript,
                workspace=working_dir,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
            )

            verify.assert_called_once_with(
                evidence_text, working_dir
            )

        def test_should_pass_evidence_text_to_verify(self, tmp_path, dummy_path):
            evidence_text = "different transcript"
            transcript = tmp_path / "transcript.md"
            transcript.write_text(evidence_text)
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                evidence_source=transcript,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
                workspace=dummy_path,
            )

            verify.assert_called_once_with(evidence_text, ANY)

        def test_should_pass_working_dir_to_verify(self, evidence_source):
            working_dir = Path("/some/other/dir")
            verify = MagicMock(return_value=True)

            Auditor().evaluate(
                workspace=working_dir,
                should=[
                    {"characteristic": "captures input",
                     "verify": verify,
                     "failure": "n/a"},
                ],
                evidence_source=evidence_source,
            )

            verify.assert_called_once_with(ANY, working_dir)

        def test_should_return_success_with_the_scorecard_when_all_pass(self, evidence_source, dummy_path):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": "alpha",
                     "verify": lambda transcript, working_dir: True,
                     "failure": "alpha reason"},
                ],
                evidence_source=evidence_source, workspace=dummy_path,
            )

            assert_that(result, equal_to(Success(ScorecardResults(
                should=[{"characteristic": "alpha", "failure": "alpha reason"}],
                results=[{"characteristic": "alpha", "status": "PASS"}],
            ))))

        def test_should_build_the_passing_scorecard_from_the_should(self, evidence_source, dummy_path):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": "beta",
                     "verify": lambda transcript, working_dir: True,
                     "failure": "beta reason"},
                ],
                evidence_source=evidence_source, workspace=dummy_path,
            )

            assert_that(result, equal_to(Success(ScorecardResults(
                should=[{"characteristic": "beta", "failure": "beta reason"}],
                results=[{"characteristic": "beta", "status": "PASS"}],
            ))))

    class TestFails:
        def test_should_return_only_the_failed_rows_as_entries(self, evidence_source, dummy_path):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": "first characteristic",
                     "verify": lambda transcript, working_dir: False,
                     "failure": "first failure"},
                    {"characteristic": "middle characteristic",
                     "verify": lambda transcript, working_dir: True,
                     "failure": "middle failure"},
                    {"characteristic": "third characteristic",
                     "verify": lambda transcript, working_dir: False,
                     "failure": "third failure"},
                ],
                evidence_source=evidence_source, workspace=dummy_path,
            )

            assert_that(result, equal_to(Failure([
                {"characteristic": "first characteristic", "failure": "first failure"},
                {"characteristic": "third characteristic", "failure": "third failure"},
            ])))

        def test_should_return_failure_with_the_failed_entries(self, evidence_source, dummy_path):
            result = Auditor().evaluate(
                should=[
                    {"characteristic": "my characteristic",
                     "verify": lambda transcript, working_dir: False,
                     "failure": "my failure message"},
                ],
                evidence_source=evidence_source, workspace=dummy_path,
            )

            assert_that(result, equal_to(Failure([
                {"characteristic": "my characteristic", "failure": "my failure message"}
            ])))

    class TestErrors:
        def test_should_raise_when_the_scorecard_is_empty(self, dummy_path):
            with pytest.raises(ValueError) as excinfo:
                Auditor().evaluate(
                    evidence_source=dummy_path,
                    workspace=dummy_path,
                    should=[],
                )

            assert_that(str(excinfo.value), equal_to("scorecard must not be empty"))
