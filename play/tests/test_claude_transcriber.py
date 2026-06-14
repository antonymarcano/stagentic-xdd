from pathlib import Path

from hamcrest import assert_that, equal_to

from claude_transcriber import ClaudeTranscriber

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_TRANSCRIPT = FIXTURES / "sample-transcript.jsonl"


class TestClaudeTranscriber:
    def test_should_write_rendered_content_to_the_output_path(self, tmp_path):
        output_path = tmp_path / "transcript.md"
        expected = (FIXTURES / "sample-transcript.md").read_text()

        ClaudeTranscriber()(jsonl_path=SAMPLE_TRANSCRIPT, output_path=output_path)

        assert_that(output_path.read_text(), equal_to(expected))
