# Test conventions

Conventions for tests in this repo — follow them when writing or changing tests. Each rule's **Why** explains what it guards, so it isn't naively "simplified" away.

## Test naming: `test_should_<behaviour>`

Test methods are named `test_should_<behaviour>` — a behavioural claim read together with the class that holds it, which names the subject (see *Test names read in context of their holding class*). The behaviour describes what the subject does or does not do; the subject itself stays out of the method name. For example `TestCritic › test_should_raise_when_the_scorecard_is_empty` reads as "the critic should raise when the scorecard is empty", and `TestSuccess › test_should_carry_its_value` as "a success should carry its value".

**Why:** the test name reads as a behavioural claim, not as a description of the method called or the mechanism. A reader scanning the file sees what the code *does*, not which method is invoked.

## Test order follows the production code's execution flow

Tests inside a `TestX` class are ordered to mirror the execution flow of the production method under test: precondition guards first, then the mechanism (what the method does internally), then the outcomes (happy path, then unhappy path).

**Why:** a reader walking the file in order encounters tests in the same direction the production code runs — guard checks first, then the work, then the results. The file reads as a sequence of "here's what happens next".

## Whole-story tests

A **whole-story test** pins *everything the subject does* — such as every call to every collaborator, in one test. Per-property tests drill into smaller specific facts the whole-story test covers. The whole-story test may be written first or last (the latter allowing for the code to be built up one test at a time).

**The whole-story test shows the subject's distinguishing outcome.** When the subject's purpose is to dispatch a call to a collaborator (e.g. `ClaudeSession.run`), the whole-story test shows that call going through. When the subject's purpose is to raise — to assert, to signal a failure — the whole-story test shows it raising, because without the raise the test stops short of what the subject *does*.

**Shape:** pin the composed collaborator interaction exactly via `==` / `assert_called_once_with` (see *Pin exact composed output once via `==`*); slots whose check isn't plain `==` carry a matcher via `matching(...)` (see *Assertion vocabulary*). One example per property is enough in the whole-story test itself — the second example for each property comes from a sibling per-property test (see companion rule below).

**Position:** the test illustrating the scope's *primary behaviour* leads its containing class — the behaviour a reader most needs to see first to grasp what the subject is for. The primary outcome class leads, the secondary outcome follows. Remaining per-property tests (that do not change the outcome) follow in execution-flow order (*Test order follows the production code's execution flow*).

Outcome and phase groupings can combine: outcome classes (`TestPasses`, `TestFails`) frame the file; phase classes (`TestBuildsPrompt`, `TestCallsSession`, `TestParsesResponse`) sit in between in play order; `TestErrors` trails as the exception paths.

**Companion rule for per-property tests:** when a whole-story test exists, per-property tests for value-flow properties may collapse from parametrised (≥2 cases) to a single example — provided that example uses a value *different* from the whole-story test's. The pair (per-property test + whole-story test) supplies the ≥2 examples needed for mutation coverage (see *Parametrise value-flow tests over ≥2 cases with `ids`*). If the values match, the second example evaporates.

**Don't fragment into one test per fact.** When a whole-story test exists, per-property tests don't earn their place by virtue of being possible — they earn their place when value, presence, or absence alters behaviour (see *Pin exact composed output once via `==`*). Fragmenting a whole-story test into one test per fact loses the integrated narrative the whole-story test conveys.

## Test names read in context of their holding class

A test method's name reads together with the class that holds it, as `class › method`. The method drops the words its holding class already carries and uses the implicit-subject `test_should_…` form, letting the class supply the subject. This refines *Test naming* (above): the subject the holding class names leaves the method name. It applies to every test, whichever class holds it — the top-level subject class or an inner phase/outcome class.

How much the method name carries depends on how much its holding class carries:

- **Under the subject class** (`TestFakeAgent`) the class names only the unit under test, so the method keeps the full behaviour it describes — it just doesn't repeat the unit. The whole-story test `TestFakeAgent › test_should_run_the_task_script_and_make_the_transcript_available` is long because its holding class carries little, not because it is exempt from the rule.
- **Under a phase or outcome class** (`TestRunsScript`, `TestReturnsTranscript`) the class names a phase or outcome as well, so the method sheds those words too:

```text
TestRunsScript        › test_should_run_the_named_task
TestReturnsTranscript › test_should_be_wrapped_in_success
```

not `test_named_task_script_should_run_in_the_working_directory` (the class already says "script") or `test_transcript_should_be_returned_wrapped_in_success` (the class already says "returns the transcript").

**Keep the word that names what the test uniquely pins; trim only what the holding class or a sibling already covers.** `test_should_run_the_named_task` keeps "the named task" because routing by name is what distinguishes it from the whole-story test; it drops "in the working directory" because the whole-story test already exercises the working directory, so naming it here would foreground a shared property over the distinguishing one.

**Why:** the file and the IDE's test tree both present the method beneath its holding class, so the class name is always in view. Repeating it in the method name adds noise; leaning on it spends the method name's words on what the test actually distinguishes.

## Per-property test layout: relevant kwargs at the top

In per-property tests, lay out multi-line kwarg blocks so the relevant slots sit at the top of each call (constructor, method call, `assert_called_once_with`). Irrelevant slots go below. Bundling adapts to the counts so the top stays focused.

**1 relevant + ≥1 irrelevant** — relevant alone on top; irrelevants bundled on a single line below:

```python
ClaudeSession(
    transcriber=transcriber_spy,      # relevant — alone on top
    claude=dummy, home=dummy,         # irrelevant — bundled below
)
```

**≥2 relevant + 1 irrelevant** — relevants bundled together on top; the lone irrelevant on its own line below:

```python
ClaudeSession(
    transcriber=transcriber_spy, home=home,   # relevant — bundled on top
    claude=dummy,                              # irrelevant — alone below
)
```

Apply the same shape at every kwarg block in the test — constructor, method call, `assert_called_once_with`.

**Why:** relevant data at the top signals what the test is about; bundling keeps the top concise.

**Whole-story tests are exempt** — they follow production signature order. They aren't focused on one slot, so there's no "relevance-first" to express. See *Whole-story tests*.

## Explicit no-raise via `does_not_raise`

When a test asserts that the subject does *not* raise — typically the pass scenario where the subject completes silently — wrap the call in `does_not_raise()` from `contextlib.nullcontext`:

```python
from contextlib import nullcontext as does_not_raise

with does_not_raise():
    Critic(session=session_stub).evaluate(...)
```

The context manager does nothing at runtime — pytest would still fail the test if an exception leaked through without it. But the line reads as the assertion: the reader sees `with does_not_raise()` and knows the behavioural claim. Without it, the claim is only inferable from the absence of `pytest.raises`.

**Why:** the pass outcome is a behavioural claim in its own right, on par with the raise scenarios. Making it explicit puts the two claims on the same footing.

The alias starts in the test file; lift it to `conftest.py` when a second file needs it.

## Write parametrise rows with `case`

Parametrised rows use the shared `case` helper (`from stagentic.test.cases import case`) rather than a bare `pytest.param` or tuple. `case(scenario_name, **named_values)` takes the scenario name first — so the id leads each row, even though `pytest.param`'s id is positionally last — and takes its values as **keyword arguments only**; there is no positional-values form. Name each value for the `parametrize` argname it feeds:

```python
@pytest.mark.parametrize("agent_response", [
    case(
        "prose-before-json",
        agent_response='...',
    ),
    case(
        "code-fenced-json",
        agent_response='...',
    ),
])
```

**Why:** the named value at the call site makes which value maps to which test-method argument obvious, instead of the reader matching positions against the `parametrize` header; the id leading the row keeps the case name in view.

`case` is homed in `stagentic-test` (`src/stagentic/test/cases.py`); import it rather than redefining it per file. **The only exception is `case`'s own tests in `test_cases.py`** — they can't use `case` to exercise `case`.

## Parametrise value-flow tests over ≥2 cases with `ids`

When a test asserts that a value passed in flows through to a destination, parametrise it over at least two cases — each labelled with an id so the case name leads the row. A single hard-coded literal could pass coincidentally if the production code hard-coded the same literal.

**Shape:** one `case` row per example (see *Write parametrise rows with `case`*), each labelled with an id so the case name leads the row:

```python
@pytest.mark.parametrize("agent_response", [
    case("prose-before-json", agent_response='...'),
    case("code-fenced-json", agent_response='...'),
])
```

**Why:** the test asserts a behaviour (the value reaches its destination), not a specific value. Two cases prove the value is general; one case proves only that one specific value works.

**When this doesn't apply:** structural assertions that don't carry a value — e.g. "no exception raised when all checks pass" or "the path is under `.claude/projects`" — are correctly exercised with a single example, because the property isn't "this value flowed through" but "this structural fact holds."

The two cases may instead be split across a whole-story test and a per-property test — see *Whole-story tests*.

## Don't test Python's own enforcement

Tests should cover behaviour the code *chooses*, not behaviour Python provides for free. Don't write tests whose only purpose is to verify a missing required keyword argument raises `TypeError`, a wrong type raises an `AttributeError`, or similar language-level guarantees.

**Why:** by that logic every signature would need a test for its required-vs-optional status and every type hint would need a test for its enforcement. The tests would balloon to document Python rather than the code. Runtime guards the code *adds* (e.g. `if not should: raise ValueError`) DO warrant tests — those are choices.

**Exception — pinning an arg deliberately made required.** When changing a parameter from optional to mandatory is itself the work, a single test asserting that omitting it now raises `TypeError` is warranted: it makes the decision explicit and checked, so a later silent re-loosening (a re-added `= None`) fails a named test rather than slipping through. This stays narrow — it's for an arg whose optionality was a live decision, not a licence to test every required parameter's binding.

## Assertion vocabulary: PyHamcrest matchers

Assertions use PyHamcrest matchers (ADR 0011), in two places:

- **Inline** — `assert_that(actual, <matcher>)`.
- **Test-double call assertions** — when an exact match can't work, wrap the
  matcher in `matching` (alias for `match_equality`, `from stagentic.test.matchers import
  matching`) so it rides inside `assert_called_once_with`:
  `prompt=matching(contains_string(...))`. `ANY` still marks don't-care slots.

**Why:** one vocabulary across inline and call assertions, and call assertions
constrain every argument they name rather than pulling values back out of
`call_args`.

## Pin exact composed output once via `==`

When the production code composes a value from inputs, write one assertion that pins the exact composed string or structure via `==`.

**Per-property tests** (separate methods focused on a single property) earn their place when a property's **value, presence, or absence alters behaviour** — e.g. an omitted flag that triggers a different code path. Whole-story tests embody this convention's exact-match pinning — see *Whole-story tests*.

**Why:** the exact-match documents the shape — prefix, separator, ordering, glue — that a reader would otherwise have to infer from the production source, and catches accidental drift in the composition. Per-property tests make behavioural facts explicit that a whole-story test's exact-match alone wouldn't surface.

## MagicMock interrogation forms

Spy interrogation uses one of these four forms — picked by the shape of the call being spied on and what the assertion needs to express.

**Kwargs on `assert_called_once_with`:** `spy.method.assert_called_once_with(arg=expected, other=ANY)` — each named slot is an expected value (`==`), `matching(<matcher>)` where `==` can't express the check (see *Assertion vocabulary*), or `ANY` for a don't-care slot. Pins call count and every named slot in one expression. Fall back to a `call_args` pull (`value = spy.call_args.kwargs[name]; assert <predicate>(value)`) only when `matching` can't bind — the `spec=Class` gotcha (see below) or a cross-spy compare.

**Record-and-delegate:** `spy = MagicMock(side_effect=stub_callable)`. When the spy needs to record calls AND return a real-shape result, `side_effect` invokes the stub with the same args and returns its result; `spy.call_args` records the call as usual.

**Multi-call:** `assert spy.call_count == N; first, second = spy.call_args_list; assert first.kwargs[name] != second.kwargs[name]`. Pins the exact call count and inspects each call independently — no reliance on "the last call's value."

**Pure stub (no interrogation):** `MagicMock(return_value=value)`. When the spy's only job is to return a value, not to record calls.

**Why:** the `unittest.mock` toolkit has a native idiom for each shape. Picking the right form pins call count, args, and intent in one expression rather than inferring count from list-length or splitting count and args across separate assertions.

## `spec=Class` vs `spec=Class()` for directly-callable spies

When the spy stands in for a class whose *methods* you call (`session_spy.run(...)`), use `MagicMock(spec=ClassName)` — the class form. When the spy is *invoked directly* as `spy(...)` (because the underlying type is itself a callable, e.g. `ClaudeCli.__call__`), use `MagicMock(spec=ClassName())` — an instance.

**Why:** `spec=Class` binds `mock(...)` to `Class.__init__`'s signature; if the real call site invokes `__call__` (a different signature), `assert_called_once_with` fails to bind and the assertion fails even when the args match. `spec=Class()` binds to the instance's `__call__` instead.

**Trigger to revisit:** if a new spy target is itself directly callable (has `__call__`) and the assertion uses `assert_called_once_with`, prefer the instance spec form.

## Stub callable → lambda; spy callable → `MagicMock`

When a test passes a callable as part of a data literal (e.g. inside a row dict) and the callable's only job is to return a fixed value, use a `lambda` inline — it documents the call's shape at the call site. When the test needs to interrogate the callable (assert it was called, assert its args), use `MagicMock`.

**Why:** the lambda shows the callable's signature inline in the row literal, so a reader sees how the row is wired without scanning back to a local definition. A `MagicMock` would obscure that. Conversely, when the test interrogates the call, the `unittest.mock` API is the idiomatic interrogation surface; rolling a hand-written closure spy duplicates `MagicMock`'s functionality.
