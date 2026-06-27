from pathlib import Path

from hamcrest import assert_that, equal_to, starts_with

from claude_transcriber import ClaudeTranscriber

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_TRANSCRIPT = FIXTURES / "sample-transcript.jsonl"
VARIED_TRANSCRIPT = FIXTURES / "varied-transcript.jsonl"


class TestClaudeTranscriber:
    def test_should_write_rendered_content_to_the_output_path(self, tmp_path):
        output_path = tmp_path / "transcript.md"
        expected = (FIXTURES / "sample-transcript.md").read_text()

        ClaudeTranscriber()(jsonl_path=SAMPLE_TRANSCRIPT, output_path=output_path)

        assert_that(output_path.read_text(), equal_to(expected))

    def test_should_prepend_the_cli_version_from_the_jsonl(self, tmp_path):
        output_path = tmp_path / "transcript.md"

        ClaudeTranscriber()(jsonl_path=SAMPLE_TRANSCRIPT, output_path=output_path)

        assert_that(
            output_path.read_text(),
            starts_with("`[VERSIONS]` Used in this run:\n```\nCLI: claude 2.1.150\n"),
        )

    def test_should_prepend_the_model_from_the_jsonl(self, tmp_path):
        output_path = tmp_path / "transcript.md"

        ClaudeTranscriber()(jsonl_path=SAMPLE_TRANSCRIPT, output_path=output_path)

        assert_that(
            output_path.read_text(),
            starts_with(
                "`[VERSIONS]` Used in this run:\n```\n"
                "CLI: claude 2.1.150\nMODEL: claude-opus-4-7\n```\n"
            ),
        )

    def test_should_show_unknown_cli_version_when_the_jsonl_has_none(self, tmp_path):
        output_path = tmp_path / "transcript.md"

        ClaudeTranscriber()(jsonl_path=VARIED_TRANSCRIPT, output_path=output_path)

        assert_that(
            output_path.read_text(),
            starts_with("`[VERSIONS]` Used in this run:\n```\nCLI: claude unknown\n"),
        )

    def test_should_show_unknown_model_when_the_jsonl_has_none(self, tmp_path):
        output_path = tmp_path / "transcript.md"

        ClaudeTranscriber()(jsonl_path=VARIED_TRANSCRIPT, output_path=output_path)

        assert_that(
            output_path.read_text(),
            starts_with(
                "`[VERSIONS]` Used in this run:\n```\n"
                "CLI: claude unknown\nMODEL: unknown\n```\n"
            ),
        )

    def test_should_render_varied_entries_to_the_approved_master(self, tmp_path):
        output_path = tmp_path / "transcript.md"
        expected = (FIXTURES / "varied-transcript.md").read_text()

        ClaudeTranscriber()(jsonl_path=VARIED_TRANSCRIPT, output_path=output_path)

        assert_that(output_path.read_text(), equal_to(expected))
