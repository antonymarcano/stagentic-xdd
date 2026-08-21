# Stagentic Play

> **Status: work in progress.**
>
> Stagentic Play is being grown inside
> `stagentic-xdd`, which is its first and only user. It will move to its own
> repository and be published as a Claude Code plugin once it has matured.
> Until then it exists here alone, there is nothing to install from a
> marketplace, and its interfaces change whenever a scenario demands it.

`play` is the framework a scenario uses to run an AI agent at a task and then
judge what it did.

Agent behaviour varies from run to run, so a scenario does not assert an exact
result. It gives the agent a task and a workspace, then evaluates the run
against a **scorecard**: a list of characteristics the run should have.

It is part of the **Stagentic** family — *stage + agentic* — tools for
auditioning agentic skills with automated rehearsals.

The theatre vocabulary runs through the code: a **scene** is the workspace state
that a task opens from and is judged against, and each run is recorded as a
transcript so it can be read back.

For what happens underneath any of this, see [HOW_IT_WORKS.md](HOW_IT_WORKS.md).

## Using it here

`play` is a package, and is not published anywhere, so a relative path source
is the only way to depend on it. A project in this repository consumes it as an
editable one, which means changes made here are picked up without reinstalling:

```toml
[dependency-groups]
dev = ["play"]

[tool.uv.sources]
play = { path = "../play", editable = true }
```

`spec/` is the working example of that.

Its modules are imported by their bare names:

```python
from agent import Agent
from critic import Critic
from result_matchers import is_a_success
```

## Writing a scenario

A scenario has two steps: perform the task, then evaluate the run.

*For now, we have a traditional Arrange, Act, Assert style. Later a
Screenplay-like given-when-then style will be added.*

```python
def test_write_a_failing_test(self, tmp_path, agent, inspector):
    working_dir = tmp_path / "miles-to-km"
    _set_opening_scene_for("0-placeholder", working_dir)
    task_name = "1-first-test-for-miles-to-km-converter"

    transcript = agent.perform(
        task=task_name,
        working_dir=working_dir,
    ).value

    assert_that(
        inspector.evaluate(
            task_to_evaluate=TASKS / task_name,
            workspace=working_dir,
            evidence_source=transcript,
            should=[
                {"characteristic": "Transcript shows the agent ran pytest",
                 "failure": "transcript shows no Bash tool running pytest"},
            ],
        ),
        is_a_success(),
    )
```

`agent` and `inspector` are fixtures defined in `conftest.py`. This allows for a
*real* agent and a *fake* agent, as well as an *auditor* (deterministic code
based evaluator) or a *critic* (a real agent evaluating non-deterministic
results).

`_set_opening_scene_for` is a helper that copies the scene's files to the
working directory. This will be added to the play framework but is a private
helper for now.

`perform` hands back the path to the run's transcript, which is the evidence the
inspector reads.

## The anatomy of a task

A **task** is one unit of agent work. Tasks live under a tasks root, each in its
own directory named `<n>-<slug>`, holding everything needed to run it and judge
it:

```
1-first-test-for-miles-to-km-converter/
├── TASK.md          # the prompt the agent is given
├── fake-task.sh     # (Optional) what a FakeAgent runs in place of an agent
└── scene/           # the workspace as it should look once the task is done
```

`TASK.md` is read as-is and becomes the agent's prompt. `fake-task.sh` is
optional — it exists only for the tasks a `FakeAgent` covers.

### The scene

A scene is a small but complete project: source, tests, a `pyproject.toml`, a
`CLAUDE.md`, and a `.claude/settings.json` naming the commands the agent is
allowed to run.

Each scene plays two parts:

- **the opening scene of a task** — copied into a fresh tmp workspace.
- **the reference scene** — the end-state an inspector judges the finished
  workspace against; which is also the opening scene of the next task.

That is what makes the tasks a chain. E.g. `0-placeholder/scene/` is the
genesis: it opens the first task, and has no `TASK.md` because nothing performs
it.

A scene also holds the `transcript.md` its own run produced. That is left behind
when the scene is copied as an opening scene — the next agent starts with the
workspace, not with a record of how it came to be.

See ADR [0007](../docs/architecture/decisions/0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md).

### Permissions in the workspace

A run is headless, so no one is there to approve a permission prompt. What the
agent may do is expressed by a `.claude/settings.json` inside the workspace,
whose `permissions.allow` list names the commands it may run.

Including a `.claude/settings.json` in a task's scene folder results in it
automatically being copied into the workspace and given to the 
agent using the --settings cli arg.

This gives you the ability to test permissions (or absence thereof) on a per
test basis.

The file has to sit at `.claude/settings.json` in the workspace root. Put it
anywhere else and it is silently ignored.

See ADR [0016](../docs/architecture/decisions/0016-hand-the-agent-its-permissions-as-a-launch-argument.md).

## Choosing an agent

An agent performs a task in a workspace and hands back the transcript of what it
did.

- **`Agent`** runs a real agent against the task's `TASK.md`. This is what
  actually exercises the guidance under test, and what a scenario must pass with
  before that guidance is considered done.
- **`FakeAgent`** runs the task's `fake-task.sh` instead. This was used as part
  of the development of the play framework. It makes the same
  workspace changes and writes the same shape of transcript a real run would.
  This keeps a scenario repeatable and fast enough to run while developing 
  the scorecard for the scenario without paying for a real run.

## Choosing an inspector

An inspector judges the finished run against the scorecard.

- **`Auditor`** checks each characteristic mechanically, by running the row's
  own `verify` callable. Deterministic, free, and instant — but it can only
  judge what a lambda can express.
- **`Critic`** asks a real agent to judge each characteristic. Slower, and its
  verdict varies between runs, but it can judge things no lambda can — whether
  the workspace is *equivalent to* the reference scene, or whether the
  transcript shows the test was written before the production code.

Both take the same call:

```python
inspector.evaluate(
    task_to_evaluate=…,   # the task's directory; its scene/ is the reference scene
    workspace=…,          # the workspace the agent worked in
    evidence_source=…,    # the transcript path perform() returned
    should=…,             # the scorecard
)
```

## Writing a scorecard

A scorecard is a list of rows, one per characteristic the run should have.

An `Auditor` row carries a `verify` callable, taking the transcript's text, the
workspace, and the reference scene, and returning a bool:

```python
{
    "characteristic": "Transcript shows the agent ran pytest",
    "verify": lambda transcript, workspace, reference_scene: "pytest" in transcript,
    "failure": "transcript shows no Bash tool running pytest",
}
```

A `Critic` row needs only `characteristic` and `failure`; a `verify` is ignored,
so one scorecard can serve both inspectors.

```python
{
    "characteristic": "Transcript shows the agent ran pytest",
    "failure": "transcript shows no Bash tool running pytest",
}
```

Write the `characteristic` as the thing that should be true — a critic is given
it verbatim to judge. Write the `failure` as what went wrong, because that is
what a scenario prints when the row fails.

## Reading the result

`evaluate` returns a success when every characteristic passed, and a failure
otherwise. Assert on it with the `is_a_success()` matcher:

```python
assert_that(inspector.evaluate(…), is_a_success())
```

On failure the matcher lists each characteristic that failed alongside its
`failure` text, so the report reads as what the agent did wrong rather than as a
mismatched data structure.

## Keeping a run's artefacts

A run's workspace is a temporary directory, so it is gone once the test ends. To
keep it — to read the transcript, or a critic's reasoning, after the fact — call
`archive` from a pytest hook:

```python
if is_archivable(phase=call.when, tmp_path=tmp_path, artefacts_dir=artefacts_dir):
    archive(tmp_path=tmp_path, test_name=item.name,
            artefacts_dir=artefacts_dir, timestamp=current_timestamp())
```

`is_archivable` decides whether there is anything to archive and anywhere to put
it, so a run with no artefacts directory configured simply keeps nothing.
`archive` copies the workspace to a uniquely named folder.

This is an area that will be simplified before first release.

## Wiring it up

The fixtures a scenario uses are built in the consuming project's
`conftest.py`. A real agent is assembled from its collaborators:

```python
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
                    home=Path.home(),
                ),
            )
```

An inspector likewise, with the critic needing a session of its own:

```python
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
                    home=Path.home(),
                )
            )
```

Assembling these by hand is temporary. What each collaborator is for is in
[HOW_IT_WORKS.md](HOW_IT_WORKS.md).
