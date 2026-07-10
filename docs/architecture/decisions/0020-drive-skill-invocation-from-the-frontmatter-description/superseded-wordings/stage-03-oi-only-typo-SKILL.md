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

# Do Not Use the 'Obvious Implementation' strategy to make a test pass

The Obvious Implementation strategy is when you make a test pass with a known implementation.

For example, Obvious Implmentation is when you have a test asserting `is_even(2) == True` then write
`return n % 2 == 0` when `return True` would have also passed the test (and not break any others).

Do not use the Obvious Implementation strategy.