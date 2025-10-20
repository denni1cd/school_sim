from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable, List, Set, Tuple, TYPE_CHECKING

import yaml

from ..actors.base_actor import NPCState
from ..actors.npc import NPC
from ..core.map import MapGrid
from ..core.time_clock import GameClock
from ..logging import EventLogger
from ..systems.activity_system import ActivitySystem
from ..systems.movement_system import MovementSystem
from ..world import RoomManager
from .activities import ActivityCatalog

if TYPE_CHECKING:
    from ..systems.schedule_system import ScheduleSystem

ROOT = Path(__file__).resolve().parents[2]

__all__ = [
    "Simulation",
    "resolve_data_path",
    "resolve_map_file",
]


def resolve_data_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate


def resolve_map_file(map_option: str | Path | None, default: str | Path) -> Path:
    if not map_option:
        return resolve_data_path(default)

    candidate = Path(map_option)
    if not candidate.suffix:
        alias_lower = candidate.name.lower()
        alias_map = {
            'campus_map': 'data/campus_map_v1.json',
            'campus_map_v1': 'data/campus_map_v1.json',
            'v1': 'data/campus_map_v1.json',
        }
        if alias_lower in alias_map:
            return resolve_data_path(alias_map[alias_lower])

        alias = candidate.name
        data_dir = ROOT / 'data'
        for pattern in (f'{alias}.json', f'campus_map_{alias}.json'):
            alias_candidate = data_dir / pattern
            if alias_candidate.exists():
                return alias_candidate

    return resolve_data_path(candidate)


def _hhmm_to_minutes(hhmm: str) -> int:
    hours, minutes = map(int, hhmm.split(':'))
    return hours * 60 + minutes


class Simulation:
    """Core simulation loop shared by headless and interactive modes."""

    def __init__(
        self,
        cfg: dict,
        grid: MapGrid | None = None,
        *,
        map_path: str | Path | None = None,
        schedule_path: str | Path | None = None,
    ) -> None:
        self.cfg = cfg
        data_cfg = cfg.get('data', {})
        default_map = data_cfg.get('map_file', 'data/campus_map.json')
        resolved_map = resolve_map_file(map_path, default_map)
        schedule_source = schedule_path or data_cfg.get('npc_schedule_file', 'data/npc_schedules.json')
        resolved_schedule = resolve_data_path(schedule_source)
        self.grid = grid or MapGrid(str(resolved_map))
        self.rng = random.Random(cfg.get('random_seed', 1337))
        time_cfg = cfg['time']
        self.clock = GameClock(time_cfg['minutes_per_tick'], time_cfg['day_length_minutes'])
        self._minutes_per_tick = float(time_cfg['minutes_per_tick'])
        self._minute_accumulator = 0.0

        activities_cfg = cfg.get('activities', {})
        catalog_path = resolve_data_path(activities_cfg.get('catalog_file', 'config/activities.yaml'))
        self.activity_catalog = ActivityCatalog.load(catalog_path)
        self.room_manager = RoomManager(self.grid)
        self.event_logger = EventLogger()

        from ..systems.schedule_system import ScheduleSystem  # avoid circular import

        self.schedule_system = ScheduleSystem(
            self.grid,
            str(resolved_schedule),
            day_length_minutes=time_cfg['day_length_minutes'],
            rng=self.rng,
            activity_catalog=self.activity_catalog,
        )
        self.activity_system = ActivitySystem(
            catalog=self.activity_catalog,
            room_manager=self.room_manager,
            event_logger=self.event_logger,
        )
        self.movement_system = MovementSystem(self.grid)

        interactions_cfg = cfg.get('interactions', {})
        messages_path = resolve_data_path(interactions_cfg.get('messages_file', 'config/interactions.yaml'))
        self._interaction_messages = self._load_interaction_messages(messages_path)

        for npc in self.schedule_system.npcs:
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
            block = npc.pending_schedule
            if block:
                room = self.grid.room_for_position(npc.x, npc.y)
                if room and room.name == block.location:
                    npc.pending_destination = None
                    npc.target = None
                    npc.path.clear()
                    npc.state = NPCState.IDLE
                    self.activity_system.start_if_ready(
                        npc,
                        current_minutes=current_minutes,
                        day_length_minutes=day_length,
                    )
                    continue
                if npc.pending_destination is None:
                    npc.pending_destination = self._select_destination(block.location)
                destination = npc.pending_destination
                if (npc.x, npc.y) != destination:
                    npc.set_target(*destination)
                else:
                    npc.target = None
                    self.activity_system.start_if_ready(
                        npc,
                        current_minutes=current_minutes,
                        day_length_minutes=day_length,
                    )

            if npc.target:
                blocked = occupied - {(npc.x, npc.y)}
                self.movement_system.plan_if_needed(npc, blocked=blocked)
                occupied.discard((npc.x, npc.y))
                arrived = self.movement_system.step(npc, occupied, steps=1)
                occupied.add((npc.x, npc.y))
                if arrived:
                    self.activity_system.on_arrival(
                        npc,
                        current_minutes=current_minutes,
                        day_length_minutes=day_length,
                    )
            else:
                self.activity_system.start_if_ready(
                    npc,
                    current_minutes=current_minutes,
                    day_length_minutes=day_length,
                )

        self._minute_accumulator += self._minutes_per_tick
        minute_cursor = int(self.clock.minute) % day_length
        while self._minute_accumulator >= 1.0:
            minute_cursor = (minute_cursor + 1) % day_length
            for npc in self.npcs:
                self.activity_system.tick_minute(
                    npc,
                    current_minutes=minute_cursor,
                )
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
            'npc_states': {
                npc.name: {'state': npc.state.value, 'position': (npc.x, npc.y)}
                for npc in self.npcs
            },
        }

    def interact_with(self, npc: NPC) -> str:
        message = self._format_interaction(npc)
        if message:
            return message
        activity = getattr(npc, 'current_activity', None)
        if activity:
            label = getattr(activity, 'label', getattr(activity, 'name', 'an activity'))
            room_label = getattr(activity, 'room_id', 'somewhere')
            return f"(Placeholder) {npc.name} is {label.lower()} in {room_label}."
        return f"(Placeholder) {npc.name} says hello."

    def _select_destination(self, room_name: str) -> Tuple[int, int]:
        room = self.grid.rooms[room_name]
        interior = self.grid.room_interior_targets(room_name)
        if interior:
            return self.rng.choice(interior)
        if room.doors:
            walkable_doors = [door for door in room.doors if self.grid.walkable(*door)]
            if walkable_doors:
                return self.rng.choice(walkable_doors)
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
        activity = getattr(npc, 'current_activity', None)
        activity_name = getattr(activity, 'name', None)
        interaction_key = getattr(activity, 'interaction_key', None)
        room = self.grid.room_for_position(npc.x, npc.y)
        template = None
        if interaction_key:
            template = messages['activities'].get(interaction_key)
        if template is None and activity_name:
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
        activity_label = None
        if activity is not None:
            activity_label = getattr(activity, 'label', None)
        if not activity_label and activity_name:
            activity_label = activity_name.replace('_', ' ')
        metadata = getattr(getattr(activity, 'state', None), 'metadata', {}) or {}
        context = {
            'name': npc.name,
            'role': role,
            'activity': activity_label or '',
            'activity_description': activity_label or '',
            'room': room.name if room is not None else '',
            'activity_state': metadata,
        }
        return template.format(**context)
