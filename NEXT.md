# NEXT

> Do not reference this file in commit messages except those about this file itself.
> NEXT.md tracks the immediate next step and is rewritten as work lands (without 
> any mention of what was just completed.

## 1. Isolate what carries the xdd skill — drop the Workflow, try a principles framing

The committed xdd skill drove the write-order misstep to 0/100 with a
compose→evaluate→write Workflow, a read-first step, motivation, and the TDD Model
corrections — but which parts are load-bearing is untested (see this
[lesson](docs/lessons/20260628-1800-write-the-failing-test-before-the-production-code/lesson.md#future-experiments-to-try)).
Measure variations
against the committed wording with the batch/tally scripts
([COMMANDS.md](COMMANDS.md)): snapshot each, run to n=100 (alternating against the
committed wording to cancel time/load drift); the go-live bar is ≤1/100 total
failures.

- **Drop the Workflow section**, keeping only the "read any related test/code
  first" directive alongside the Model corrections and motivation — does
  write-order hold at ~0/100 without the procedural loop?
- **Replace the workflow with a set of principles**, framed as "A good
  Test-Driven Developer always follows these principles…" followed by a list of
  principles rather than a procedure — does a principles framing hold as well as
  the workflow?

## 2. Capture code-change diffs in the run transcript — Edit still to do

The captured `transcript.md` (produced by `ClaudeTranscriber`) renders a tool use
as only its `file_path`, so what the agent changed can be invisible to a reviewer
or critic reading the transcript.

**Write — done.** A Write now renders the content it wrote as a fenced block, by
default (the branch-by-abstraction seam is collapsed and the approval masters
migrated).

**Edit — still to do.** Render the before/after (`old_string` → `new_string`) as a
diff. The JSONL already carries the full tool input. TDD in `play`
(`claude_transcriber.py`) — extend the current transcriber, rather than waiting on
the ground-up rewrite in ADR 0014.

## 3. Observed Misstep: Added multiple cases to a test all at once

Introducing a parametrised `case` is introducing a test, so adding more than one
case at once writes several failing tests before any production change — the same
smallest-step break as composing several plain test methods up front. A `case`
earns its place only to remove or avoid duplication, and lands across two commits:

1. **Refactor** the existing single test into the parametrised shape over its one
   present case — behaviour-preserving, no new assertion (structural).
2. **Add** the next case as its own behavioural commit; one case per commit
   thereafter.

**Still to do:**
- Add a scenario to `spec/tests/test_red_green_commit.py` that judges an agent
  introducing cases this way — one at a time, refactor-first — rather than
  landing a multi-case parametrised block in a single step.
- Work out how to build the scene that recreates the misstep: the opening
  workspace state that tempts an agent into adding several cases at once.

## 4. N× batch gateway — run a scenario Nx and tally (belongs in play)

Guidance experiments (baseline vs a `SKILL.md` change) are measured by running a
scenario many times and tallying per-run outcomes. Until this lands, an interim
10× command in [COMMANDS.md](COMMANDS.md) runs the real-agent scenarios at 10-way
concurrency with no launch stagger; it launches but does not tally, so the signals (did the skill
load; literal vs formula) are read per run by hand.

Make it a first-class mechanism in **play** — framework work, not a spec helper or
a shell loop (cf. "Review later: move scene management to play"). Run a named
scenario N times with capped concurrency and return a per-run tally and pass-rate.
Per run, capture the pytest result plus the scenario's signals (skill loaded; the
production shape). This makes experiments (baseline vs B, gateway variants)
reproducible rather than one-off.

## 5. Contract-test ClaudeCli's options

`ClaudeCli` passes `--permission-mode`, `--session-id`, `--add-dir`, and
`--plugin-dir` to real claude, but only a bare prompt is contract-tested
(`play/tests/contract/test_claude_cli.py`). Add one contract test per option,
verifying it does what we expect against the real CLI, one at a time.

**Deferred — versions / CLI upgrade.** ADR 0016 (trust the workspace) and the
move to 2.1.195 aren't needed on 2.1.191 — the gate is absent; the trust marking
becomes necessary only on 2.1.193+.

## 6. Pin and record reasoning effort and the context window

ADR [0019](docs/architecture/decisions/0019-pin-and-record-reasoning-effort-and-context-window.md)
(Proposed): a run transcript records the CLI version and model (ADR
[0017](docs/architecture/decisions/0017-record-cli-version-and-model-in-the-run-transcript.md)),
but not the **reasoning effort** or the **context window** a run used — both bear
on a lesson's provenance (ADR
[0015](docs/architecture/decisions/0015-capture-xdd-skill-missteps-as-lessons.md)).
What was learned while capturing the first lesson:

- The harness runs resolve to `claude-opus-4-8[1m]` — the **1M context** variant
  (Opus 4.8 maps to 1M by default). The header's source, `message.model`, records
  the API id `claude-opus-4-8`, dropping the `[1m]`; the `[1m]` form is visible
  only in the `system/init` event's `model`.
- The harness passes no `--effort`, so runs use the CLI **default (high** for
  Opus 4.8**)**. Effort is absent from both the session JSONL and the
  `system/init` event, so it can only be recorded as the value the harness sets.

Two pieces of work, each TDD in `play/`:

1. **Pin effort.** Add a `--effort` flag to the harness's `claude -p` invocation
   (`play/src/claude_cli.py`), pinned to **high** — the current Opus 4.8 default,
   so this locks in the behaviour the first lessons were captured under rather
   than changing it. Effort levels are **model-dependent** (Opus 4.8/4.7:
   `low|medium|high|xhigh|max`; Opus 4.6, Sonnet 4.6: `low|medium|high|max`;
   Haiku 4.5: no documented effort support), so the flag must be **gated on the
   resolved model** — never pass `--effort` to a model that does not support it
   (it would fail the run). `ClaudeCli` therefore needs to know which model it is
   invoking, or which models support the chosen level.
2. **Record effort + context.** Extend the versions header (ADR 0017) so the
   transcript records the effort the harness set and the resolved context window
   (the `[1m]` form from the `system/init` event, not the per-message
   `message.model`).

Then backfill the captured lessons' metadata from the recorded values rather than
from this investigation.

## 7. Simplify the dev commands with a build tool

The "before any commit" gate — test → lint → mutation — and the levels of test and
check (unit, contract, integration, the spec configs, focused/full mutation, the full
baseline) are currently sequenced by hand and documented as prose in
[COMMANDS.md](COMMANDS.md). In a JVM project this would be a build script (`gradle
build` runs compile → test → checks in one command). Python has no single equivalent,
and `uv` (unlike cargo/gradle) has no built-in task runner. This item explores encoding
the levels and the gate as named tasks. **Choice TBC — this will mature into an ADR
after further discussion.**

### Options considered

- **`poethepoet` (poe)** — tasks in `pyproject.toml` (`[tool.poe.tasks]`), run via
  `uv run poe <task>`. Most native to the uv + pyproject setup, but per-pyproject and
  Python-only, with no natural root to orchestrate across `play`/`spec`/`stagentic-test`.
- **`just`** — a `justfile` of recipes; recipe-with-dependencies gives a task DAG (like
  Gradle's), `just --list` gives discoverability (like `gradle tasks`), and it is
  polyglot. Scoped to this repo, a single **root `justfile`** orchestrating the
  sub-projects through `uv run --directory …` is the cleanest shape — no import/module
  machinery (that was only for cross-repo reuse, which we've decided we don't need).
- **`nox`** (`noxfile.py`) — session-based; only worth it for matrix testing across
  Python versions or dist/build steps. Overkill for chaining checks.

**Current lean: `just`, single root `justfile`.** `poe` is the fallback if we'd rather
keep tasks in `pyproject.toml`.

### Shape (levels as recipes, composites via dependencies)

Illustrative, not exhaustive:

```make
lint: lint-play lint-spec lint-helpers
play-unit:    uv run --directory play pytest -m "not contract and not integration"
play-full:    uv run --directory play pytest
helpers:      uv run --directory stagentic-test pytest
spec:         uv run --directory spec pytest tests
spec-critic:  uv run --directory spec pytest tests --inspector=critic
spec-real:    uv run --directory spec pytest tests --agent=real
mutate module:  uv run --directory play mutmut run '{{module}}*'
mutate-all:     uv run --directory play mutmut run

check: play-unit lint                        # fast, gated
baseline: play-full play-integration helpers spec spec-critic spec-real
build: lint baseline mutate-all              # the gradle-build analogue
```

Recipe dependencies run first and abort on the first failure, so the gate's ordering
comes for free; `just --list` documents the levels.

### The gating, precisely

- **Mutation must follow a green baseline** — correctness, not economy: mutation testing
  measures whether tests kill mutants, so it is meaningless on red.
- **test → lint is fail-fast economy, not a dependency** — linting a red tree isn't
  wrong, just wasted; we fix behaviour before polishing style.
- **Mutation depends on *tests*, not on *lint*** — a lint failure doesn't invalidate
  mutation results; lint sits before mutation only to fail cheap. So: tests gate
  everything; lint and mutation both need green tests but are independent of each other.

### `build` vs the current scoped rules

`gradle build` feels cheap to re-run because Gradle is **incremental and cached** — it
skips work whose inputs didn't change. A `just build` here has none of that: `baseline`
hits **real claude** (spec-critic, spec-real) and `mutate-all` is a full sweep, so a
full `build` is minutes and network-dependent every time. That is exactly why the
current "before any commit" rules in [CLAUDE.md](CLAUDE.md) are **scoped** (single test
file → just that file; play-src change → full baseline) rather than always-everything.

So the real decision is **what runs when**, not the recipe:

- **Fast vs full split** — `check` (lint + unit) for routine commits; `build` (full)
  before significant commits or in CI.
- **Automated git hook vs manual** — the Python `pre-commit` framework can run a task on
  `git commit`, but it must stay **fast** (ruff on staged files, maybe the unit lane);
  the full baseline and mutation must never live in a git hook (every commit would stall
  for minutes and call real claude). So: hook → `check`; `build` stays a task you invoke.
- **Scoped judgement vs always-full** — keep the cheaper scoped rules (a human/agent
  picks scope) or go always-full (simpler, slow, no caching to rescue it).

### What a runner cannot encode

The runner gates a command's exit code; it cannot make the mutation **judgement** — a
survivor means *subtract the speculative code* (or document an accepted-mutation), not
"add a test". That call stays with the human/agent (see
[working-practices](docs/working-practices.md)).

### Open decisions (for the ADR)

1. Tool: `just` (lean) vs `poe`.
2. `baseline` parallelism: it is deliberately parallel today (six suites at once, ≈ one
   scenario's wall-clock); `just` runs dependencies **sequentially**, so a parallel
   `baseline` needs shell `&`/`wait` in that one recipe, or we accept serial.
3. Fast-auto (`pre-commit` hook) + manual full `build`, keep the scoped rules, or a blend.

## 8. Improvement plan working approach

One change at a time: apply it, run the test(s) the change's scope calls
for, then propose a commit — behavioural and structural changes kept in
separate commits (see
[`docs/working-practices.md`](docs/working-practices.md)).

At the start of the review run the full baseline tests and then full mutation test.
If clear, for a file under review, add all lenses in the correct order to 
the task list before reviewing any files. Number each lens in the task list.

Then, once the task list is complete, for each lens, one at a time, review the
file through that lens and:
- Tell me the lens
- If no issues seen through that lens, say no issues (no explanation
  needed) and await the user's approval to proceed to the next lens.
- If changes are required, show me the before and after of the change you
  propose and await the user's approval to proceed.

Review the file *only* when its lens is the active one — and read it fresh at
that moment, along with any other file the lens needs (e.g. the production
source for the execution-flow lens). Do not read the whole file, nor any file
a later lens will need, up front. Each lens is a fresh pass: look at the file
through that lens alone, report, and only then move to the next.

Reading fresh at each lens is correctness, not tidiness. A lens reviews the
file's current state — which includes any change an earlier lens produced. A
read taken before those changes is stale, so a lens reviewing against it is
reviewing text that no longer exists. Re-read when the lens becomes active so
every pass sees what is actually there.

Reporting lens-by-lens in order is necessary but not sufficient — the
examination itself must be lens-at-a-time, not a single up-front sweep
re-narrated as separate lenses.

### Reviewing a test file

Review the file through each lens below in turn, confirming each one by
one — even where it needs no change. Most lenses are the conventions in
[`docs/architecture/conventions/test-conventions.md`](docs/architecture/conventions/test-conventions.md);
the last two are inferred from the reviewed exemplars.
Add each lens to your task list for easy tracking in the session.

Review the file through each lens below in turn and in the order below:

- Whole-story tests
- Test order follows the production code's execution flow
- Tests can be grouped in classes that express key variations in behaviour
- Test naming `test_should_<behaviour>` and each reads in context of its holding class
- MagicMock interrogation forms
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

## 9. Improvement plan

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
- [x] `auditor.py` (and `tests/test_auditor.py`)
- [x] `scorecard_results.py` (and `tests/test_scorecard_results.py`)
- [~] `claude_transcriber.py` (and `tests/test_claude_transcriber.py`) —
  interim mutation coverage added: the `varied-transcript` approval test took
  survivors 75 → 8 (the remaining 8 are equivalence mutants). Bringing it fully
  to standard is superseded by a ground-up rewrite — see ADR
  [0014](docs/architecture/decisions/0014-separate-claude-jsonl-translation-from-the-transcriber.md).
  Kept out of `source_paths` (the equivalence survivors can't be accepted yet).
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

### `Auditor.evaluate` should derive per-row status, not hard-code PASS

`Auditor.evaluate`'s success branch hard-codes `"status": "PASS"` for every
result row. It can, because that branch is reached only when `_failures_from`
returns empty — the all-pass case. The literal is a symptom: the Auditor
reimplements pass/fail branching instead of delegating to
`ScorecardResults.failures()` the way `Critic.evaluate` does. On success it
hand-builds an all-PASS `results` list; on any failure it returns `Failure(...)`
and bypasses `ScorecardResults` entirely.

The symmetric fix mirrors `Critic.evaluate`: evaluate each row once into a real
`PASS`/`FAIL` status, build `ScorecardResults(should=should, results=<those
rows>)`, then `match scorecard.failures()`. Then the status is derived per row,
never a literal, and both `evaluate` methods read alike.

This is a **behavioural** change, not a refactor: it changes what
`ScorecardResults.should` holds on the Auditor path (today
`_entries_from(should)`; Critic stores the raw `should`) and the `Failure`
payload shape, so it needs test updates. It is adjacent to the deferred
`ScorecardEntry` work above — do it as its own red-green.

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

## Review later: consider a delta from scene to scene

Each task's `scene/` is a full copy of the workspace end-state and also the
opening scene for the next task, so consecutive scenes duplicate most files
verbatim — building task 2's scene copies task 1's `pyproject.toml`, tests,
`.claude/settings.json`, and `uv.lock` unchanged, and only `src/conversion.py`
differs.

Consider holding each scene as a delta — only the files that changed from the
previous scene. A full scene is then materialised by copying the scenes in
order, each later scene's files layered over what is already there. This
applies to both roles a scene plays: the start (opening) scene for the next
task, and the reference (end-state) scene the critic judges against.

## Review later: move scene management to play

Scene setup currently lives in the spec test helper `_set_opening_scene_for`
(copying the previous scene into the workspace, filtering the previous task's
outputs like `transcript.md`). Materialising a scene, deciding what carries
into an opening scene, and the delta-from-scene idea above are framework work —
they belong in `play/`, not in a spec test helper. Move scene management into
`play/` so scenarios call it rather than reimplement it.

## Lowest priority: review whether the fake agent and auditor belong in the spec

The `FakeAgent` and `Auditor` were introduced to drive out the design of
`play` — they're framework machinery, and probably aren't useful for
validating the xdd skill itself (that's the real agent + critic's job). They
likely belong as their own example scenarios under `play/tests/`, exercising
`FakeAgent`/`Auditor` as framework features, which would let us remove them
from the xdd spec scenarios. Review whether the spec should run only the real
agent + critic, with the fake/auditor relocated to `play`'s own tests, their
appropriate home.
