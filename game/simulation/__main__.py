from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from ..config import load_config
from ..interface import CommandDispatcher, CommandError, PrincipalControls
from . import Simulation, resolve_map_file


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the headless school simulation with activity logging.')
    parser.add_argument('--ticks', type=int, default=300, help='Number of ticks to simulate.')
    parser.add_argument('--profile', type=str, help='Configuration profile to load (overrides settings.yaml).')
    parser.add_argument('--map', dest='map_name', help='Map file or alias to load (e.g. campus_map_v1).')
    parser.add_argument(
        '--log-activities',
        nargs='?',
        const='-',
        default=None,
        help='Write activity events to PATH (JSON). Use "-" to print to stdout.',
    )
    parser.add_argument(
        '--commands',
        type=str,
        help='Path to a text file containing principal commands to execute before advancing.',
    )
    args = parser.parse_args()

    cfg = load_config(profile=args.profile)
    data_cfg = cfg.get('data', {})
    default_map = data_cfg.get('map_file', 'data/campus_map.json')
    map_path = resolve_map_file(args.map_name, default_map)

    simulation = Simulation(cfg, map_path=map_path)
    if args.commands:
        command_path = Path(args.commands)
        if not command_path.exists():
            raise FileNotFoundError(f"Command script {command_path} not found")
        controls = PrincipalControls(simulation)
        dispatcher = CommandDispatcher(controls)
        for raw_line in command_path.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                result = dispatcher.execute(line)
            except CommandError as exc:
                print(f"Command error for '{line}': {exc}", file=sys.stderr)
            else:
                print(result.message)
    simulation.advance(args.ticks)

    if args.log_activities:
        events = [asdict(event) for event in simulation.event_logger.iter_events()]
        payload = json.dumps(events, indent=2)
        if args.log_activities == '-':
            print(payload)
        else:
            output_path = Path(args.log_activities)
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload, encoding='utf-8')


if __name__ == '__main__':
    main()
