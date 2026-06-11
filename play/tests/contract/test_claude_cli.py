import uuid

import pytest

from claude_cli import ClaudeCli


@pytest.mark.contract
def test_claude_cli_responds_to_a_simple_prompt(tmp_path):
    result = ClaudeCli()(
        "Respond with exactly the word PASS and nothing else.",
        workspace=tmp_path,
        session_id=str(uuid.uuid4()),
    )
    assert "PASS" in result
