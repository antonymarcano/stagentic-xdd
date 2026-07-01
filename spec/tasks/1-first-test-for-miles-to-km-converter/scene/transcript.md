[TOOL] **Write** `tests/test_conversion.py`

[TOOL] **Write** `src/conversion.py`

[TOOL] **Bash** `uv run pytest tests/`

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
configfile: pyproject.toml
collected 1 item

tests/test_conversion.py F                                               [100%]

=================================== FAILURES ===================================
______________________ test_one_mile_is_about_1_60934_km _______________________

    def test_one_mile_is_about_1_60934_km():
>       assert miles_to_km(1) == 1.60934
E       assert 0 == 1.60934
E        +  where 0 = miles_to_km(1)

tests/test_conversion.py:5: AssertionError
=========================== short test summary info ============================
FAILED tests/test_conversion.py::test_one_mile_is_about_1_60934_km - assert 0 == 1.60934
============================== 1 failed in 0.01s ===============================
```
