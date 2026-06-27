from pathlib import Path

from claude_session import ClaudeSession
from inspector import Inspector
from result import Failure, Result, Success
from scorecard_json_extraction import candidate_scorecard_from
from scorecard_results import ScorecardResults


class Critic(Inspector):
    def __init__(self, *, session: ClaudeSession):
        self._session = session

    def evaluate(self, *,
        task_to_evaluate: Path,
        workspace: Path,
        evidence_source: Path,
        should: list[dict],
    ) -> Result[ScorecardResults, list[dict[str, str]]]:
        if not should:
            raise ValueError("scorecard must not be empty")

        reference_scene = task_to_evaluate / "scene"
        agent_response = self._session.run(
            prompt=_prompt_for(
                evidence_source, workspace, should, reference_scene
            ),
            working_dir=workspace,
            transcript_path=workspace / "critique.md",
            additional_dirs=(reference_scene,),
        )
        scorecard = ScorecardResults.from_(
            maybe_results=candidate_scorecard_from(agent_response),
            should=should,
        )
        match scorecard.failures():
            case []:
                return Success(scorecard)
            case failures:
                return Failure(failures)


def _prompt_for(
    evidence_source: Path, working_dir: Path, should: list[dict], reference_scene: Path
) -> str:
    characteristics = "\n".join(f"- {row['characteristic']}" for row in should)
    return (
        f"Transcript: {evidence_source}\n"
        f"Workspace: {working_dir}\n\n"
        f"Reference scene: {reference_scene}\n"
        f"The reference scene is the canonical end-state; for characteristics about the workspace, judge by equivalence to it.\n\n"
        f"Evaluate each of the following characteristics against the transcript and workspace.\n"
        f"Respond with only a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
        f"Characteristics:\n{characteristics}"
    )
