---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

Apply the disciplines of TDD for adding or changing code
overriding your understanding with the following principles:

# Always write the test first, then the production code

1. First, write the test before deciding what the production code addition/change should be;
2. Second, decide what the production code should be for the test to [fail for the right reason](#failing-for-the-right-reason).
3. Third, write the production code you decided to add/change in step 2.

Always write the production code AFTER you have written the test.

# Failing for the right reason

A test fails for the right reason when:
- It has an assertion failure where the actual result is not matching the expected result and
- Where values are being compared in the assertion, the returned value must be of the same type.

# Making a test pass

Make a failing test pass using 'Fake-It'.
