from pathlib import Path

from headless import run_headless


def test_m3_headless_log(tmp_path: Path):
    log_path = tmp_path / "sim_log.txt"
    run_headless(ticks=5, log_path=log_path)
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) > 0
