from pathlib import Path

import pytest
from agent import Agent
from archiver import archive, current_timestamp
from auditor import Auditor
from claude_cli import ClaudeCli
from claude_session import ClaudeSession
from claude_transcriber import ClaudeTranscriber
from critic import Critic
from fake_agent import FakeAgent

TASKS = Path(__file__).parent / "tasks"
XDD_PLUGIN = Path(__file__).parent.parent / "xdd-plugin"


def pytest_addoption(parser):
    parser.addoption("--inspector", default=None, choices=["auditor", "critic"])
    parser.addoption("--agent", default="fake", choices=["fake", "real"])
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
    match _inspector_for(
        agent=request.config.getoption("--agent"),
        inspector=request.config.getoption("--inspector"),
    ):
        case "auditor":
            return Auditor()
        case "critic":
            return Critic(
                session=ClaudeSession(
                    claude=ClaudeCli(),
                    transcriber=ClaudeTranscriber(),
                    home=Path.home())
            )


def _inspector_for(*, agent: str, inspector: str | None) -> str:
    if inspector is not None:
        return inspector
    return "critic" if agent == "real" else "auditor"


@pytest.fixture
def agent(request):
    match request.config.getoption("--agent"):
        case "fake":
            return FakeAgent(tasks_root=TASKS)
        case "real":
            return Agent(
                tasks_root=TASKS,
                session=ClaudeSession(
                    claude=ClaudeCli(plugin_dir=XDD_PLUGIN),
                    transcriber=ClaudeTranscriber(),
                    home=Path.home())
            )
