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

Per ADR
[0010](architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md),
mutation testing is part of doing the work — scoped to the files in
`source_paths`, not the whole codebase.

This is the green-step discipline. While a `source_paths` file is in flight,
reaching green is not yet the cue to propose a commit: the green step is
**focused mutmut on the file → dial back any survivor to the most naive code
that still passes, re-running until clean → run the test suite the change's
scope calls for → full-set mutmut gate → remove the `mutants/` tree → propose
the commit**. Don't propose a
commit straight off a green when the file you're developing is a mutation
target.

**The file you're developing belongs in `source_paths` while you work on it.**
If it isn't a mutation target yet — a new module — add its path to `source_paths`
so mutmut mutates it, and run the focused check after *every* green. Keep that
`source_paths` addition uncommitted until the work's final green. (A *shared test
helper* can't be mutated from under `tests/`: mutmut's source roots are
hardcoded, so a `tests/`-located file's mutants never map to a covering test.
Home it in `test_utilities/src` instead, where it's a permanent mutation target
like any module — see ADR
[0012](architecture/decisions/0012-adopt-path-source-packages-for-cross-project-code.md).)
A green with no surviving mutants — or with no mutants at all, when the code is
too minimal to mutate — both mean nothing is running ahead of the tests.

**Start from a clean baseline.** A survivor after a red-green only implicates
your new code if the file had none before you started. For a file that predates
your change, baseline it with the focused check first; if it already carries
survivors — pre-existing speculative code, or coverage gaps — close them before
writing the new test/code, so any survivor that appears afterwards is
unambiguously yours to dial back.

**First — focused, on the file you're developing.** After every green, run
the focused mutation check on that file (see
[Mutation testing](../COMMANDS.md#mutation-testing) for the command and the
`<module>` naming). It's fast, and a surviving mutant means the
implementation is running ahead of its tests — speculative code no test pins.
Dial it back to what the test demands before going on: *remove* the unpinned
implementation — don't write a new test to cover the survivor. A survivor says
subtract code, not add coverage. The generality you strip is deferred, not
abandoned: it returns as its own red-green when a later test genuinely demands
it. Two beats — dial the overstep back against the current tests, then let a new
failing test drive the generalisation in.

**Then — the full set, as a regression gate.** Once the focused run is clean,
run `mutmut run` over `source_paths` before committing: it must come back clean,
or every survivor a documented accepted-mutation. Focused-first catches
overreach quickly, without paying for the full sweep first.
