import json

import pytest
from stagentic.test.cases import case

from scorecard_json_extraction import candidate_scorecard_from


class TestScorecardJsonExtraction:
    @pytest.mark.parametrize("response, expected", [
        case(
            "single-row",
            response='[{"characteristic": "captures input", "status": "PASS"}]',
            expected=[{"characteristic": "captures input", "status": "PASS"}],
        ),
        case(
            "multiple-rows",
            response=(
                '[{"characteristic": "captures input", "status": "PASS"},'
                ' {"characteristic": "reports outcome", "status": "FAIL"}]'
            ),
            expected=[
                {"characteristic": "captures input", "status": "PASS"},
                {"characteristic": "reports outcome", "status": "FAIL"},
            ],
        ),
    ])
    def test_extraction_should_return_the_decoded_scorecard(self, response, expected):
        assert candidate_scorecard_from(response) == expected

    @pytest.mark.parametrize("response", [
        case(
            "prose-before-json",
            response='Based on my evaluation:\n\n[{"characteristic": "any", "status": "PASS"}]',
        ),
        case(
            "fence-without-language-hint",
            response='```\n[{"characteristic": "any", "status": "PASS"}]\n```',
        ),
        case(
            "code-fenced-json",
            response='```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n',
        ),
        case(
            "prose-before-fenced-json",
            response='Based on the transcript:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n',
        ),
        case(
            "prose-around-fenced-json",
            response='Based on the transcript:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nThat completes the evaluation.',
        ),
        case(
            "code-block-before-fenced-json",
            response='Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```',
        ),
        case(
            "multiline-json-in-fence",
            response='```json\n[\n  {"characteristic": "any", "status": "PASS"}\n]\n```\n',
        ),
        case(
            "bracketed-prose-before-json",
            response='Based on [1] the evidence:\n[{"characteristic": "any", "status": "PASS"}]',
        ),
        case(
            "closing-fence-without-newline",
            response='```json\n[{"characteristic": "any", "status": "PASS"}]```',
        ),
        case(
            "single-char-before-json",
            response='>[{"characteristic": "any", "status": "PASS"}]',
        ),
        case(
            "code-block-after-fenced-json",
            response='```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```',
        ),
        case(
            "prose-after-json",
            response='[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.',
        ),
        case(
            "prose-after-json-with-bracket-in-prose",
            response='[{"characteristic": "any", "status": "PASS"}]\n\nSee [note] for details.',
        ),
        case(
            "prose-around-json-with-bracket-in-trailing-prose",
            response='Based on the transcript:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nSee [note] for details.',
        ),
        case(
            "prose-around-json-with-decodable-bracket-in-trailing-prose",
            response='Based on the transcript:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nSee [1] for details.',
        ),
        case(
            "non-evaluation-json-after-scorecard",
            response='The evaluation:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nFor reference, files changed:\n\n[{"path": "conversion.py", "added": 12}]',
        ),
        case(
            "non-evaluation-json-before-scorecard",
            response='[{"path": "conversion.py", "added": 12}]\n\n[{"characteristic": "any", "status": "PASS"}]',
        ),
    ])
    def test_extraction_should_find_the_scorecard_in_wrapped_json(self, response):
        assert candidate_scorecard_from(response) == [
            {"characteristic": "any", "status": "PASS"}
        ]

    @pytest.mark.parametrize("response, characteristic_name", [
        case(
            "brackets",
            response='[{"characteristic": "lists [every] item", "status": "PASS"}]',
            characteristic_name="lists [every] item",
        ),
        case(
            "triple-backticks",
            response='```json\n[{"characteristic": "uses ```code``` blocks", "status": "PASS"}]\n```',
            characteristic_name="uses ```code``` blocks",
        ),
        case(
            "brackets-inside-fence",
            response='```json\n[{"characteristic": "lists [every] item", "status": "PASS"}]\n```',
            characteristic_name="lists [every] item",
        ),
        case(
            "code-block-before-fenced-json-with-bracket-in-string",
            response='Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```',
            characteristic_name="any [example]",
        ),
        case(
            "code-block-before-unhinted-fenced-json-with-bracket-in-string",
            response='Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```\n[{"characteristic": "any [example]", "status": "PASS"}]\n```',
            characteristic_name="any [example]",
        ),
    ])
    def test_extraction_should_find_the_scorecard_despite_special_characters_in_strings(
            self, response, characteristic_name,
    ):
        assert candidate_scorecard_from(response) == [
            {"characteristic": characteristic_name, "status": "PASS"}
        ]

    @pytest.mark.parametrize("response", [
        case("non-json-prose", response="not valid json."),
        case("truncated-mid-json", response='[{"characteristic": "any", "status": "P'),
    ])
    def test_extraction_should_raise_ValueError_with_cause_when_response_is_not_valid_json(self, response):
        with pytest.raises(ValueError) as excinfo:
            candidate_scorecard_from(response)

        assert str(excinfo.value) == f"response did not contain valid JSON: {response!r}"
        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)
