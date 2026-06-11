from dataclasses import dataclass

from raise_when import raise_when

_REQUIRED_KEYS = ("characteristic", "status")


@dataclass
class ScorecardResults:
    should: list[dict]
    results: list[dict]

    @classmethod
    def from_(cls, maybe_results, should):
        results = _results_unless(
            maybe_results,
            has_problem=_invalid,
            raising_error=ValueError,
        )

        raise_when(
            _problems_of([
                _duplicated(results),
                _unaccounted_for(should, results),
                _unexpected(should, results),
            ]),
            raising_error=ValueError,
            with_message=_problems_message,
        )

        return cls(should=should, results=results)

    def failures(self):
        statuses = {row["characteristic"]: row["status"] for row in self.results}
        return [row for row in self.should if statuses.get(row["characteristic"]) != "PASS"]


def _results_unless(maybe_results, *, has_problem, raising_error):
    problem = has_problem(maybe_results)
    if problem: raise raising_error(problem)
    return maybe_results


def _invalid(maybe_results):
    problems = _problems_of([
        _empty(maybe_results),
        _invalid_rows_in(maybe_results),
    ])
    return _problems_message(problems) if problems else None


def _empty(maybe_results):
    return "results must not be empty" if not maybe_results else None


def _invalid_rows_in(maybe_results):
    results_with_missing_keys = [
        result for result in maybe_results if _is_missing_key_from(result)
    ]
    return _formatted_invalid_results(
        results_with_missing_keys
    ) if results_with_missing_keys else None


def _is_missing_key_from(result):
    return any(
        key not in result for key in _REQUIRED_KEYS
    )


def _formatted_invalid_results(results):
    return "invalid rows:\n" + "\n".join(
        _formatted_invalid_result(result) for result in results
    )


def _formatted_invalid_result(result):
    missing = ", ".join(
        repr(key) for key in _REQUIRED_KEYS if key not in result
    )
    return f"- missing {missing}: {result}"


def _duplicated(results):
    characteristics = [result["characteristic"] for result in results]
    duplicated = {
        name for name in characteristics if characteristics.count(name) > 1
    }
    return _formatted_duplicates(results, duplicated) if duplicated else None


def _formatted_duplicates(results, duplicated):
    return "duplicated characteristics:\n" + "\n".join(
        f"- {result['characteristic']}: {result['status']}"
        for result in results
        if result["characteristic"] in duplicated
    )


def _unaccounted_for(should, results):
    reported = {result["characteristic"] for result in results}
    unaccounted = [
        row["characteristic"] for row in should
        if row["characteristic"] not in reported
    ]
    return f"unaccounted characteristics: {', '.join(unaccounted)}" if unaccounted else None


def _unexpected(should, results):
    expected = {row["characteristic"] for row in should}
    unexpected = [
        result["characteristic"] for result in results
        if result["characteristic"] not in expected
    ]
    return f"unexpected characteristics: {', '.join(unexpected)}" if unexpected else None


def _problems_of(possible_problems):
    return [
        problem for problem in possible_problems if problem is not None
    ]


def _problems_message(problems):
    return "\n\n".join(problems)
