from pathlib import Path

import pytest
from hamcrest import all_of, assert_that, has_item
from matchers import does_not

from claude_cli import ClaudeCli
from claude_session import ClaudeSession
from claude_transcriber import ClaudeTranscriber
from critic import Critic
from result_matchers import is_a_success

_TRANSCRIPT_PYTEST_RAN_AND_PASSED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 passed in 0.01s
"""

_TRANSCRIPT_PYTEST_RAN_AND_FAILED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 failed in 0.01s
"""


@pytest.mark.integration
class TestCriticIntegration:
    @pytest.fixture
    def session(self):
        return ClaudeSession(
            claude=ClaudeCli(),
            transcriber=ClaudeTranscriber(),
            home=Path.home(),
        )

    def test_should_fail_when_a_characteristic_is_not_met(self, session, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

        result = Critic(session=session).evaluate(
            evidence_source=transcript,
            workspace=tmp_path,
            task_to_evaluate=tmp_path,
            should=[
                {"characteristic": "Transcript shows the agent ran pytest",
                 "failure": "No pytest invocation found in the transcript"},
                {"characteristic": "Transcript shows a PASS pytest result",
                 "failure": "No PASS result found in the transcript"},
            ],
        )

        failed_characteristics = [row["characteristic"] for row in result.value]
        assert_that(failed_characteristics, all_of(
            has_item("Transcript shows a PASS pytest result"),
            does_not(has_item("Transcript shows the agent ran pytest")),
        ))

    def test_should_pass_when_all_characteristics_are_met(self, session, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_PASSED)

        result = Critic(session=session).evaluate(
            evidence_source=transcript,
            workspace=tmp_path,
            task_to_evaluate=tmp_path,
            should=[
                {"characteristic": "Transcript shows the agent ran pytest",
                 "failure": "No pytest invocation found in the transcript"},
                {"characteristic": "Transcript shows a PASS pytest result",
                 "failure": "No FAILED result found in the transcript"},
            ],
        )

        assert_that(result, is_a_success())
