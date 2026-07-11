import subprocess
import sys
from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest
from cases import case
from hamcrest import assert_that, contains_string, equal_to

from conftest import _reject_incompatible_inspector

SPEC_DIR = Path(__file__).parent.parent


class TestInspectorGuard:
    @pytest.mark.parametrize("agent, inspector, expectation", [
        case(
            "the-auditor-judging-the-real-agent-is-rejected",
            agent="real", inspector="auditor",
            expectation=pytest.raises(pytest.UsageError),
        ),
        case(
            "the-real-agent-defaults-to-the-critic",
            agent="real", inspector=None,
            expectation=does_not_raise(),
        ),
        case(
            "the-critic-may-judge-the-real-agent",
            agent="real", inspector="critic",
            expectation=does_not_raise(),
        ),
        case(
            "the-auditor-may-judge-the-fake-agent",
            agent="fake", inspector="auditor",
            expectation=does_not_raise(),
        ),
    ])
    def test_should_reject_only_the_auditor_judging_the_real_agent(
        self, agent, inspector, expectation
    ):
        with expectation:
            _reject_incompatible_inspector(agent=agent, inspector=inspector)


class TestInspectorGuardWiring:
    def test_should_abort_a_real_agent_auditor_run(self):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "--co", "-n0",
             "--agent=real", "--inspector=auditor"],
            cwd=SPEC_DIR, capture_output=True, text=True, check=False,
        )
        assert_that(result.returncode, equal_to(pytest.ExitCode.USAGE_ERROR))
        assert_that(
            result.stderr,
            contains_string(
                "the auditor can only evaluate deterministic results, so it "
                "cannot judge the real agent; use --inspector=critic (the default)"
            ),
        )
