import pytest
from hamcrest import assert_that, equal_to
from stagentic.test.cases import case

from scorecard_results import ScorecardResults


class TestScorecardResults:
    class TestAcceptsValidResults:
        @pytest.mark.parametrize("maybe_results", [
            case(
                "single-result",
                maybe_results=[{"characteristic": "captures input", "status": "PASS"}],
            ),
            case(
                "multiple-results",
                maybe_results=[
                    {"characteristic": "captures input", "status": "PASS"},
                    {"characteristic": "reports outcome", "status": "FAIL"},
                ],
            ),
        ])
        def test_should_bind_them_to_the_scorecard(self, maybe_results):
            should = characteristics_for_all(maybe_results)

            scorecard = ScorecardResults.from_(
                maybe_results=maybe_results,
                should=should,
            )

            assert_that(scorecard, equal_to(ScorecardResults(should=should, results=maybe_results)))

    class TestReportsFailures:
        @pytest.mark.parametrize("non_pass_status", [
            case("fail", non_pass_status="FAIL"),
            case("inconclusive", non_pass_status="INCONCLUSIVE"),
        ])
        def test_should_list_a_characteristic_that_did_not_pass(self, non_pass_status):
            scorecard = ScorecardResults.from_(
                maybe_results=[{"characteristic": "alpha", "status": non_pass_status}],
                should=[{"characteristic": "alpha", "failure": "alpha reason"}],
            )

            assert_that(scorecard.failures(), equal_to([{"characteristic": "alpha", "failure": "alpha reason"}]))

        def test_should_exclude_a_characteristic_that_passed(self):
            scorecard = ScorecardResults.from_(
                maybe_results=[
                    {"characteristic": "alpha", "status": "FAIL"},
                    {"characteristic": "beta", "status": "PASS"},
                ],
                should=[
                    {"characteristic": "alpha", "failure": "alpha reason"},
                    {"characteristic": "beta", "failure": "beta reason"},
                ],
            )

            assert_that(scorecard.failures(), equal_to([{"characteristic": "alpha", "failure": "alpha reason"}]))

        def test_should_list_every_characteristic_that_did_not_pass(self):
            scorecard = ScorecardResults.from_(
                maybe_results=[
                    {"characteristic": "first", "status": "FAIL"},
                    {"characteristic": "middle", "status": "PASS"},
                    {"characteristic": "third", "status": "FAIL"},
                ],
                should=[
                    {"characteristic": "first", "failure": "first failure"},
                    {"characteristic": "middle", "failure": "middle failure"},
                    {"characteristic": "third", "failure": "third failure"},
                ],
            )

            assert_that(scorecard.failures(), equal_to([
                {"characteristic": "first", "failure": "first failure"},
                {"characteristic": "third", "failure": "third failure"},
            ]))

        def test_should_be_empty_when_every_characteristic_passed(self):
            scorecard = ScorecardResults.from_(
                maybe_results=[
                    {"characteristic": "alpha", "status": "PASS"},
                    {"characteristic": "beta", "status": "PASS"},
                ],
                should=[
                    {"characteristic": "alpha", "failure": "alpha reason"},
                    {"characteristic": "beta", "failure": "beta reason"},
                ],
            )

            assert_that(scorecard.failures(), equal_to([]))

    class TestRejectsInvalidResults:
        def test_should_raise_when_there_are_no_results(self):
            no_results = []
            dummy_scorecard = []

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    maybe_results=no_results,
                    should=dummy_scorecard
                )

            assert_that(str(excinfo.value), equal_to("results must not be empty"))

        @pytest.mark.parametrize("maybe_results, expected_message", [
            case(
                "missing-characteristic",
                maybe_results=[{"status": "PASS"}],
                expected_message=(
                    "invalid rows:\n"
                    "- missing 'characteristic': {'status': 'PASS'}"
                ),
            ),
            case(
                "missing-status",
                maybe_results=[{"characteristic": "runs the test"}],
                expected_message=(
                    "invalid rows:\n"
                    "- missing 'status': {'characteristic': 'runs the test'}"
                ),
            ),
            case(
                "missing-both",
                maybe_results=[{"name": "delta", "result": "FAIL"}],
                expected_message=(
                    "invalid rows:\n"
                    "- missing 'characteristic', 'status': {'name': 'delta', 'result': 'FAIL'}"
                ),
            ),
            case(
                "missing-either-across-rows",
                maybe_results=[
                    {"name": "alpha", "status": "PASS"},
                    {"characteristic": "beta", "status": "PASS"},
                    {"characteristic": "gamma", "result": "FAIL"},
                ],
                expected_message=(
                    "invalid rows:\n"
                    "- missing 'characteristic': {'name': 'alpha', 'status': 'PASS'}\n"
                    "- missing 'status': {'characteristic': 'gamma', 'result': 'FAIL'}"
                ),
            ),
        ])
        def test_should_name_the_key_it_lacks(self, maybe_results, expected_message):
            dummy_scorecard = []

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    maybe_results=maybe_results,
                    should=dummy_scorecard
                )

            assert_that(str(excinfo.value), equal_to(expected_message))

    class TestRejectsIncoherentResults:
        @pytest.mark.parametrize("results, expected_message", [
            case(
                "all-duplicated",
                results=[
                    {"characteristic": "alpha", "status": "PASS"},
                    {"characteristic": "alpha", "status": "FAIL"},
                ],
                expected_message=(
                    "duplicated characteristics:\n"
                    "- alpha: PASS\n"
                    "- alpha: FAIL"
                ),
            ),
            case(
                "some-duplicated",
                results=[
                    {"characteristic": "beta", "status": "PASS"},
                    {"characteristic": "alpha", "status": "PASS"},
                    {"characteristic": "beta", "status": "FAIL"},
                ],
                expected_message=(
                    "duplicated characteristics:\n"
                    "- beta: PASS\n"
                    "- beta: FAIL"
                ),
            ),
        ])
        def test_should_list_a_duplicated_characteristic(self, results, expected_message):
            should = characteristics_for_all(results)

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    maybe_results=results,
                    should=should,
                )

            assert_that(str(excinfo.value), equal_to(expected_message))

        @pytest.mark.parametrize("should, expected_message", [
            case(
                "one-unaccounted",
                should=[
                    {"characteristic": "first"},
                    {"characteristic": "second"},
                ],
                expected_message="unaccounted characteristics: second",
            ),
            case(
                "two-unaccounted",
                should=[
                    {"characteristic": "first"},
                    {"characteristic": "second"},
                    {"characteristic": "third"},
                ],
                expected_message="unaccounted characteristics: second, third",
            ),
        ])
        def test_should_list_unaccounted_for_characteristics(self, should, expected_message):
            results = [{"characteristic": "first", "status": "PASS"}]

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    should=should,
                    maybe_results=results,
                )

            assert_that(str(excinfo.value), equal_to(expected_message))

        @pytest.mark.parametrize("results, expected_message", [
            case(
                "one-unexpected",
                results=[
                    {"characteristic": "first", "status": "PASS"},
                    {"characteristic": "extra", "status": "PASS"},
                ],
                expected_message="unexpected characteristics: extra",
            ),
            case(
                "two-unexpected",
                results=[
                    {"characteristic": "first", "status": "PASS"},
                    {"characteristic": "extra", "status": "PASS"},
                    {"characteristic": "other", "status": "PASS"},
                ],
                expected_message="unexpected characteristics: extra, other",
            ),
        ])
        def test_should_list_unexpected_characteristics(self, results, expected_message):
            should = [{"characteristic": "first"}]

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    maybe_results=results,
                    should=should,
                )

            assert_that(str(excinfo.value), equal_to(expected_message))

        def test_should_report_every_problem_together(self):
            results = [
                {"characteristic": "alpha", "status": "PASS"},
                {"characteristic": "alpha", "status": "FAIL"},
                {"characteristic": "invented", "status": "PASS"},
            ]
            should = [
                {"characteristic": "alpha"},
                {"characteristic": "missing"},
            ]

            with pytest.raises(ValueError) as excinfo:
                ScorecardResults.from_(
                    maybe_results=results,
                    should=should,
                )

            assert_that(str(excinfo.value), equal_to(
                "duplicated characteristics:\n"
                "- alpha: PASS\n"
                "- alpha: FAIL\n"
                "\n"
                "unaccounted characteristics: missing\n"
                "\n"
                "unexpected characteristics: invented"
            ))


def characteristics_for_all(results):
    return [
        {"characteristic": name}
        for name in dict.fromkeys(
            result["characteristic"] for result in results
        )
    ]
