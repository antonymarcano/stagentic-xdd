# Commands

Key developer commands for this repo. All commands run from the repo root.

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

### 10× real-agent batch (interim — superseded by the N× gateway in NEXT.md)

Runs the real-agent scenarios 10× at 10-way concurrency, staggering each launch by
100ms — the shortest stagger that avoids the archive copytree race under parallel
runs (100ms clean at 30 runs; 50ms flakes ~2/30). Keep it one line: a mid-command
newline splits the loop body and runs `pytest` without its flags.

```
cd /workspace/stagentic-xdd && for r in $(seq 10); do uv run --directory spec pytest tests --agent=real --.artefacts-dir .artefacts & sleep 0.1; done; wait
```

It launches the runs but does not tally results — read each run's outcome from its
own output.

### `spec/` scenarios with critic (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic
```

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
