---
name: xdd
description: Use when adding or changing code. New code is created by adhering to TDD discipline.
---

Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:

# Always write the test first

The test should always be written before the production code that makes it pass.

# Failing for the right reason

A test fails for the right reason when it has an assertion failure where the actual
result is not matching the expected result.

# Making a test pass — do not use the 'Obvious Implementation' strategy

Make a failing test pass as naively as possible — hard-code whatever answer the
test asserts rather than writing the general implementation. A single test cannot
tell a hard-coded answer apart from the general implementation — both pass it — so
the general implementation introduces behaviour no test has asked for or verified.
Generalise *only* when a subsequent, differing test forces it.
