from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_approved_top_level_boundaries_exist() -> None:
    for name in [
        "specs",
        "cpu",
        "emulator",
        "simulator",
        "assembler",
        "microcode",
        "loader",
        "hardware",
        "programs",
        "tests",
        "scripts",
        "docs",
    ]:
        assert (ROOT / name).is_dir(), name


def test_compiler_boundary_is_not_created() -> None:
    assert not (ROOT / "compiler").exists()
