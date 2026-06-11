from pathlib import Path
from typing import Protocol

from result import Result
from scorecard_results import ScorecardResults


class Inspector(Protocol):
    def evaluate(
            self, *,
            evidence_source: Path,
            working_dir: Path,
            should: list[dict],
    ) -> Result[ScorecardResults, list[dict[str, str]]]: ...
