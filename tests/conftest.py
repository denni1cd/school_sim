import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.config import load_config
from game.simulation import Simulation


@pytest.fixture
def simulation() -> Simulation:
    cfg = load_config()
    return Simulation(cfg)
