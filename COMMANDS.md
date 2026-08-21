# Commands

Key developer commands for this repo. All commands run from the repo root.

**Run each command exactly as written — no added filtering, piping, or scaffolding**
(`| grep …`, `; echo "EXIT=$?"`, `> file 2>&1`, and the like). Filtering risks hiding
the output you actually need, forcing a second run — and several commands here are
expensive (real-agent runs, mutation sweeps), so a wasted re-run costs real time and
money. Appending `; …` or `| …` also turns an allowlisted command into a compound one,
which prompts for permission (each part is checked separately). Run it whole, read all
of it, then decide.

## Linting

```
uv run --directory play ruff check .
uv run --directory spec ruff check .
uv run --directory stagentic-test ruff check .
```

## Tests

### `play/` unit tests

```
uv run --directory play pytest tests -m "not contract and not integration"
```

### `play/` integration tests (require `claude` CLI)

```
uv run --directory play pytest tests -m integration
```

### `play/` contract tests (require `claude` CLI)

```
uv run --directory play pytest tests -m contract
```

### `play/` full suite (require `claude` CLI)

```
uv run --directory play pytest
```

### `stagentic-test/` tests

```
uv run --directory stagentic-test pytest
```

> **Spec scenarios run in parallel by default** — `spec/pyproject.toml` sets
> `addopts = ["-n", "auto"]` (pytest-xdist), so every `spec` command below
> distributes scenarios across workers. To run serially — to debug, or to read
> un-interleaved output — append `-n0`.

### `spec/` scenarios

```
uv run --directory spec pytest tests
```

### `spec/` scenarios with critic, preserving artefacts (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic --.artefacts-dir .artefacts
```

### `spec/` scenarios with real agent (require `claude` CLI)

The real agent is judged by the critic by default; pass `--inspector=auditor`
to override.

```
uv run --directory spec pytest tests --agent=real
```

### `spec/` scenarios with real agent, preserving artefacts (require `claude` CLI)

```
uv run --directory spec pytest tests --agent=real --.artefacts-dir .artefacts
```

### Repeated real-agent runs (interim)

A scenario judged by the critic passes or fails probabilistically, so one run
establishes nothing. The scripts in [`scripts/`](scripts) run a scenario many times
and tally the outcomes. Interim tooling — the framework version is NEXT.md §4.

Invoke every one from the **repo root with the relative path**. That matches the
permission allowlist (e.g. `Bash(bash scripts/verify-runs.sh*)`) and runs without a
prompt; an absolute path does not match and will prompt.

They share two conventions:

- `artefacts-dir` passed to a **runner** is relative to `spec/`, so
  `.artefacts/<name>` lands at `spec/.artefacts/<name>`. Passed to `tally.sh` it is
  relative to the **repo root**, so the same batch is `spec/.artefacts/<name>`.
- Runs **accumulate** in a dir. Name a fresh subfolder per batch rather than
  creating adjacent `.artefacts-*` dirs — everything stays under `.artefacts`.

#### Verify one wording at scale

Runs the live working tree N times, tallying after each batch. Use
`--stop-on-fail` to gate (halt at the first failing batch); omit it to measure a
rate over all batches.

```
bash scripts/verify-runs.sh [--stop-on-fail] <artefacts-dir> [batches] [runs] [pytest-node]
```

Defaults: `batches=10`, `runs=10`, and the whole red-green-commit file
(`tests/test_red_green_commit.py`) — so each run covers every scenario in it.
Exits 0 when every run is clean, 1 when a run failed, 2 when there was nothing to
evaluate.

#### Compare two wordings

Alternates arm A and arm B wave by wave, swapping the target file before each
arm's batch and restoring it on any exit. Alternating cancels the load/latency
drift that would otherwise land entirely on whichever arm ran second.

```
bash scripts/compare-wordings.sh <artefacts-dir> <fileA> <labelA> <fileB> <labelB> [waves] [runs]
```

Set `STOP_ON_A_FAIL=1` when arm A is a known-clean control, so a failure in it
stops the run as a contaminated window; leave it unset when arm A is a baseline
expected to fail sometimes. `NODE` and `TARGET` override the scenario and the file
being swapped (default the xdd `SKILL.md`).

#### One batch, or one tally

The primitive each runner is built from, and the reader:

```
bash scripts/run-batch.sh [pytest-node] [count] [artefacts-dir]
bash scripts/tally.sh [characteristic] [artefacts-dir]
```

`tally.sh` reports full-pass, a per-characteristic failure breakdown, skill-load
checked two independent ways, and the count for one named characteristic
(defaulting to the write-order one). It tallies every run currently in the dir —
cumulative across batches.

#### Significance

Whether two measured rates differ by more than chance:

```
bash scripts/fisher.sh <a> <b> <c> <d>
```

For the 2x2 table `[[a, b], [c, d]]` — e.g. `a`=arm-A fails, `b`=arm-A passes,
`c`=arm-B fails, `d`=arm-B passes.

**When a batch deviates from the established rate**, check
[status.claude.com](https://status.claude.com/) for an incident (degraded
capacity, model routing, elevated errors) before attributing the shift to a code
or guidance change — an upstream incident can masquerade as one.

### `spec/` scenarios with critic (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic
```

## Run artefacts

Real-agent runs archive their workspace (transcript, critique, source, tests)
under `spec/.artefacts/` — gitignored via `**/.artefacts`. `--.artefacts-dir`
takes a path **relative to the spec project** (because `uv run --directory spec`
runs there), so `.artefacts` lands under `spec/`.

Keep separate runs apart with a **subfolder per batch under `.artefacts`, named
at run time**: `--.artefacts-dir .artefacts/<batch-name>` (e.g.
`.artefacts/experiment/<wording>`). Everything stays under `.artefacts`; do
**not** create adjacent `.artefacts-*` sibling directories. Point
`scripts/tally.sh` at a subfolder to tally that batch, or at a
parent folder to tally every batch beneath it cumulatively.

## Mutation testing

Mutates the files in `source_paths` (`play/pyproject.toml`) against the fast
unit lane. See ADR [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md).

`stagentic-test` is mutated the same way against its own `source_paths`
(`stagentic-test/pyproject.toml`) — swap `--directory play` for
`--directory stagentic-test` in the commands below.

### Focus one file (during TDD or review)

```
uv run --directory play mutmut run "<module>*"
```

`<module>` is the bare module name — the prefix mutmut gives its mutant
names, not a path or filename: no `src/`, no `.py` (e.g. `critic`, never
`src/critic.py`).

### Full set (before work is 'done')

```
uv run --directory play mutmut run
```

### Reading the result

The result is the command's **exit code**: `0` means every mutant was
killed, non-zero means at least one survived. Read that — don't pipe the
run through `grep`, which can filter out the survivor lines you need and
risk a false all-clear, and don't run the full set just to `grep` it. Run
the focused command above for per-file feedback; reserve the full set for
the regression gate.

Only when the exit code is non-zero, inspect the survivors:

```
uv run --directory play mutmut results
uv run --directory play mutmut show <mutant>
```

### Clean up after the run

`mutmut` has no cleanup of its own (3.6.0) — it leaves a `mutants/` tree under
`play/`, a verbatim copy of `src/` and the test suite where it also stores its
results. Once the run is complete and any survivors inspected, remove it:

```
rm -rf play/mutants
```

Removing it when done keeps the next run from replaying stale cached results,
and stops IDE duplicate-code inspections flagging the copied test files as
duplicates of the originals.
