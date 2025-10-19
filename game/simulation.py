from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable, List, Set, Tuple

import yaml

from .actors.base_actor import NPCState
from .actors.npc import NPC
from .core.map import MapGrid
from .core.time_clock import GameClock
from .systems.activity_system import ActivitySystem
from .systems.movement_system import MovementSystem
from .systems.schedule_system import ScheduleSystem

ROOT = Path(__file__).resolve().parents[1]


def resolve_data_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate


def _hhmm_to_minutes(hhmm: str) -> int:
    hours, minutes = map(int, hhmm.split(':'))
    return hours * 60 + minutes


class Simulation:
    """Core simulation loop shared by headless and interactive modes."""

    def __init__(self, cfg: dict, grid: MapGrid | None = None):
        self.cfg = cfg
        data_cfg = cfg.get('data', {})
        map_path = resolve_data_path(data_cfg.get('map_file', 'data/campus_map.json'))
        schedule_path = resolve_data_path(data_cfg.get('npc_schedule_file', 'data/npc_schedules.json'))
        self.grid = grid or MapGrid(str(map_path))
        self.rng = random.Random(cfg.get('random_seed', 1337))
        time_cfg = cfg['time']
        self.clock = GameClock(time_cfg['minutes_per_tick'], time_cfg['day_length_minutes'])
        self._minutes_per_tick = float(time_cfg['minutes_per_tick'])
        self._minute_accumulator = 0.0

        self.schedule_system = ScheduleSystem(
            self.grid,
            str(schedule_path),
            day_length_minutes=time_cfg['day_length_minutes'],
            rng=self.rng,
        )
        self.activity_system = ActivitySystem()
        self.movement_system = MovementSystem(self.grid)

        interactions_cfg = cfg.get('interactions', {})
        messages_path = resolve_data_path(interactions_cfg.get('messages_file', 'config/interactions.yaml'))
        self._interaction_messages = self._load_interaction_messages(messages_path)

        dorm_x, dorm_y = self.grid.room_center('Dorm')
        for npc in self.schedule_system.npcs:
            npc.x, npc.y = dorm_x, dorm_y
            npc.state = NPCState.IDLE
            npc.target = None
            npc.path.clear()

        self._prime_initial_activities()

    @property
    def npcs(self) -> List[NPC]:
        return self.schedule_system.npcs

    def _prime_initial_activities(self) -> None:
        day_length = self.clock.day_length_minutes
        current_minutes = int(self.clock.minute) % day_length
        for npc in self.npcs:
            if not npc.schedule:
                continue
            chosen_activity = None
            chosen_minutes = None
            for time_str, activity in npc.schedule:
                minutes = _hhmm_to_minutes(time_str)
                if minutes <= current_minutes:
                    chosen_activity = activity
                    chosen_minutes = minutes
                else:
                    break
            if chosen_activity is None:
                continue
            npc.assign_activity(chosen_activity, chosen_minutes)
            destination = self._select_destination(chosen_activity.location)
            npc.pending_destination = destination

    def tick(self) -> None:
        current_time = self.clock.get_time_str()
        self.schedule_system.update(current_time)

        day_length = self.clock.day_length_minutes
        current_minutes = int(self.clock.minute) % day_length
        occupied: Set[Tuple[int, int]] = {(npc.x, npc.y) for npc in self.npcs}

        for npc in self.npcs:
            if npc.pending_activity:
                room = self.grid.room_for_position(npc.x, npc.y)
                if room and room.name == npc.pending_activity.location:
                    npc.pending_destination = None
                    npc.target = None
                    npc.path.clear()
                    npc.state = NPCState.IDLE
                    self.activity_system.start_if_ready(npc, current_minutes=current_minutes, day_length_minutes=day_length)
                    continue
                if npc.pending_destination is None:
                    npc.pending_destination = self._select_destination(npc.pending_activity.location)
                destination = npc.pending_destination
                if (npc.x, npc.y) != destination:
                    npc.set_target(*destination)
                else:
                    npc.target = None
                    self.activity_system.start_if_ready(npc, current_minutes=current_minutes, day_length_minutes=day_length)

            if npc.target:
                blocked = occupied - {(npc.x, npc.y)}
                self.movement_system.plan_if_needed(npc, blocked=blocked)
                occupied.discard((npc.x, npc.y))
                arrived = self.movement_system.step(npc, occupied, steps=1)
                occupied.add((npc.x, npc.y))
                if arrived:
                    self.activity_system.on_arrival(npc, current_minutes=current_minutes, day_length_minutes=day_length)
            else:
                self.activity_system.start_if_ready(npc, current_minutes=current_minutes, day_length_minutes=day_length)

        self._minute_accumulator += self._minutes_per_tick
        while self._minute_accumulator >= 1.0:
            for npc in self.npcs:
                self.activity_system.tick_minute(npc)
            self._minute_accumulator -= 1.0

        self.clock.tick()

    def advance(self, ticks: int) -> None:
        for _ in range(ticks):
            self.tick()

    def iter_npc_positions(self) -> Iterable[tuple[str, tuple[int, int]]]:
        for npc in self.npcs:
            yield npc.name, (npc.x, npc.y)

    def snapshot(self) -> dict:
        return {
            'time': self.clock.get_time_str(),
            'npc_states': {npc.name: {'state': npc.state.value, 'position': (npc.x, npc.y)} for npc in self.npcs},
        }

    def interact_with(self, npc: NPC) -> str:
        message = self._format_interaction(npc)
        if message:
            return message
        activity_name = getattr(getattr(npc, 'current_activity', None), 'name', None)
        if activity_name:
            description = activity_name.replace('_', ' ')
            return f"(Placeholder) {npc.name} says: I'm in the middle of {description}."
        return f"(Placeholder) {npc.name} says hello."

    def _select_destination(self, room_name: str) -> Tuple[int, int]:
        room = self.grid.rooms[room_name]
        if room.doors:
            return self.rng.choice(room.doors)
        return self.grid.random_room_tile(room_name, self.rng)

    def _load_interaction_messages(self, path: Path) -> dict:
        if not path.exists():
            return {
                'default': "(Placeholder) {name} says hello.",
                'rooms': {},
                'roles': {},
                'activities': {},
            }
        data = yaml.safe_load(path.read_text()) or {}
        return {
            'default': data.get('default', "(Placeholder) {name} says hello."),
            'rooms': dict(data.get('rooms', {})),
            'roles': dict(data.get('roles', {})),
            'activities': dict(data.get('activities', {})),
        }

    def _format_interaction(self, npc: NPC) -> str | None:
        messages = getattr(self, '_interaction_messages', None)
        if not messages:
            return None
        activity_name = getattr(getattr(npc, 'current_activity', None), 'name', None)
        room = self.grid.room_for_position(npc.x, npc.y)
        template = None
        if activity_name:
            template = messages['activities'].get(activity_name)
        if template is None and room is not None:
            template = messages['rooms'].get(room.name)
        role = getattr(npc, 'role', '')
        if template is None and role:
            template = messages['roles'].get(role)
        if template is None:
            template = messages.get('default')
        if not template:
            return None
        activity_desc = activity_name.replace('_', ' ') if activity_name else ''
        context = {
            'name': npc.name,
            'role': role,
            'activity': activity_name or '',
            'activity_description': activity_desc,
            'room': room.name if room is not None else '',
        }
        return template.format(**context)
