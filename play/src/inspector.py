from pathlib import Path
from typing import Protocol

from result import Result
from scorecard_results import ScorecardResults


class Inspector(Protocol):
    def evaluate(
            self, *,
            evidence_source: Path,
            workspace: Path,
            should: list[dict],
            task_to_evaluate: Path,
    ) -> Result[ScorecardResults, list[dict[str, str]]]: ...
