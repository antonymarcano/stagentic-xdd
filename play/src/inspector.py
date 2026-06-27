from pathlib import Path
from typing import Protocol

from result import Result
from scorecard_results import ScorecardResults


class Inspector(Protocol):
    def evaluate(self, *,
        task_to_evaluate: Path,
        workspace: Path,
        evidence_source: Path,
        should: list[dict],
    ) -> Result[ScorecardResults, list[dict[str, str]]]: ...
