from pathlib import Path

from inspector import Inspector
from result import Failure, Result, Success
from scorecard_results import ScorecardResults


class Auditor(Inspector):
    def evaluate(
            self, *,
            evidence_source: Path,
            workspace: Path,
            should: list[dict],
            task_to_evaluate: Path,
    ) -> Result[ScorecardResults, list[dict[str, str]]]:
        if not should: raise ValueError("scorecard must not be empty")

        reference_scene = task_to_evaluate / "scene"
        evidence_content = evidence_source.read_text()
        match _entries_from(
            _failures_from(evidence_content, workspace, should, reference_scene)
        ):
            case []:
                return Success(ScorecardResults(
                    should=_entries_from(should),
                    results=_passes_from(should),
                ))
            case failures:
                return Failure(failures)


def _entries_from(failures: list[dict]) -> list[dict[str, str]]:
    return [{"characteristic": row["characteristic"], "failure": row["failure"]} for row in failures]


def _failures_from(content: str, working_dir: Path, should: list[dict], reference_scene: Path) -> list[dict]:
    return [row for row in should if not row["verify"](content, working_dir, reference_scene)]


def _passes_from(should: list[dict]) -> list[dict[str, str]]:
    return [{"characteristic": row["characteristic"], "status": "PASS"} for row in should]
