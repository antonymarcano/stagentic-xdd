# Working practices

## Lead with the proposed commit

For any change or series of changes, propose the commit message(s)
before the implementation. See [`commit-style.md`](commit-style.md)
for the shape of commit messages.

For any series of changes, number each proposed commit so the user
can easily reference them. When revisiting a numbered item, always
include at least the commit subject.

Applies to proposals from a person or from an agent.

## Separate behavioural and structural changes

Each commit either changes observable behaviour (new test, new
feature, bug fix) or it changes structure (refactor that preserves
behaviour) — never both. Mixed commits force a reviewer to
disentangle which lines do what; separate commits let each kind be
inspected on its own.

Structural commits may touch a single file or many files. What makes
them structural is that they preserve behaviour: every test passes
before and after, with no test added or modified to assert new
intent.

The rule applies equally to source and tests.

## Mutation-test as you work

Per ADR [0010](architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md),
mutation testing is part of doing the work — scoped to the files in
`source_paths`, not the whole codebase. While a `source_paths` file is in
flight, reaching green is not the cue to commit. The green step runs this
sequence (see [Mutation testing](../COMMANDS.md#mutation-testing) for the
commands and `<module>` naming):

1. **Focused mutmut on the file.** Dial back any survivor to the most naive
   code that still passes; re-run until clean.
2. **Run the test suite** the change's scope calls for.
3. **Full-set mutmut over `source_paths`** as the regression gate: clean, or
   every survivor a documented accepted-mutation.
4. **Remove the `mutants/` tree**, then propose the commit.

Focused-first catches overreach quickly, before you pay for the full sweep.

**A survivor means subtract code, not add coverage.** The focused check is
fast; a surviving mutant means the implementation is running ahead of its
tests — speculative code no test pins. *Remove* it — don't write a test to
cover the survivor. The generality you strip isn't abandoned: a later test that
genuinely demands it drives it back in as its own red-green. (A green with no
survivors — or none to mutate, when the code is too minimal — both mean nothing
runs ahead of the tests.)

**Start from a clean baseline.** A survivor implicates your new code only if
the file had none before you started. For a file that predates your change,
baseline it with the focused check first and close any pre-existing survivors —
speculative code or coverage gaps — before writing the new test/code, so any
survivor that appears afterwards is unambiguously yours to dial back.

**Keep the file in `source_paths` while you work on it.** If it isn't a
mutation target yet — a new module — add its path so mutmut mutates it, and run
the focused check after every green. When to commit that addition:

- **New module, developed clean from the outset** (every green survivor-free):
  commit the `source_paths` addition as you go — each commit is already a clean
  baseline.
- **Existing file that starts with survivors:** keep the addition uncommitted
  until the work's final green, so you never commit a baseline that isn't yet
  clean.

A *shared test helper* can't be mutated from under `tests/`: mutmut's source
roots are hardcoded, so a `tests/`-located file's mutants never map to a
covering test. Home it in `stagentic-test/src/stagentic/test` instead, where
it's a permanent mutation target like any module — see ADR
[0012](architecture/decisions/0012-adopt-path-source-packages-for-cross-project-code.md).
