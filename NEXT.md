# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 0. Working approach

One change at a time: apply it, run the test(s) the change's scope calls
for, then propose a commit — behavioural and structural changes kept in
separate commits (see
[`docs/working-practices.md`](docs/working-practices.md)).

At the start of the review run the full baseline tests and then full mutation test.
If clear, for a file under review, add all lenses in the correct order to the task list.
For each, one at a time:
- Tell me the lens
- If no issues seen through that lens, say no issues (no explanation needed)
- If changes are required, show me the before and after of the change you propose.  

### Reviewing a test file

Review the file through each lens below in turn, confirming each one by
one — even where it needs no change. Most lenses are the conventions in
[`docs/architecture/conventions/test-conventions.md`](docs/architecture/conventions/test-conventions.md);
the last two are inferred from the reviewed exemplars.
Add each lens to your task list for easy tracking in the session.

Review the file through each lens below in turn and in the order below:

- Test naming `test_should_<behaviour>`
- Test order follows the production code's execution flow
- MagicMock interrogation forms
- Whole-story tests
- Test names read in context of their holding class
- Per-property test layout: relevant kwargs at the top
- Explicit no-raise via `does_not_raise`
- Write parametrise rows with `case`
- Parametrise value-flow tests over ≥2 cases with `ids`
- Don't test Python's own enforcement
- Assertion vocabulary: PyHamcrest matchers
- Pin exact composed output once via `==`
- `spec=Class` vs `spec=Class()` for directly-callable spies
- Stub callable → lambda; spy callable → `MagicMock`
- Marker placement: lane marker on the holding class, not the method (inferred)
- Import grouping: stdlib / third-party / first-party (inferred, ruff-enforced)

### Reviewing a src file

As above, but through these lenses. Most are the conventions in
[`docs/architecture/conventions/src-conventions.md`](docs/architecture/conventions/src-conventions.md);
the last two are inferred from the reviewed exemplars.
Add each lens to your task list for easy tracking in the session.

Review the file through each lens below in turn and in the order below:

- Type hints on every public method parameter (avoid `Any`)
- Required vs optional: no `| None = None` defaults for test convenience
- Runtime guards for semantic preconditions the type system can't express
- Helper-function parameter order mirrors the call it makes
- IDE warning suppression with an inline rationale comment
- Private functions follow the order their calls appear
- Orchestrator methods read at a single level of abstraction
- Naming-suffix vocabulary for private helpers
- Kwarg-style helpers compose into prose at the call site
- Public methods take keyword-only args (`*` separator) (inferred)
- Import grouping: stdlib / third-party / first-party (inferred, ruff-enforced)

## 1. Improvement plan

We are working through each file in turn, bringing each up to the reference
standard set by `critic.py` / `TestCritic` — matching the conventions inferred
from `critic.py` and `test_critic.py` — and running mutation testing to confirm
coverage.

`critic.py` is the current reference standard for this repo's production code.
`TestCritic` is the current reference standard for tests.

For each file:
- Review the test first, then the implementation; bring both to the standard
  set by `critic.py` / `test_critic.py`.
- Match the conventions inferred from those files, alongside the documented
  conventions in `docs/architecture/conventions/`.
- Run mutation testing (`mutmut`, per ADR
  [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md)):
  review survivors against the tests and act where appropriate. Read-only for now (ADR 0010 stage 1); "where
  appropriate" is judgement, not an enforced gate. `source_paths` grows by one
  file as each reaches acceptable coverage.

The conventions in `docs/architecture/conventions/` are the standard; the
reference-standard files above are exemplars, not infallible. A file under
review may already exceed them in places. Anchor each proposed change on the
convention text and judgement, not on what other files happen to do. Follow
the working practices in [`docs/working-practices.md`](docs/working-practices.md)
for the workflow itself, rather than inferring one from the files.

Some files have a per-file punch list at
`docs/architecture/improvements/<file>.md` — items tracked separately so they
don't bury NEXT.md.

### `play/src/`

- [x] `critic.py` (and `tests/test_critic.py`, `tests/integration/test_critic_integration.py`)
- [x] `agent.py` (and `tests/test_agent.py`)
- [x] `result.py` (and `tests/test_result.py`)
- [x] `result_matchers.py` (and `tests/test_result_matchers.py`)
- [x] `fake_agent.py` (and `tests/test_fake_agent.py`)
- [x] `claude_cli.py` (and `tests/test_claude_cli.py`, `tests/contract/test_claude_cli.py`)
- [x] `claude_session.py` (and `tests/test_claude_session.py`)
- [ ] `auditor.py` (and `tests/test_auditor.py`)
- [ ] `scorecard_results.py` (and `tests/test_scorecard_results.py`)
  - Outstanding improvements tracked in
    [`docs/architecture/improvements/scorecard_results.md`](docs/architecture/improvements/scorecard_results.md).
- [ ] `transcriber.py` (and `tests/test_transcriber.py`)
- [ ] `claude_jsonl_path.py` (and `tests/test_claude_jsonl_path.py`)
- [ ] `failure_message.py` (and `tests/test_failure_message.py`)
- [ ] `raise_when.py` (and `tests/test_raise_when.py`)
- [ ] `scorecard_json_extraction.py` (and `tests/test_scorecard_json_extraction.py`)
- [ ] `inspector.py` — No test yet

A cross-cutting improvement surfaced by the critic extraction — a
`ScorecardEntry` type spanning `Critic`, `Auditor`, and `formatted_failures_for`
— is deferred and tracked in
[`docs/architecture/improvements/scorecard-entry.md`](docs/architecture/improvements/scorecard-entry.md).

### `spec/`

- [ ] `archiver.py` (and `tests/test_archiver.py`)
- [ ] `conftest.py`

### Error handling (cross-cutting — final review)

A final pass over error handling across the harness, after the per-file
reviews above. `ClaudeSession`, for one, has no error handling and does not
wrap errors raised by `ClaudeCli` — whether it should is a question the
per-file lenses don't currently cover.

**Prerequisite:** the error-handling strategy must be agreed and documented
first. An ADR captures the 'why' and proposes the 'how';
`docs/architecture/conventions/src-conventions.md` hosts the finally agreed
'how'. The review checks each file against the agreed convention, so it
can't run until that convention exists.

A candidate convention to start from — every public entry point to the
`play` framework:
- returns `Success` when it succeeds;
- returns `Failure` for an in-domain failure;
- raises an exception for a mechanical/infrastructure failure (file not
  found, network unavailable).

This may become the standard for all files.

## 2. Write the xdd skill

The `play/` harness is committed: `Agent`, `Transcriber`, and JSONL path
computation are in `play/src/`. What remains on the harness side is wiring
`spec/conftest.py` to expose `--agent=real` — this was built and validated
locally but reverted pending the scenario passing.

A first draft of the scenario's task,
`spec/tasks/1-first-test-for-miles-to-km-converter/TASK.md`, already exists in
the working tree but is deliberately left **untracked**. It lands with the
commit below (alongside `spec/conftest.py` and
`0-placeholder/scene/.claude/settings.json`) only once the improvement plan
(§1) is complete and the scenario passes — not before.

A real run (before the revert) confirmed all five scorecard checks fail —
the agent lacks the guidance a skill would provide.

The workspace already has `spec/tasks/0-placeholder/scene/.claude/settings.json`
allowing `Bash(uv run pytest*)`, so the agent can run tests once the skill
steers it correctly.

The skill needs to guide the agent to:
1. Replace the placeholder test with a failing test that imports from `conversion`.
2. Create a stub `src/conversion.py` so the test fails at assertion (not import).
3. Run `uv run pytest` and confirm the result is `FAILED`.

Once `--agent=real` is green:
- Add integration tests for the real-agent path one at a time.
  *(cf. `ea7b497`)*
- Commit `spec/conftest.py`, `TASK.md`, and
  `0-placeholder/scene/.claude/settings.json` together.

## Future options

- **Critic saves results to a file**: instruct the critic prompt to write
  its scorecard to a specific file (e.g. `scorecard.json`) rather than
  returning JSON in the response text. The file would contain only JSON,
  sidestepping the prose-stripping problem entirely.
- **Mix mechanical and judgement characteristics in one scorecard**:
  the auditor today verifies rows that carry a `verify` lambda; the
  critic today judges rows that carry only prose. A scorecard given
  to the critic could mix both shapes — the critic would judge the
  prose rows and delegate the lambda-bearing rows to the auditor.
  Other routing approaches are possible.

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.

## Enforcing working-practices via hooks

This began as a way to make the dev process less painful. It became more
than that: a technique we tested and proved, and one that may turn into a
mechanism for building the xdd skill itself.

**What happened.** The working practices live in
`docs/working-practices.md`, and the agent reads them at session start.
Even so, it kept skipping steps — pulled back toward habits from its
training data.

The specific miss: on every green, the agent skipped both the focused
mutation test and the commit. It was too eager to get on to writing the
next test.

**What we decided.** Nudge the agent with a hook at the moment it reaches
green — exactly where the miss happens. A reminder injected into context,
not a block.

It was tested this session and worked: the nudge fired on each green with
a mutation target in flight, and pulled the green step back into view.

**Why it matters beyond the dev process.** The xdd skill's job is to steer
an agent through Red-Green-Refactor. A hook that nudges at green is that
same kind of steering. So what we prove here may carry straight into how
the skill is built — this is learning for the product, not throwaway
scaffolding.

The hooks are still spike code: written quickly, no tests yet. If they
become part of the skill, they get the proper TDD treatment then.

**Why a hook, not just the doc.** A `CLAUDE.md` pointer is advisory — it
needs the agent to read *and* apply the doc, and both have failed
(read-but-not-applied, and applied-as-paraphrase). A hook puts the nudge
in the harness instead of in prose. Scripts live in `.claude/hooks/`;
config in the checked-in `.claude/settings.json`.

The hooks — built, and candidates:

- **SessionStart — inject working-practices (built).** Prints the literal
  text of `docs/working-practices.md` into context via
  `hookSpecificOutput.additionalContext` — the actual words, not a pointer,
  because the failure mode was paraphrase, not ignorance. Cannot block.
- **PostToolUse after pytest — green nudge (built, proven this session).**
  On a pytest green, injects a reminder to run the focused mutation check
  (see [Mutation testing](COMMANDS.md#mutation-testing)) on the in-flight
  file before moving on. Cannot block (it runs after the tool); a pure
  reminder. Targets the exact miss:
  moving on from a green without the focused mutation test.
- **PostToolUse after mutmut — marker writer (candidate).** Would detect
  `mutmut run`, parse the result, and write a marker (timestamp +
  clean/dirty) for a commit gate to read.
- **PreToolUse before commit — the gate (candidate).** Would block the
  commit (exit 2 / `permissionDecision: deny`) unless the mutmut marker is
  newer than the most-recently-edited `source_paths` file, and list the
  missing steps.

The marker writer and the gate are ideas, not plans. We build them only if
we see cases where the nudges alone aren't enough.

If we do build the gate, two questions are open:

- **Hard block or soft warn.** A hard block enforces the mechanical check
  but is brittle: a buggy gate blocks good commits, and judgement clauses
  ("a survivor must be a *documented* accepted-mutation") can't be encoded,
  so it would block on survivors it can't judge. Current lean: hard block
  on the mechanical check (mutmut ran clean since the last edit), warn-only
  when survivors are present, leaving judgement to the agent.
- **Matcher robustness.** The scripts parse `tool_input.command`
  themselves rather than trust an `if: Bash(git commit*)` glob, because the
  repo convention is `git -C <repo> commit`, which the naive glob misses.

**Known limits.** A hook sees one command and its args, not the meaning of
the session. String matchers can be dodged by spelling things differently.
Judgement clauses can't be encoded. So the hooks back up the mechanical
steps only — they don't remove the agent's job of applying the doc.
