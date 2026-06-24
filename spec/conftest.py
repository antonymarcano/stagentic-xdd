from pathlib import Path

import pytest
from auditor import Auditor
from claude_cli import ClaudeCli
from claude_session import ClaudeSession
from claude_transcriber import ClaudeTranscriber
from critic import Critic
from fake_agent import FakeAgent

from archiver import archive, current_timestamp

TASKS = Path(__file__).parent / "tasks"


def pytest_addoption(parser):
    parser.addoption("--inspector", default="auditor", choices=["auditor", "critic"])
    parser.addoption("--.artefacts-dir", default=None)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    yield
    archive(
        phase=call.when,
        tmp_path=item.funcargs.get("tmp_path"),
        test_name=item.name,
        artefacts_dir=item.config.getoption("--.artefacts-dir"),
        timestamp=current_timestamp(),
    )


@pytest.fixture
def inspector(request):
    match request.config.getoption("--inspector"):
        case "auditor":
            return Auditor()
        case "critic":
            return Critic(
                session=ClaudeSession(
                    claude=ClaudeCli(),
                    transcriber=ClaudeTranscriber(),
                    home=Path.home())
            )


@pytest.fixture
def agent():
    return FakeAgent(tasks_root=TASKS)
