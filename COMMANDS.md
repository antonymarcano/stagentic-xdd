# Commands

Key developer commands for this repo. All commands run from the repo root.

## Linting

```
uv run --directory play ruff check .
uv run --directory spec ruff check .
uv run --directory test_utilities ruff check .
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

### `test_utilities/` tests

```
uv run --directory test_utilities pytest
```

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

### `spec/` scenarios with critic (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic
```

### `spec/` scenarios with real agent and auditor (require `claude` CLI)

The real agent defaults to the critic; this opts back in to the auditor.

```
uv run --directory spec pytest tests --agent=real --inspector=auditor
```

## Mutation testing

Mutates the files in `source_paths` (`play/pyproject.toml`) against the fast
unit lane. See ADR [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md).

`test_utilities` is mutated the same way against its own `source_paths`
(`test_utilities/pyproject.toml`) — swap `--directory play` for
`--directory test_utilities` in the commands below.

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
