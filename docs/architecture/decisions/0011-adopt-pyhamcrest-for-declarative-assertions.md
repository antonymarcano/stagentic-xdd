---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0011 — Adopt PyHamcrest for declarative test assertions

**Status:** Accepted

## Context

Assertions in the test suite arise in two places, today served by two unrelated
mechanisms:

- Inside test-double call assertions — e.g. the arguments to `ClaudeSession.run`
  checked via `assert_called_once_with`, which compares expected against actual
  with `==`. Matching beyond exact equality means either `ANY` (which asserts
  nothing) or pulling the argument back out of `call_args.kwargs` and writing a
  run of bare `assert fragment in actual` lines.
- Inline — ordinary `assert` statements over return values and state.

No single assertion vocabulary serves both. The `==`-based call assertions
cannot use a richer matcher, and the inline asserts share nothing with them, so
the same kind of check — a substring, a subset of a mapping, an element of a
collection — is written differently, or not at all, depending on where it is
needed.

The primary force is reusability: one matcher vocabulary usable in both
test-double call assertions and inline assertions, applied consistently, and
broad enough to cover most of the ways — and the types — that need asserting on
(strings, collections, mappings, objects, and their composition) rather than a
one-off helper per case. A secondary benefit, and a stated preference, is that
such assertions read at the level of intent.

The obstacle for the call-assertion case: `assert_called_with` compares with
`==`, and a plain matcher object is not consulted because equality defaults to
identity. A matcher has to be bridged into `==`.

## Decision

Adopt **PyHamcrest** as a test dependency and use its matchers for assertions
across the test suite, starting with `play`.

- For test-double call assertions, wrap matchers with PyHamcrest's
  `match_equality`, whose `__eq__` delegates to the matcher's `matches()` — so
  Hamcrest matchers work inside `assert_called_once_with` while keeping its
  "called exactly once" check. This is a documented PyHamcrest use case for
  non-Hamcrest-aware libraries such as `unittest.mock`.
- For other assertions, use `assert_that(actual, matcher)`.
- Alias `match_equality` as **`matching`** so the call site reads at intent:
  `prompt=matching(all_of(contains_string(...)))`. The alias lives in a small
  shared test module (`stagentic-test`, `src/stagentic/test/matchers.py`),
  imported as `from stagentic.test.matchers import matching`.

## Consequences

- One matcher vocabulary now spans test-double call assertions and inline
  assertions, the same matchers reused across both — the primary aim.
- A new test dependency (PyHamcrest) in each project's `dev` group as it adopts
  the style. It is actively maintained and released.
- `ANY` placeholders are replaced by real matchers, so call assertions actually
  constrain every argument; the `call_args.kwargs` pull and the repeated
  `in` lines disappear into one matcher tree.
- Failures render through the matcher's own description, so the message states
  what was expected.
- Assertions read at the level of intent (a stated preference).
- Contributors must learn the Hamcrest matcher set, and a `matching(...)`
  wrapper sits between the test and the call assertion.
- `matching(...)` objects are matchers, not values — their `==` means "matches",
  meaningful only in a comparison/argument slot (the same contract as `ANY`).
- This does not conflict with ADR 0001. "Vanilla pytest" there means not
  adopting a BDD/Screenplay DSL to express scenarios; an assertion library is
  orthogonal to that.

## Alternatives considered

- **`callee`** — purpose-built matchers for `unittest.mock` whose `__eq__` drops
  straight into `assert_called_with`. Rejected: unmaintained — last release
  2019 (0.3.1), classifiers stop at Python 3.7, open issues and PRs unanswered;
  the repo runs Python 3.12.
- **Hand-rolled `__eq__` matchers** (e.g. a `StringContaining`, or our own
  `matching` bridge over a matcher's `matches()`). Works with zero dependencies,
  but reinvents `match_equality` and commits us to growing and maintaining our
  own matcher library. Rejected in favour of the maintained, official tool —
  while keeping the `matching` name as a thin alias.
- **Keep the status quo** (`ANY` + `call_args` pull + bare `assert in`).
  Rejected: `ANY` asserts nothing, and the pattern reads below intent.
- **`assert_that` for mock calls without `match_equality`.** Not possible —
  `assert_that` calls `matches()`, but mock checks call arguments with `==`,
  never `matches()`; `match_equality` is exactly what closes that gap.
