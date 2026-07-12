---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0012 — Adopt path-source packages for cross-project code

**Status:** Accepted 

**NOTE:** the flat top-level module layout is superseded by [ADR 0021](0021-adopt-the-stagentic-namespace-for-shared-code.md); the rest stands.

## Context

`play/`, `spec/`, and the shared test helpers are separate bodies of code that
need to reference one another: the helpers are shared between `play` and `spec`,
and `play` is imported by `spec` (and is the embryo slated for extraction to its
own repo). The question this ADR settles is how cross-project code is shared.
Two specific forces drive it.

`play/` and `spec/` are separate pytest projects, each with its own `src/`,
`tests/`, `pyproject.toml`, and mutation gate. Shared *test* helpers — not
production code, not domain-specific — have accreted and duplicated across the
test files of `play/`:

- **matchers** (`matching`, `does_not`, `contain_string`, `contains_strings`)
  — currently `play/tests/matchers.py` (ADR
  [0011](0011-adopt-pyhamcrest-for-declarative-assertions.md)).
- **`case`** — a `pytest.param` wrapper that puts the id first — defined three
  times, in two different signatures: `def case(id, *values)`
  (`test_scorecard_results.py`, `test_scorecard_json_extraction.py`) and
  `def case(id, **named_values)` (`test_raise_if.py`).

Two problems follow. First, these helpers have no single home: they are
duplicated (and have already drifted, as the two `case` signatures show), and
nothing tests them. Second, they get **no mutation coverage**, and that gap is
structural, not incidental.

Mutation testing is part of doing the work (ADR
[0010](0010-adopt-mutation-testing-with-a-staged-rollout.md)). But mutmut
cannot mutation-test a helper that lives under `tests/`:

- mutmut only mutates files under **hardcoded** source roots — `.`, `src`,
  `source` (in `setup_source_paths`); the list is not configurable.
- Those roots determine the dotted key mutmut derives from each file's path, so
  `tests/matchers.py` is keyed `tests.matchers`.
- The tests import the helper as `matchers` (because `pytest`'s
  `pythonpath = ["src", "tests"]` puts `tests/` on the path), and mutmut records
  the covering test under that module name.
- The keys diverge — `tests.matchers` (path) vs `matchers` (import) — so every
  mutant of the helper is silently marked "no tests" and never checked.

`src/critic.py` avoids this only because `src/` *is* a recognised root: its key
`critic` matches its import. Adding a `tests/` helper to a `source_paths` list
does not help.

Second, `spec`'s scenarios import `play`'s framework code. Today that is a
relative `pythonpath` entry (`"../play/src"`), which breaks the moment `play`
is extracted and is invisible to the IDE — the same weakness as the helper
wiring.

The forces: one home for shared test utilities, with their own tests and
mutation coverage; a single `case`; cross-project reuse (`play`↔`spec` helpers,
and `spec` importing `play`); a sharing mechanism that survives `play`'s
extraction and resolves in the IDE; and working *with* mutmut's source-root
convention rather than against it.

## Decision

Adopt path-source packages as the mechanism for all cross-project code, and
create **`test_utilities/`** as the first such package — a peer project to
`play/` and `spec/`, with its own `src/`, `tests/`, and `pyproject.toml`.

- Shared helpers live in `test_utilities/src/` as top-level modules (e.g.
  `matchers.py`), imported as `from matchers import …`. Under the recognised
  `src/` root, mutmut keys them `matchers` — matching the import — so they are
  mutation-testable exactly like any production module.
  ([ADR 0021](0021-adopt-the-stagentic-namespace-for-shared-code.md) supersedes
  this flat layout: the helpers move under the `stagentic` namespace, imported as
  `from stagentic.test.matchers import …`, to avoid PyPI name collisions.)
- `test_utilities` carries its own mutation gate
  (`[tool.mutmut] source_paths = ["src/matchers.py", …]`), **permanently**.
  This retires the workaround of temporarily adding a test helper to another
  project's `source_paths`, which cannot work (see Context).
- **Wiring lands in two phases — each committed.**
  - *Phase 1 (`pythonpath`):* `play` and `spec` each add
    `"../test_utilities/src"` to their `[tool.pytest.ini_options] pythonpath`,
    sharing the helpers and getting them mutation-tested with minimal wiring.
    This is a stepping stone, not the destination: a relative path breaks once
    the projects are no longer siblings (so it does not survive `play`'s
    extraction), and the IDE cannot resolve a `pythonpath` entry.
  - *Phase 2 (standalone packages):* the shared and cross-imported code becomes
    installable packages, declared as dependencies.
    - `test_utilities` gains a build backend and ships its flat `src/` modules
      as top-level imports (`from matchers import …` unchanged), so it is
      installable without restructuring.
    - `play` becomes an installable package too — it is imported by `spec`, and
      it is the embryo that will be extracted to its own repository.
    - `play` and `spec` declare the dependencies via path sources
      (`[tool.uv.sources] test_utilities = { path = "../test_utilities" }`, and
      `spec` likewise on `play`), retiring the `pythonpath` entries. Each
      project keeps its own `pyproject.toml`, lockfile, and environment; there is
      no workspace.

  Standalone packages are chosen deliberately. A declared package dependency is
  what `play` carries across the repo boundary when it is extracted: the path
  source becomes a git or published source, with nothing structural to unpick.
  It is also what the IDE resolves natively — a packaged dependency lives in
  each project's environment, where editor and test runner both find it, which a
  `pythonpath` entry never achieves.
- Consolidate `case` into a single signature in `test_utilities`; the call
  sites adopt it.
- Initial scope: `matchers` and `case`. Domain-specific helpers
  stay where they are — `characteristics_for_all` and the `dummy` fixture in
  `play/`, and `spec`'s `inspector`/`agent` fixtures, `pytest_*` hooks, `_have`,
  and `_tree_diff`.

## Consequences

- Shared test utilities gain one home, their own tests, and mutation coverage —
  closing the structural gap that mutmut cannot mutate a `tests/`-located
  helper.
- Duplication goes away: one `case`, one `matchers`.
- Mutation config simplifies: helpers are permanent mutation targets in their
  own project, so no temporary, uncommitted `source_paths` edits during
  development.
- A third project to maintain: its own `pyproject.toml`, lockfile, lint, and
  test invocations. `COMMANDS.md` gains its commands; `CLAUDE.md` "Layout" gains
  the project; the test-conventions "lift the alias to `conftest.py`" guidance
  and the working-practices "add the file you're developing to `source_paths`"
  wording are revised to point at `test_utilities` for shared helpers.
- Phase 1's `pythonpath` wiring is explicitly temporary — light but
  unconventional, invisible to the IDE, and not extraction-safe; Phase 2
  replaces it with declared package dependencies.
- `play` becoming a package is a step toward its planned extraction: its
  dependency on `test_utilities` is already declared, so extraction only changes
  where that package is sourced from (a git or published source in place of the
  local path).
- Each project keeps its own lockfile and environment; there is no shared
  workspace environment. Cross-project code is present because it is installed
  (editable) as a declared dependency, not because a path entry points at a
  sibling's `src/`.
- Consolidating `case` forces choosing one signature; the call sites that used
  the other form change with it.

## Alternatives considered

- **Keep `matchers` in `play/tests/` and temporarily add it to `source_paths`
  for mutation.** Rejected: mutmut's hardcoded source roots (`.`, `src`,
  `source`) mean a `tests/`-located file's mutants never map to any test ("no
  tests") — it is not achievable, not merely awkward.
- **Move `matchers` to `play/src/`.** Rejected: misfiles test-only code as
  production, pulls it into `play`'s production mutation gate, and still gives
  `spec` no clean way to reuse it.
- **Relocate `matchers` to the `play/` project root (`.`) to hit mutmut's `.`
  convention.** Rejected: a tool-driven placement at the project root, still
  `play`-only, and with no home for the helpers' own tests.
- **Put the helpers in `conftest.py`.** Partial at best: `conftest` shares
  fixtures within a single project, not across `play`/`spec`, and gives neither
  mutation coverage nor a tested home for non-fixture helpers like `matchers`
  and `case`.
- **A uv workspace (single root, shared lockfile and environment).** Make
  `play`, `spec`, and `test_utilities` members under one root `pyproject.toml`
  sharing a single lockfile and environment — either keeping `pythonpath` or
  consuming the helpers as a workspace-member dependency (`{ workspace = true }`).
  Tried, then rejected: it is a monorepo arrangement that `play`'s planned
  extraction would have to unpick — a workspace member is not an independently
  installable dependency, so the wiring would be built now only to be reworked
  at extraction. Keeping `pythonpath` under the workspace still left the IDE
  unable to resolve the helpers (the env is shared, but nothing is declared or
  installed), and the single shared environment collapsed the per-project
  environments the projects otherwise keep independent.
