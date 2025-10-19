
from __future__ import annotations

import argparse
import random
from pathlib import Path

from .config import load_config
from .simulation import Simulation

ROOT = Path(__file__).resolve().parents[1]


def main(ticks: int = 300, verbose: bool = False, profile: str | None = None):
    cfg = load_config(profile=profile)
    random.seed(cfg.get('random_seed', 1337))
    simulation = Simulation(cfg)
    simulation.advance(ticks)
    snapshot = simulation.snapshot()

    if verbose:
        print(f"Simulated {ticks} ticks -> game time {snapshot['time']}")
        for name, info in snapshot['npc_states'].items():
            state = info['state']
            pos = info['position']
            print(f"  {name:<8} state={state:<16} position={pos}")

    return snapshot


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the headless school simulation.')
    parser.add_argument('--ticks', type=int, default=300, help='Number of ticks to simulate.')
    parser.add_argument('--profile', type=str, help='Configuration profile to load (overrides settings.yaml).')
    parser.add_argument('--verbose', action='store_true', help='Print snapshot details after simulation.')
    args = parser.parse_args()
    main(ticks=args.ticks, verbose=args.verbose, profile=args.profile)
