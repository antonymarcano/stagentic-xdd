# Lessons

A lesson records one distinct BDD/TDD misstep a coding agent made under the
[xdd skill](../../xdd-plugin/skills/xdd) — with the correction that resolved it and
the configuration it was seen and validated under.

The xdd skill is built by closing these missteps: a real agent runs a task, an
inspector scores the transcript, and where the agent falls short of
[BDD/TDD discipline](https://www.linkedin.com/pulse/what-almost-everyone-gets-wrong-tdd-bdd-antony-marcano-shjye)
the guidance is changed until it passes.

Each lesson is the durable record of that cycle:

- *why* a piece of guidance exists and *what* misstep it defends against — so a
  later editor can see what a line holds back before pruning it;
- source material for an overseeing agent that catches the same missteps during
  ordinary work.

The process — one lesson per principle, written as the work happens, committed on
green alongside the guidance change — is defined in
[ADR 0015](../architecture/decisions/0015-capture-xdd-skill-missteps-as-lessons.md).
[`TEMPLATE.md`](TEMPLATE.md) is the lesson shape.

## Index

| # | Lesson | Misstep it guards against |
|---|---|---|
| 1 | [An honest red fails on the assertion, not the import](20260627-2225-honest-red-fails-on-the-assertion-not-the-import/lesson.md) | Stopping at an import-error red instead of driving the failure down to an assertion. |
| 2 | [The failing test is written before the production code](20260628-1800-write-the-failing-test-before-the-production-code/lesson.md) | Writing the production code before the failing test. |
| 3 | [Fake it until you triangulate it](20260701-0635-fake-it-until-you-triangulate-it/lesson.md) | Jumping to the general implementation (Obvious Implementation) instead of Fake-It. |
| 4 | [A failing stub returns a value of the asserted type](20260710-1711-a-failing-stub-returns-a-value-of-the-asserted-type/lesson.md) | Stubbing with a value whose type differs from the asserted value (`None`, int), so the red is a type artefact rather than a value comparison. |
