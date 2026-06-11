from pathlib import Path

from inspector import Inspector
from result import Failure, Result, Success
from scorecard_results import ScorecardResults


class Auditor(Inspector):
    def evaluate(
            self, *,
            evidence_source: Path,
            working_dir: Path,
            should: list[dict],
    ) -> Result[ScorecardResults, list[dict[str, str]]]:
        if not should: raise ValueError("scorecard must not be empty")

        evidence_content = evidence_source.read_text()
        match _entries_from(_failures_from(evidence_content, working_dir, should)):
            case []:
                return Success(ScorecardResults(
                    should=_entries_from(should),
                    results=[{"characteristic": row["characteristic"], "status": "PASS"}
                             for row in should],
                ))
            case failures:
                return Failure(failures)


def _failures_from(content: str, working_dir: Path, should: list[dict]) -> list[dict]:
    return [row for row in should if not row["verify"](content, working_dir)]


def _entries_from(failures: list[dict]) -> list[dict[str, str]]:
    return [{"characteristic": row["characteristic"], "failure": row["failure"]} for row in failures]
