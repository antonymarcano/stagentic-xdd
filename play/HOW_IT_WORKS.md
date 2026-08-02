# How Stagentic Play works

The inner workings, for anyone changing `play` rather than writing scenarios
with it. See [README.md](README.md) for how to use it.

## A real agent run

`Agent` owns the workspace conventions — where the prompt comes from, and where
the transcript goes — and delegates the run itself to three collaborators.

- **`Agent(tasks_root=…, session=…)`** reads the prompt from
  `<tasks_root>/<task>/TASK.md`, asks its session to run it, and returns
  `Success(<working_dir>/transcript.md)`.
- **`ClaudeSession(claude=…, transcriber=…, home=…)`** gives the run a new
  session id, calls the CLI, then transcribes the log that run produced. Its
  `run` returns what the CLI printed on stdout, which is what a `Critic` reads
  as the agent's answer.
- **`ClaudeCli(runner=subprocess.run, plugin_dir=…)`** builds and runs the
  `claude -p` command, with the workspace as the process's working directory. It
  raises `RuntimeError` carrying the CLI's stderr when the command fails. The
  `runner` seam is what lets its own tests assert on the command without
  launching anything.
- **`ClaudeTranscriber()`** reads the session's JSONL log and renders it as
  readable markdown — a header naming the CLI version and model, then the
  prompts, the assistant's messages, and each tool it used.

`ClaudeJsonlPath` works out where the CLI wrote that log, from the home
directory, the workspace, and the session id.

### Handing over the workspace's permissions

Claude Code ignores a `permissions.allow` list it finds inside a workspace that
has not been trusted, and a scenario's workspace is a new temporary directory,
which never has been. So `ClaudeCli` passes the file's path to the CLI with
`--settings`. A file handed over on the command line is not one the CLI found
lying in a directory, so its permissions apply.

The flag is passed only when the workspace actually has a
`.claude/settings.json`, which leaves callers that pass a bare workspace — the
contract and integration tests among them — unaffected.

See ADR [0016](../docs/architecture/decisions/0016-hand-the-agent-its-permissions-as-a-launch-argument.md).

## Inspectors

Both inspectors implement the `Inspector` protocol:

```python
evaluate(*, task_to_evaluate: Path, workspace: Path,
         evidence_source: Path, should: list[dict]) -> Result
```

Each derives the reference scene as `task_to_evaluate / "scene"`, and each
raises `ValueError` when handed an empty scorecard — a scorecard with no rows
would otherwise pass every run.

- **`Auditor()`** calls each row's `verify` with the transcript's text, the
  workspace, and the reference scene. The rows that return false are the
  failures.
- **`Critic(session=…)`** builds a prompt naming the transcript, the workspace,
  the reference scene, and every characteristic, and asks for a JSON array of
  `characteristic`/`status` back. It runs through a `ClaudeSession` of its own,
  so its reasoning is transcribed to `critique.md` in the workspace.

`ScorecardResults` holds the scorecard alongside the results and answers
`failures()`. `ScorecardResults.from_` is what turns a critic's answer into
one, rejecting a reply that is missing rows or carrying malformed ones.
`scorecard_json_extraction` finds the JSON array in a reply that may also
contain prose.

## Results

`Success` and `Failure` are generic dataclasses, each holding a `value`. A
`Success` from an inspector holds the `ScorecardResults`; a `Failure` holds the
list of failed rows, each with its `characteristic` and `failure`.

`is_a_success()` is a hamcrest matcher over that type. Its mismatch description
runs the failure list through `formatted_failures_for`, which is why a failing
scenario reads as a list of characteristics rather than as a dataclass dump.

## The archiver

`is_archivable` answers whether the run is worth archiving: the pytest phase
must be `call`, and there must be both a workspace and an artefacts directory.
Keeping that decision separate from `archive` is what lets the hook stay a
single `if`.

`archive` copies the workspace to `<artefacts_dir>/<timestamp>-<test>-<suffix>`,
the random suffix keeping parallel runs of the same test apart. It leaves out
`.venv`, `__pycache__` and `.pytest_cache` — `.venv` because following it into a
shared package cache races with other workers, the other two because they are
regenerable state rather than a record of the run.

## The test lanes

`play` has its own suite, in three lanes:

- unit tests — the default lane, needing no CLI;
- `contract` — tests that call the real `claude` CLI to check it does what
  `ClaudeCli` expects of it;
- `integration` — tests that exercise a full inspector against a real CLI.

Test doubles live in `tests/test_doubles/`. See [COMMANDS.md](../COMMANDS.md)
for the commands, including the mutation-testing gate.
