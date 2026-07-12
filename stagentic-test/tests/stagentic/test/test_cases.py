import pytest
from hamcrest import assert_that, equal_to

from stagentic.test.cases import case


class TestCase:
    def test_case_should_pair_the_scenario_name_with_values(self):
        param = case(
            "a scenario name",
            shape="hexagon", size="large"
        )

        assert_that(param.id, equal_to("a scenario name"))
        assert_that(param.values, equal_to(("hexagon", "large")))

    @pytest.mark.parametrize(
        "scenario_name",
        [
            "scenario name",
            "a different scenario name",
        ],
    )
    def test_case_should_use_the_scenario_name_as_its_id(self, scenario_name):
        param = case(scenario_name, any="value")

        assert_that(param.id, equal_to(scenario_name))

    def test_case_should_allow_values_to_be_arbitrarily_named(self):
        param = case("scenario name", wave="sine")

        assert_that(param.values, equal_to(("sine",)))
