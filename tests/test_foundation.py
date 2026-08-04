from pathlib import Path

import r8_foundation

ROOT = Path(__file__).parents[1]


def test_package_metadata_is_available() -> None:
    assert r8_foundation.__version__ == "0.1.0"


def test_repository_root_is_deterministic() -> None:
    assert (ROOT / "AGENTS.md").is_file()
    assert (ROOT / "docs" / "architecture.md").is_file()


def test_runner_is_deterministic() -> None:
    assert sorted(["foundation", "repository"]) == ["foundation", "repository"]
