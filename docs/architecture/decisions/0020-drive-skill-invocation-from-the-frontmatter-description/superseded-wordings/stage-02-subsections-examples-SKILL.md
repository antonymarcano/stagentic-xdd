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

# Making a test pass

Make a failing test pass using 'Fake-It' with 'Triangulation'; do not use 'Obvious Implementation'.

## Fake-It

Fake-It makes a test pass by making the smallest possible change to the code that
will pass the test, no matter how naive — and without breaking other tests.
Use Fake-It as the default way to make a failing test pass.

For example, to pass a first test `is_even(2) == True`, return the literal `True`.

## Triangulation

Triangulation is the process of each new test forcing an ever less naive implementation
until the real implementation satisfies the desired capability.

For example, adding `is_even(3) == False` — which the `return True` fake-it implementation cannot pass —
forces the naive code towards the real `return n % 2 == 0`.

## Obvious Implementation

Do not use Obvious Implementation. You can recognise it when you skip Fake-It and
write the general implementation directly. Instead, use Fake-It, then Triangulation,
to reach the real implementation.

For example, if you have a test asserting only `is_even(2) == True` then writing
`return n % 2 == 0` is applying the Obvious Implementation strategy.
