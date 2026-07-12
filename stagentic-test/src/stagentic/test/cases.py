import pytest


def case(scenario_name, **named_values):
    return pytest.param(
        *named_values.values(),
        id=scenario_name
    )
