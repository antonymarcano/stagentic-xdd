---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

# Workflow

Repeat this loop until it satisfies the task it has been set, according to the principles of TDD and taking account of the [model corrections](#model-corrections) below:

1. Write a test.
2. Run it, then read the result:
- If the task is complete, stop.
- If the test failed, go to step 3.
3. When adding/changing production code:
- Make the minimum change that addresses only the failure the run just presented
- Write no more code than that failure demands, regardless of how naive the change might seem.
4. If the task is not complete:
- Go back to step 2 if the test is still failing
- Go back to step 1 if the test now passes.

# Model corrections

Your model has some misunderstandings of TDD, which you should override with the following:

## Always write the test first

Decide upon the test first, then write it before deciding on what code change is required next.

## Failing for the right reason

A test fails for the right reason when:
- It has an assertion failure where the actual result is not matching the expected result and
- Where values are being compared in the assertion, the returned value must be of the same type.

## Making a test pass

Make a failing test pass using 'Fake-It'.
