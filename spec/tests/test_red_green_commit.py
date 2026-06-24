import ast
import re
import shutil
from pathlib import Path

from hamcrest import assert_that
from result_matchers import is_a_success

TASKS = Path(__file__).parent.parent / "tasks"


class TestRedGreenCommit:
    def test_write_a_failing_test(self, tmp_path, agent, inspector):
        working_dir = tmp_path / "miles-to-km"
        _set_opening_scene_for("0-placeholder", working_dir)
        task_name = "1-first-test-for-miles-to-km-converter"

        transcript = agent.perform(
            task=task_name,
            working_dir=working_dir
        ).value

        assert_that(
            inspector.evaluate(
                evidence_source=transcript,
                workspace=working_dir,
                task_to_evaluate=TASKS / task_name,
                should=_have_completed(
                    task_name,
                    matching=[
                        "Production module exists at src/conversion.py with content",
                        f"Workspace closely matches the scene structure for {task_name} (src, tests)",
                        "Production returns a literal value, and does not use a formula",
                        "Transcript shows the agent ran pytest",
                        "Transcript shows a FAILED pytest result",
                        "Test fails comparing a return value, not on a missing module or symbol",
                    ],
                ),
            ),
            is_a_success(),
        )


def _set_opening_scene_for(task_name: str, working_dir: Path) -> None:
    shutil.copytree(TASKS / task_name / "scene", working_dir)


# FULL SCORECARD MAPPING
# Including optional programmatic Auditor lambdas (ignored by agentic Critic)
def _have_completed(task_name, *, matching):
    table = {
        "Production module exists at src/conversion.py with content": {
            "verify": lambda transcript, target_dir, reference_scene: (
                (target_dir / "src" / "conversion.py").is_file()
                and (target_dir / "src" / "conversion.py").stat().st_size > 0
            ),
            "failure": "src/conversion.py is missing or empty",
        },
        f"Workspace closely matches the scene structure for {task_name} (src, tests)": {
            "verify": lambda transcript, target_dir, reference_scene: (
                not _tree_diff(reference_scene, target_dir)
            ),
            "failure": "workspace contents do not match the expected end-state",
        },
        "Production returns a literal value, and does not use a formula": {
            "verify": lambda transcript, target_dir, reference_scene: _returns_only_literals(
                target_dir / "src" / "conversion.py"
            ),
            "failure": "src/conversion.py uses a computed formula, not a literal value",
        },
        "Transcript shows the agent ran pytest": {
            "verify": lambda transcript, target_dir, reference_scene: bool(
                re.search(r"\[TOOL] \*\*Bash\*\*.*?pytest", transcript, re.DOTALL)
            ),
            "failure": "transcript shows no `[TOOL] **Bash**` running pytest",
        },
        "Transcript shows a FAILED pytest result": {
            "verify": lambda transcript, target_dir, reference_scene: bool(
                re.search(
                    r"\[TOOL] \*\*Bash\*\*.*?pytest.*?FAILED", transcript, re.DOTALL
                )
            ),
            "failure": "transcript shows no FAILED result from pytest",
        },
        "Test fails comparing a return value, not on a missing module or symbol": {
            "verify": lambda transcript, target_dir, reference_scene: (
                bool(
                    re.search(
                        r"FAILED.*?(assert|AssertionError)", transcript, re.DOTALL
                    )
                )
                and not re.search(
                    r"(ImportError|NameError|ModuleNotFoundError|cannot import name)",
                    transcript,
                    re.DOTALL,
                )
            ),
            "failure": "assertion failed on a missing module or symbol, not on a return value that didn't match",
        },
    }
    return [{"characteristic": name, **table[name]} for name in matching]


def _returns_only_literals(source_path: Path) -> bool:
    tree = ast.parse(source_path.read_text())
    returns = [n for n in ast.walk(tree) if isinstance(n, ast.Return)]
    return bool(returns) and all(_is_literal(r.value) for r in returns)


def _is_literal(node: ast.expr | None) -> bool:
    if isinstance(node, ast.UnaryOp):
        node = node.operand
    return isinstance(node, ast.Constant)


def _tree_diff(expected_root, actual_root):
    expected = {
        p.relative_to(expected_root): p for p in expected_root.rglob("*") if p.is_file()
    }
    actual = {
        p.relative_to(actual_root): p for p in actual_root.rglob("*") if p.is_file()
    }
    diffs = []
    for rel in sorted(set(expected) | set(actual), key=str):
        if rel not in expected:
            diffs.append(f"unexpected: {rel}")
        elif rel not in actual:
            diffs.append(f"missing: {rel}")
        elif expected[rel].read_bytes() != actual[rel].read_bytes():
            diffs.append(f"differs: {rel}")
    return diffs
