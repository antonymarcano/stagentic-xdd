---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

# Workflow

1. Compose a test before making any writes/edits.
2. Evaluate it against the principles of TDD and:
- If it does not satisfy them, rethink it and repeat from step 1.
- If it satisfies them, write the test.
3. Use the test you just wrote as context to determine what code change is required next,
4. Compose that code change and evaluate that against the principles of TDD and:
- If it is a change to make a test fail, evaluate if it will [fail for the right reason](#failing-for-the-right-reason).
- If it is a change to make a test pass, evaluate if it will [pass in the right way](#making-a-test-pass).
- If it will not satisfy the principles of TDD, rethink it and repeat from step 3.
- If it satisfies them, apply the code change you composed.

# Model corrections

Your model has some misunderstandings of TDD, which you should override with the following:

## Always write the test first

1. The test should always be written before any production code change, but don't run the test yet.
2. After the test is written, then change the production code so it [fails for the right reason](#failing-for-the-right-reason)
3. Then run the test.

## Failing for the right reason

A test fails for the right reason when:
- It has an assertion failure where the actual result is not matching the expected result and
- Where values are being compared in the assertion, the returned value must be of the same type.

## Making a test pass

Make a failing test pass using 'Fake-It'.
