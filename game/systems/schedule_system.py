from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..actors.npc import NPC


@dataclass
class Activity:
    name: str
    duration: int
    location: str


class ScheduleSystem:
    def __init__(self, mapgrid, path: str, *, day_length_minutes: int = 1440, rng=None):
        self.mapgrid = mapgrid
        self.day_length_minutes = day_length_minutes
        self.rng = rng
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.activities: Dict[str, Activity] = {
            key: Activity(key, value["duration"], value["location"])
            for key, value in data["activities"].items()
        }
        self.npcs: List[NPC] = []
        self._default_spawn = self.mapgrid.room_center("Dorm")
        for npc_data in data["npcs"]:
            schedule = self._build_schedule(npc_data["schedule"])
            spawn_x, spawn_y = self._spawn_point(schedule)
            npc = NPC(
                name=npc_data["name"],
                x=spawn_x,
                y=spawn_y,
                role=npc_data.get("role", "student"),
                schedule=schedule,
            )
            self.npcs.append(npc)

    def _build_schedule(self, entries: List[Dict]) -> List[Tuple[str, Activity]]:
        schedule: List[Tuple[str, Activity]] = []
        for entry in entries:
            activity = self.activities[entry["activity"]]
            minutes = self._hhmm_to_minutes(entry["time"])
            jitter = int(entry.get("jitter", 0) or 0)
            if jitter and self.rng is not None:
                minutes = (minutes + self.rng.randint(-jitter, jitter)) % self.day_length_minutes
            time_str = self._minutes_to_hhmm(minutes)
            schedule.append((time_str, activity))
        schedule.sort(key=lambda item: self._hhmm_to_minutes(item[0]))
        return schedule

    def _spawn_point(self, schedule: List[Tuple[str, Activity]]) -> Tuple[int, int]:
        if schedule:
            location = schedule[0][1].location
            return self.mapgrid.room_center(location)
        return self._default_spawn

    def update(self, hhmm: str) -> None:
        for npc in self.npcs:
            for time_str, activity in npc.schedule:
                if time_str != hhmm:
                    continue
                if npc.pending_activity is not None:
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