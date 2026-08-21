---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

## Always Write the Test First

1. After the test is written, then change the production code so it [fails for the right reason](#failing-for-the-right-reason)

## Failing for the Right Reason

A test fails for the right reason when:
- Where values are being compared in the assertion, the returned value must be of the same type.
