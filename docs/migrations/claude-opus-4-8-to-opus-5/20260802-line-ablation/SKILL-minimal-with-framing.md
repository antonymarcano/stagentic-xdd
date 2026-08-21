---
name: xdd
description: Use for ALL test-driven development work — before writing a failing test, making a failing test pass, or refactoring. Invoke before adding or changing any production or test code.
---

# Model Corrections

Your model has some misunderstandings of TDD, which you should override with the following:  

## Always Write the Test First

After the test is written, then change the production code so it [fails for the right reason](#failing-for-the-right-reason)

## Failing for the Right Reason

Where values are being compared in the assertion, the returned value must be of the same type.

## Making a Test Pass

Make a failing test pass using 'Fake-It'.
