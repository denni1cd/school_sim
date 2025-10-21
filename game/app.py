
from __future__ import annotations

import argparse
import random
from pathlib import Path

from .config import load_config
from .simulation import Simulation, resolve_map_file

ROOT = Path(__file__).resolve().parents[1]


def main(
    ticks: int = 300,
    verbose: bool = False,
    profile: str | None = None,
    map_override: str | None = None,
    dump_daily_plan: str | None = None,
):
    cfg = load_config(profile=profile)
    random.seed(cfg.get('random_seed', 1337))
    data_cfg = cfg.get('data', {})
    default_map = data_cfg.get('map_file', 'data/campus_map.json')
    map_path = resolve_map_file(map_override, default_map)
    simulation = Simulation(cfg, map_path=map_path)
    simulation.advance(ticks)
    snapshot = simulation.snapshot()

    if dump_daily_plan:
        simulation.schedule_system.export_daily_plan(dump_daily_plan)

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
    parser.add_argument(
        '--map',
        dest='map_name',
        help='Map file or alias to load (e.g. campus_map_v1 or data/campus_map_v1.json).',
    )
    parser.add_argument('--verbose', action='store_true', help='Print snapshot details after simulation.')
    parser.add_argument(
        '--dump-daily-plan',
        dest='dump_daily_plan',
        help='Write the generated daily plan to CSV at the given path.',
    )
    args = parser.parse_args()
    main(
        ticks=args.ticks,
        verbose=args.verbose,
        profile=args.profile,
        map_override=args.map_name,
        dump_daily_plan=args.dump_daily_plan,
    )
