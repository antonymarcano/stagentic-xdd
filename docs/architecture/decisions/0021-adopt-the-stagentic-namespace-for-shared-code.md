---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0021 — Adopt the `stagentic` namespace for shared cross-project code

**Status:** Accepted

## Context

[ADR 0012](0012-adopt-path-source-packages-for-cross-project-code.md) created
`test_utilities` as a path-source package and shipped its helpers as flat
top-level modules — `src/cases.py`, `src/matchers.py`, imported as `from cases
import case` and `from matchers import matching`. That layout was chosen so the
package was "installable without restructuring"; the collision cost of the
generic names was not yet in view.

Two forces are now in view that were not when 0012 was decided:

- **Collision.** `cases` and `matchers` are generic names owned by unrelated
  packages on PyPI. If a consumer's dependency tree pulls in a PyPI `cases`, it
  shadows the helper and `from cases import case` resolves to the wrong package —
  the importing suite errors on collection. A bare `cases` also gives an IDE
  nothing to map back to its distribution, so it flags the import as an
  undeclared requirement. The distribution name `test_utilities` is itself
  generic, carrying the same risk once published.
- **Reuse across stagentic projects.** These helpers are meant to be reused
  across multiple stagentic projects and will likely extract to their own repo,
  importable into any project. A layout that only fixes the modules in isolation
  leaves each future sibling (`play`, `spec`, others) its own unrelated
  top-level import, with no shared family root — so extraction and reuse would
  churn imports a second time.

## Decision

Adopt **`stagentic`** as a shared namespace root for cross-project code, and
home the shared test helpers under it as the first member.

- **`stagentic` is a PEP 420 implicit namespace package** — no `__init__.py` at
  the `stagentic/` root — so each separately-distributed package contributes its
  own subpackage without any one distribution owning the root. This is the
  idiomatic layout for a family of related distributions (e.g. `google.cloud.*`,
  `azure.*`). A future sibling like `stagentic.play` ships under the same root
  with no churn to the helpers.
- **The test helpers become `stagentic.test`**, imported as `from
  stagentic.test.cases import case` and `from stagentic.test.matchers import
  matching`. The name follows the `django.test` precedent — a package of helpers
  for *writing* tests, distinct from a project's own test suite. `stagentic.test`
  is a regular package (its own `__init__.py`); only the `stagentic/` root is a
  namespace.
- **The distribution is named `stagentic-test`** (hyphen dist → dotted import,
  the conventional split). `play` and `spec` update their `[tool.uv.sources]`
  key from `test_utilities` to `stagentic-test`.
- The mutmut `source_paths` follow the files to
  `src/stagentic/test/{cases,matchers}.py`; they remain permanent mutation
  targets.

This **amends** [ADR 0012](0012-adopt-path-source-packages-for-cross-project-code.md):
the flat-layout sub-choice is reversed. The path-source packaging mechanism ADR
0012 established — a peer project consumed via an editable path source — is
unchanged.

## Consequences

- Imports are collision-proof and self-documenting: `stagentic.test.cases` names
  its origin and cannot be shadowed by an unrelated top-level module.
- The shared root is future-proof: when `play` extracts and publishes, it ships
  under `stagentic.*` with no churn to the helpers. (`spec` consumes the helpers
  but is not itself published.)
- The project directory and distribution rename from `test_utilities` to
  `stagentic-test`, matching the name it will carry as its own repo. `play` and
  `spec` update their path-source key and dependency name.
- Every import site moves in lockstep — `play` and `spec` tests, and the helpers'
  own tests — to `from stagentic.test.… import …`. A one-time mechanical
  migration, verified green by the existing suites.
- The current-state docs — `test-conventions.md` (import convention),
  `COMMANDS.md` and `working-practices.md` (project paths), and ADR 0011's
  `matching` example — update to the namespaced import and `stagentic-test`
  paths. ADR 0012 carries a note that 0021 supersedes its flat-layout choice.
- The focused mutmut filter gains the dotted prefix (e.g. `stagentic.test.cases`).
- Naming trade-off accepted: by the `django.test` precedent, `stagentic.test`
  can read as "stagentic's own test suite" rather than "helpers for writing
  tests." Accepted for the brevity and the precedent; `stagentic.testing` was the
  unambiguous alternative.

## Alternatives considered

- **Namespace under the single package** (`test_utilities.cases`). Collision-proofs
  the modules and names their distribution, but shares no root with future
  siblings and keeps the generic `test_utilities` distribution name — forcing a
  second import churn when the siblings extract and publish.
- **`stagentic.testing`** (the `numpy.testing` / `pandas.testing` precedent).
  Unambiguously "helpers for testing," avoiding the "own test suite" reading, but
  longer in every import. We chose the shorter `django.test` framing.
- **Rename to less-generic top-level names** (e.g. `tu_cases`). Still top-level,
  so still collision-prone in principle, still no shared root, and the import
  still doesn't name its distribution.
- **Keep the flat layout.** Rejected: the collision is silent until a transitive
  dependency introduces a PyPI `cases`/`matchers`, and the IDE misclassification
  is present today.
