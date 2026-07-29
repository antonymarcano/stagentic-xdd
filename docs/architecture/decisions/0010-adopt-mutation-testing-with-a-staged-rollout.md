---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0010 — Adopt mutation testing with a staged rollout

**Status:** Accepted

## Context

A passing test suite confirms the code does what the tests check — not that
the tests would *notice* if the code changed. A test can pass while pinning
nothing: an assertion that merely duplicates a collaborator's own tests, or a
behaviour pinned in only one place that a refactor could silently drop. The
recent review of `critic`'s tests surfaced exactly this.

This matters acutely for the agentic TDD work this repo exists to build. An
agent told to "use TDD" routinely writes more code than the failing test
demands — behaviour the tests never required and therefore never pin. Mutants
emerge wherever a change to the code exceeds the need described by a failing
test. The result looks test-driven but isn't: an *illusion of test-driven
code*, where code can change in material ways without a single test failing.
Every such living mutant is an opportunity for a future change to introduce a
bug the tests won't catch.

Background and motivation: Antony Marcano, "Mutants in the Machine: The AI
Illusion of Test-Driven Code" —
https://ideas.riverglide.com/mutants-in-the-machine-the-ai-illusion-of-test-driven-code-37d623642486

## Decision

Adopt mutation testing with `mutmut`, rolled out one file at a time. The
practice is in force now; the staging is the *scope* — `source_paths` starts at
a single file and grows as each is brought to standard and its coverage
accepted, never switched on for the whole codebase at once.

Tooling — mutmut 3.x:

- `source_paths` in `[tool.mutmut]` (in `play/pyproject.toml`) is the
  accumulating set of files under mutation. A file is added when it is in the process of being brought
  to standard; the config is committed only once its mutation coverage is
  acceptable. Committing a file into `source_paths` declares its coverage a
  defended baseline.
- Test selection is pinned to the fast unit lane via
  `pytest_add_cli_args_test_selection = ["-m", "not contract and not integration"]`
  — mutants must not trigger real-CLI calls.

Commands:

- **Focus one file** — `mutmut run "<file>*"` — fast feedback on a single file.
- **Full set** — `mutmut run` — every file in `source_paths`.
- `mutmut results` and `mutmut show <id>` inspect survivors.

### In force now

Scoped to the files in `source_paths`:

- **During TDD — on green, before committing.** Run a focused
  `mutmut run "<file>*"` on the file just developed. A surviving mutant means
  the implementation did more than the failing test demanded; dial the code back
  to only what the test requires, then commit. This is triggered by doing TDD —
  including new components introduced *during* the refactoring pass — not by any
  phase boundary.
- **Reviewing an existing file during the pass** — run the same focused
  `mutmut run "<file>*"` as a read-only signal; survivors are coverage gaps to
  weigh and act on.
- **Before work is 'done'** — the full-set `mutmut run` must be clean, or every
  survivor a documented accepted-mutation. `source_paths` lists only files whose
  coverage we have already accepted, so this gate defends those baselines
  against regression; it never blocks on unvetted code. It applies from the
  first file on the list (now), not after the pass completes.

### Deferred

- **CI automation** of the full-set gate — for now it is a manual step before
  declaring work done.
- **The accepted-mutation mechanism** — a way to record, against specific code,
  that a surviving mutant is intentionally accepted (an equivalence mutant, or a
  redundancy deliberately kept). Until it exists, accepted survivors are tracked
  by hand, and a *hard automated* gate waits on it so an accepted survivor does
  not fail the build forever. No file in `source_paths` has such a survivor yet.

## Consequences

- "Well-tested" becomes measurable per file rather than a matter of judgement.
- A committed `source_paths` entry turns a later survivor into a regression
  signal — coverage that was defended has been lost.
- **Equivalence mutants** — survivors for which no failing test is derivable —
  are unavoidable; handling them is the deferred accepted-mutation mechanism.
- mutmut 3.x materialises a `mutants/` working copy; it is gitignored.
- The full-set run grows slower as `source_paths` accumulates — acceptable for
  a done-gate, which is why the focused run exists for iteration.
- Mutation testing is part of doing work now, not a future gate.
  `docs/working-practices.md` should carry both practices (focused while
  TDD'ing/iterating; full-set clean-or-accepted before 'done'), and
  `CLAUDE.md`'s "Before any commit" guidance should include the full-set gate.
  Both are follow-on edits to this ADR.
- Pinning to the fast lane means results say nothing about
  contract/integration-covered behaviour — a deliberate scope limit.

## Alternatives considered

- **No mutation testing — rely on review judgement.** The status quo. Review
  cannot reliably tell a behaviour-pinning assertion from a vacuous one; that
  is exactly what the `critic` test review surfaced.
- **Run mutation across everything at once.** Noisy, slow, and untargeted
  while files are still being brought to standard. The per-file,
  accumulate-as-you-go approach matches the pass.
- **Hard-gate from day one** — fail the build automatically on any survivor.
  Rejected for now: without the accepted-mutation mechanism an intentionally
  accepted survivor would fail the build forever. The full-set gate runs as a
  manual clean-or-accepted check until that mechanism (and CI automation) lands.
