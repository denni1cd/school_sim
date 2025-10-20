from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import yaml

from ..actors.npc import NPC
from ..simulation.conflict_resolver import (
    ConflictRecord,
    detect_room_capacity_conflicts,
    resolve_with_staggering,
)
from ..simulation.schedule_generator import (
    DailySchedule,
    ScheduleAssignment,
    ScheduleTemplate,
    TravelEstimator,
    format_minutes,
    parse_duration,
    parse_hhmm,
)
from ..simulation.activities import ActivityCatalog, ActivityProfile


@dataclass
class ActivityDefinition:
    name: str
    duration: int
    location: str
    notes: Optional[str] = None


@dataclass
class ScheduledActivity:
    name: str
    duration: int
    location: str
    slot: Optional[str] = None
    notes: Optional[str] = None
    expected_travel: Optional[int] = None
    travel_buffer: int = 0
    profile: Optional[ActivityProfile] = None


class ScheduleSystem:
    def __init__(
        self,
        mapgrid,
        path: str,
        *,
        day_length_minutes: int = 1440,
        rng=None,
        activity_catalog: ActivityCatalog | None = None,
    ):
        self.mapgrid = mapgrid
        self.day_length_minutes = day_length_minutes
        self.rng = rng
        self.activity_catalog = activity_catalog
        roster_path = Path(path)
        if not roster_path.is_absolute():
            roster_path = (Path.cwd() / roster_path).resolve()
        if roster_path.suffix.lower() == '.json':
            self._init_from_legacy_json(roster_path)
            return

        roster_data = yaml.safe_load(roster_path.read_text(encoding="utf-8")) or {}

        activities_file = roster_data.get("activities_file")
        templates_file = roster_data.get("templates_file")
        assignments_data = roster_data.get("assignments", [])

        if not activities_file or not templates_file:
            raise ValueError("Roster configuration must include activities_file and templates_file")

        activities_path = Path(activities_file)
        if not activities_path.is_absolute():
            candidate = (roster_path.parent / activities_path).resolve()
            if candidate.exists():
                activities_path = candidate
            else:
                activities_path = (Path.cwd() / activities_path).resolve()
        templates_path = Path(templates_file)
        if not templates_path.is_absolute():
            candidate = (roster_path.parent / templates_path).resolve()
            if candidate.exists():
                templates_path = candidate
            else:
                templates_path = (Path.cwd() / templates_path).resolve()

        activities_raw = yaml.safe_load(activities_path.read_text(encoding="utf-8")) or {}
        activity_entries = activities_raw.get("activities", {})
        self.activity_definitions: Dict[str, ActivityDefinition] = {}
        for key, value in activity_entries.items():
            duration = int(value.get("duration", 0))
            location = str(value.get("location", ""))
            notes = value.get("notes")
            self.activity_definitions[key] = ActivityDefinition(
                name=key,
                duration=duration,
                location=location,
                notes=str(notes) if notes is not None else None,
            )

        templates_raw = yaml.safe_load(templates_path.read_text(encoding="utf-8")) or {}
        self.templates: Dict[str, ScheduleTemplate] = {
            name: ScheduleTemplate(name, variants, day_length_minutes=day_length_minutes)
            for name, variants in templates_raw.items()
        }

        self.assignments: List[ScheduleAssignment] = [
            ScheduleAssignment.from_dict(entry, templates=self.templates)
            for entry in assignments_data
        ]

        self.assignment_specs: Dict[str, Mapping[str, object]] = {
            str(entry.get("name")): entry
            for entry in assignments_data
            if isinstance(entry, Mapping) and entry.get("name")
        }

        self._daily_plan: Dict[str, List[DailySchedule]] = {}
        for assignment in self.assignments:
            blocks = assignment.apply()
            self._daily_plan[assignment.actor_id] = blocks

        self._finalize_setup()

    def _init_from_legacy_json(self, roster_path: Path) -> None:
        payload = json.loads(roster_path.read_text(encoding="utf-8"))
        activities = payload.get("activities", {})
        self.activity_definitions = {
            key: ActivityDefinition(
                name=key,
                duration=int(value.get("duration", 0)),
                location=str(value.get("location", "")),
                notes=str(value.get("notes")) if value.get("notes") is not None else None,
            )
            for key, value in activities.items()
        }
        self.templates = {}
        self.assignments = []
        npcs = payload.get("npcs", [])
        self.assignment_specs = {
            str(entry.get("name")): {"role": entry.get("role", "student")}
            for entry in npcs
            if isinstance(entry, Mapping)
        }
        self._daily_plan = {}
        for npc_data in npcs:
            if not isinstance(npc_data, Mapping):
                continue
            name = str(npc_data.get("name"))
            schedule_entries = npc_data.get("schedule", [])
            blocks: List[DailySchedule] = []
            for entry in schedule_entries:
                if not isinstance(entry, Mapping):
                    continue
                activity_id = str(entry.get("activity"))
                if activity_id not in self.activity_definitions:
                    continue
                minutes = self._hhmm_to_minutes(str(entry.get("time", "00:00")))
                jitter = int(entry.get("jitter", 0) or 0)
                if jitter and self.rng is not None:
                    minutes = (minutes + self.rng.randint(-jitter, jitter)) % self.day_length_minutes
                spec = self.activity_definitions[activity_id]
                blocks.append(
                    DailySchedule(
                        actor_id=name,
                        slot=activity_id,
                        activity_id=activity_id,
                        room_id=spec.location,
                        start_tick=minutes,
                        duration_minutes=spec.duration,
                        day_length_minutes=self.day_length_minutes,
                    )
                )
            blocks.sort(key=lambda block: block.start_tick)
            self._daily_plan[name] = blocks
        self._finalize_setup()

    def _finalize_setup(self) -> None:
        travel_estimator = TravelEstimator(self.mapgrid)
        travel_estimator.annotate(self._daily_plan, adjust_buffers=True)

        flat_blocks: List[DailySchedule] = [block for blocks in self._daily_plan.values() for block in blocks]
        self.detected_conflicts = []
        self.conflicts = []
        if flat_blocks:
            self.detected_conflicts = detect_room_capacity_conflicts(list(flat_blocks), self.mapgrid.rooms)
            self.conflicts = resolve_with_staggering(flat_blocks, self.mapgrid.rooms)
            travel_estimator.annotate(self._daily_plan, adjust_buffers=False)

        for blocks in self._daily_plan.values():
            blocks.sort(key=lambda block: block.start_tick)

        self.npcs = []
        self._default_spawn = self._choose_spawn()
        self.daily_plan = {actor_id: list(blocks) for actor_id, blocks in self._daily_plan.items()}

        for actor_id, blocks in self.daily_plan.items():
            schedule = self._build_schedule(blocks)
            spec = self.assignment_specs.get(actor_id, {})
            role_value = spec.get("role", "student") if spec else "student"
            role = str(role_value) if role_value else "student"
            spawn_x, spawn_y = self._spawn_point(blocks, role)
            npc = NPC(
                name=actor_id,
                x=spawn_x,
                y=spawn_y,
                role=role,
                schedule=schedule,
            )
            npc.daily_plan = list(blocks)
            self.npcs.append(npc)

    def override_plan(
        self,
        actor_id: str,
        overrides: Sequence[Mapping[str, object]],
        *,
        source: str = "principal_override",
    ) -> List[DailySchedule]:
        if actor_id not in self.daily_plan:
            raise KeyError(f"Unknown actor '{actor_id}'")

        day_length = self.day_length_minutes
        blocks: List[DailySchedule] = []
        for index, payload in enumerate(overrides):
            if not isinstance(payload, Mapping):
                continue
            activity_value = payload.get("activity")
            if not activity_value:
                raise ValueError("Override block requires an activity")
            start_value = payload.get("start")
            duration_value = payload.get("duration")
            room_value = payload.get("room")
            notes_value = payload.get("notes")
            travel_value = payload.get("travel_buffer")
            slot_value = payload.get("slot") or f"{source}_{index}"

            spec = self.activity_definitions.get(str(activity_value))
            start_tick = parse_hhmm(str(start_value)) if start_value else 0
            duration = (
                parse_duration(str(duration_value))
                if duration_value
                else (spec.duration if spec else 0)
            )
            room_id = (
                str(room_value)
                if room_value
                else (spec.location if spec else "")
            )
            notes = str(notes_value) if notes_value is not None else None
            travel_buffer = (
                parse_duration(str(travel_value))
                if travel_value
                else 0
            )

            block = DailySchedule(
                actor_id=actor_id,
                slot=str(slot_value),
                activity_id=str(activity_value),
                room_id=room_id,
                start_tick=start_tick % day_length,
                duration_minutes=max(duration, 0),
                day_length_minutes=day_length,
                notes=notes,
                travel_buffer=max(travel_buffer, 0),
            )
            blocks.append(block)

        if not blocks:
            raise ValueError("Override requires at least one block")

        blocks.sort(key=lambda item: item.start_tick)
        self._daily_plan[actor_id] = list(blocks)
        self.daily_plan[actor_id] = list(blocks)
        self.assignment_specs.setdefault(actor_id, {})["override_source"] = source

        self._recalculate_plans(actor_id=actor_id)
        return self.daily_plan[actor_id]

    def _recalculate_plans(self, actor_id: str | None = None) -> None:
        travel_estimator = TravelEstimator(self.mapgrid)
        travel_estimator.annotate(self.daily_plan, adjust_buffers=True)

        flat_blocks: List[DailySchedule] = [
            block
            for blocks in self.daily_plan.values()
            for block in blocks
        ]
        if flat_blocks:
            self.detected_conflicts = detect_room_capacity_conflicts(
                list(flat_blocks),
                self.mapgrid.rooms,
            )
            self.conflicts = resolve_with_staggering(flat_blocks, self.mapgrid.rooms)
            travel_estimator.annotate(self.daily_plan, adjust_buffers=False)
        else:
            self.detected_conflicts = []
            self.conflicts = []

        target_names = {actor_id} if actor_id else {npc.name for npc in self.npcs}
        for npc in self.npcs:
            if npc.name not in target_names:
                continue
            blocks = self.daily_plan.get(npc.name, [])
            npc.schedule = self._build_schedule(blocks)
            npc.daily_plan = list(blocks)
            npc.pending_schedule = None
            npc.pending_activity_start_minutes = None
            npc.pending_destination = None
            npc.target = None
            npc.path.clear()

        if actor_id and all(npc.name != actor_id for npc in self.npcs):
            blocks = self.daily_plan.get(actor_id, [])
            if blocks:
                schedule = self._build_schedule(blocks)
                spec = self.assignment_specs.get(actor_id, {})
                role_value = spec.get("role", "student") if spec else "student"
                role = str(role_value) if role_value else "student"
                spawn_x, spawn_y = self._spawn_point(blocks, role)
                npc = NPC(
                    name=actor_id,
                    x=spawn_x,
                    y=spawn_y,
                    role=role,
                    schedule=schedule,
                )
                npc.daily_plan = list(blocks)
                self.npcs.append(npc)

    def _build_schedule(self, blocks: List[DailySchedule]) -> List[Tuple[str, ScheduledActivity]]:
        schedule: List[Tuple[str, ScheduledActivity]] = []
        for block in blocks:
            spec = self.activity_definitions.get(block.activity_id)
            duration = block.duration_minutes
            location = block.room_id or (spec.location if spec else "")
            notes = block.notes if block.notes is not None else (spec.notes if spec else None)
            profile = self._resolve_profile(block.activity_id)
            activity = ScheduledActivity(
                name=block.activity_id,
                duration=duration,
                location=location,
                slot=block.slot,
                notes=notes,
                expected_travel=block.expected_travel,
                travel_buffer=block.travel_buffer,
                profile=profile,
            )
            schedule.append((format_minutes(block.start_tick), activity))
        schedule.sort(key=lambda item: self._hhmm_to_minutes(item[0]))
        return schedule

    def _spawn_point(self, blocks: List[DailySchedule], role: str | None) -> Tuple[int, int]:
        for block in blocks:
            room_name = block.room_id
            if not room_name:
                spec = self.activity_definitions.get(block.activity_id)
                room_name = spec.location if spec else None
            if room_name and room_name in self.mapgrid.rooms:
                interior = self.mapgrid.room_interior_targets(room_name)
                if interior:
                    return interior[0]
                return self.mapgrid.room_center(room_name)
        return self._choose_spawn(role=role)

    def _choose_spawn(self, role: str | None = None) -> Tuple[int, int]:
        candidates = list(self.mapgrid.spawn_points(role))
        if candidates:
            if self.rng is not None:
                return self.rng.choice(candidates)
            return candidates[0]

        if role:
            default = getattr(self, "_default_spawn", None)
            if default:
                return default

        dorm_names = [
            room.name
            for room in self.mapgrid.rooms.values()
            if (room.room_type or "").lower() == "dormitory"
        ]
        if dorm_names:
            return self.mapgrid.room_center(dorm_names[0])

        if self.mapgrid.rooms:
            room = next(iter(self.mapgrid.rooms.values()))
            rx, ry, rw, rh = room.rect
            return rx + rw // 2, ry + rh // 2

        return 0, 0

    @property
    def default_spawn(self) -> Tuple[int, int]:
        return self._default_spawn

    def update(self, hhmm: str) -> None:
        for npc in self.npcs:
            for time_str, activity in npc.schedule:
                if time_str != hhmm:
                    continue
                if npc.pending_schedule is not None:
                    continue
                if npc.current_activity and npc.current_activity.name == activity.name:
                    continue
                start_minutes = self._hhmm_to_minutes(time_str)
                npc.assign_activity(activity, start_minutes)
                break

    def _hhmm_to_minutes(self, hhmm: str) -> int:
        hours, minutes = map(int, hhmm.split(":"))
        return (hours * 60 + minutes) % self.day_length_minutes

    def _minutes_to_hhmm(self, minutes: int) -> str:
        minutes %= self.day_length_minutes
        hours, mins = divmod(minutes, 60)
        return f"{hours:02d}:{mins:02d}"

    def export_daily_plan(self, path: str | Path) -> None:
        output_path = Path(path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "actor_id",
                    "start_time",
                    "end_time",
                    "slot",
                    "activity",
                    "room",
                    "expected_travel_minutes",
                    "travel_buffer_minutes",
                    "notes",
                ]
            )
            for actor_id, blocks in sorted(self.daily_plan.items()):
                for block in sorted(blocks, key=lambda item: item.start_tick):
                    spec = self.activity_definitions.get(block.activity_id)
                    duration = block.duration_minutes
                    start_minutes = block.start_tick
                    end_minutes = start_minutes + duration
                    writer.writerow(
                        [
                            actor_id,
                            format_minutes(start_minutes),
                            format_minutes(end_minutes),
                            block.slot,
                            block.activity_id,
                            block.room_id or (spec.location if spec else ""),
                            block.expected_travel if block.expected_travel is not None else "",
                            block.travel_buffer,
                            block.notes or (spec.notes if spec else ""),
                        ]
                    )

    def _resolve_profile(self, activity_id: str) -> ActivityProfile | None:
        if self.activity_catalog is None:
            return None
        return self.activity_catalog.resolve(activity_id)

