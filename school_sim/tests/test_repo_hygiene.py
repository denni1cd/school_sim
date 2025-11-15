"""Check repository hygiene indicators used by the suite."""

from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_school_sim_directory_structure():
    tests_dir = Path(__file__).resolve().parent
    school_root = tests_dir.parent

    assert school_root.name == "school_sim"

    required_children = {
        school_root / "configs",
        school_root / "runtime",
        school_root / "tests",
        school_root / "events",
    }

    for path in required_children:
        assert path.exists() and path.is_dir(), f"missing directory: {path}"

    required_configs = [
        school_root / "configs" / filename
        for filename in ("events.yaml", "game.yaml", "rooms.yaml", "schedule.yaml", "students.yaml",
                         "policies.yaml", "clubs.yaml", "curriculum.yaml", "staff.yaml")
    ]
    for path in required_configs:
        assert path.exists() and path.is_file(), f"missing config file: {path.name}"

    runtime_children = {
        school_root / "runtime" / "logs",
        school_root / "runtime" / "saves",
        school_root / "runtime" / "scenes",
    }
    for path in runtime_children:
        assert path.exists() and path.is_dir(), f"missing runtime directory: {path}"


def test_makefile_targets_present():
    project_root = Path(__file__).resolve().parents[2]
    makefile = project_root / "Makefile"
    text = read_text(makefile)
    for target in ("run:", "simulate:", "test:"):
        assert f"{target}\n" in text or f"{target}\r\n" in text, f"target `{target}` missing"


def test_requirements_minimal():
    project_root = Path(__file__).resolve().parents[2]
    requirements = project_root / "requirements.txt"
    allowed = {"pygame", "pyyaml", "pytest"}
    lines = {
        line.strip().lower()
        for line in read_text(requirements).splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    assert lines <= allowed, f"unexpected requirements: {sorted(lines - allowed)}"


def test_readme_documents_commands_and_controls():
    project_root = Path(__file__).resolve().parents[2]
    readme = project_root / "readme.md"
    text = read_text(readme).lower()
    for command in ("make run", "make simulate", "make test"):
        assert command in text, f"{command} missing from README"
    required_controls = {"p", "t", "e", "b", "l", "o", "esc", "enter"}
    for control in required_controls:
        assert control in text, f"control `{control}` missing from README"
