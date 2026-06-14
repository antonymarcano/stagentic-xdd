# Src conventions

Production code conventions for `play/src/` that should persist across refactors. A fresh contributor might be tempted to relax these to silence a warning or save a line; this document captures why each one is the way it is.

## Type hints on every public method parameter

Public method signatures hint every parameter with a concrete type (`Path`, `str`, `list[dict]`, `ClaudeCli`). Helpers may follow the same rule when their signature reveals contract details, but the public surface always does.

**Why:** a reader learns the contract from the signature without reading the body. `agent.py`'s `Agent.perform(self, *, task: str, working_dir: Path)` says everything about what `perform` consumes; `claude_session.py`'s constructor types its collaborators (`claude: ClaudeCli, transcriber: ClaudeTranscriber, home: Path`) so the dependency shape is self-evident.

**Avoid `Any`:** if you reach for `from typing import Any`, ask whether `dict`, `list`, or a concrete type would fit. The auditor's `should` is `list[dict]`, not `list[Any]` — the latter conveys nothing the bare container doesn't.

## Required vs optional: no `| None = None` defaults for test convenience

When the production contract always supplies a value, the signature reflects that — no `= None` default, no `Path | None`. Don't relax the contract to make unit tests easier to write; update the tests to pass the value (a `tmp_path`-backed fixture is enough).

**Why:** the `| None = None` default lies about the contract. A reader sees an optional parameter and assumes the code handles `None`; in reality the only caller passing `None` is a test that didn't want to bother. Requiring the value at the signature surfaces an omitted argument at call time (Python raises `TypeError`) rather than letting `None` propagate to a callback or an internal helper.

## Runtime guards for semantic preconditions the type system can't express

Add a runtime guard (`if not should: raise ValueError("scorecard must not be empty")`) when the semantic precondition can't be expressed in the type system. An empty list satisfies `list[dict]`; only the runtime guard catches the degenerate case.

**Why:** the guard surfaces a misuse rather than letting it silently no-op. `Auditor.evaluate` with an empty `should` would otherwise return `None` and look successful; the `ValueError` says "the call had no effect — that's not what you meant."

**When NOT to add one:** Python already enforces the misuse. Missing required arguments raise `TypeError`; wrong types are caught by linters/type-checkers. Don't duplicate language-level guarantees with runtime guards (and don't write tests for them; see `test-conventions.md`).

## Helper-function parameter order mirrors the call it makes

When a helper function calls another callable, its own parameter order matches the call's argument order. `_failures_from(content, working_dir, should)` calls `row["verify"](content, working_dir)` — the `(content, working_dir)` pair sits adjacent in both signatures.

**Why:** the helper's signature documents what it forwards to the call inside. Param ordering that breaks the call's pair (e.g. `_failures_from(content, should, working_dir)` with `verify(content, working_dir)` inside) forces a reader to mentally re-pair the arguments.

## IDE warning suppression with an inline rationale comment

When design intent overrides an IDE warning the type system can't settle, suppress the warning inline with a comment explaining why — the suppression directive and the rationale together, so the next reader meets the silence and its reason at once.

**Why:** silencing a warning without explanation leaves the next reader to re-derive the design intent. A bare suppression says "ignore this" without recording what the design knows that the inspection doesn't.

**When the type system already settles it, no suppression belongs.** `Auditor.evaluate` reads as "could be static" in isolation, but implementing the `Inspector` protocol fixes its signature by contract, so PyCharm doesn't raise the warning — a suppression there would silence nothing.

**Trigger to revisit:** when the reason no longer holds, drop the suppression — one that outlives its rationale hides a warning that may now be real.

## Private functions follow the order their calls appear

Private module-level functions in a file are defined in the order their calls *appear* in the public method, reading top-to-bottom and left-to-right. Depth-first: each helper appears, then the helpers whose calls appear in its body right after it. Constants used only by one helper sit just before that helper.

For a nested call such as `_entries_from(_failures_from(...))`, the outer call is read first, so `_entries_from` is defined before `_failures_from` — even though `_failures_from` *executes* first as the inner argument. Order by what a reader meets first, not by execution order.

**Why:** a reader encounters the definitions in the same order they encounter the calls reading the public method, so following the code doesn't require jumping around. When a helper is reused (called from multiple sites), its position is fixed by its *first* appearance.

## Orchestrator methods read at a single level of abstraction

The body of a public method that orchestrates helpers (e.g. `Critic.evaluate`, `Auditor.evaluate`) reads as a sequence of declarative steps at the same level of abstraction. Each statement is a helper call that names *what* the step does; no inline mechanism (variable assignments mid-flow, if-guards, list comprehensions) sits alongside the calls.

**Why:** the orchestrator says *what* the subject does step by step. A mix of declarative calls and inline mechanism forces a reader to switch levels mid-method — the helper calls describe intent, the inline mechanism describes *how*. Extracting the mechanism into a helper restores the single-level reading.

## Naming-suffix vocabulary for private helpers

Private helper suffixes carry consistent meaning:

- `_X_in(collection)` — return the X's *in* the given collection (`_duplicated_in`, `_problems_in`, `_failures_in`, `_unaccounted_in`).
- `_X_for(inputs)` — return the X accountable *for* the given inputs (`_unaccounted_for`).
- `_X_of(thing)` — return X derived *of* the thing (`_names_of`).
- `_X_from(source)` — return X extracted *from* the source (`_rows_from`, `_statuses_from`).

**Why:** a consistent suffix vocabulary lets the reader infer the helper's shape from its name. A new helper that breaks the vocabulary (e.g. `_problems_by(...)` when `_problems_in(...)` would fit) makes the reader pause to figure out what's different.

## Kwarg-style helpers compose into prose at the call site

When a helper takes more than one configuration parameter — typically a detector, an exception type, and a formatter — make the configuration kwargs keyword-only and name them so the call site reads as English. `_rows_unless(result, has_problem=_malformed, raising_error=ValueError, with_message=_formatted_malformed)` reads as *"rows unless [it] has_problem, raising_error, with_message"*.

**Why:** a prose-reading call site documents the intent at the point of use. A positional alternative (`_rows_unless(result, _malformed, ValueError, _formatted_malformed)`) saves keystrokes but forces the reader to remember the slot order or open the helper's `def`. The keyword-only signature (`*` separator) enforces the readability — callers can't accidentally fall back to positional and lose the prose.
