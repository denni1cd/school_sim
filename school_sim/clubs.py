from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .timetable import minutes_to_timestr


@dataclass
class Club:
    club_id: str
    name: str
    room: str
    meets_at: str
    capacity: int
    effects: Dict[str, float]
    members: List[str] = field(default_factory=list)

    def has_meeting_at(self, time_minutes: int) -> bool:
        return minutes_to_timestr(time_minutes) == self.meets_at


class ClubsManager:
    def __init__(self, config: dict, *, budget_callback):
        self._clubs: Dict[str, Club] = {}
        self._active_sessions: Dict[str, float] = {}
        self._costs = (config or {}).get("costs", {})
        self._budget_callback = budget_callback
        for entry in (config or {}).get("clubs", []):
            club = Club(
                club_id=entry.get("id"),
                name=entry.get("name") or entry.get("id", "Club"),
                room=entry.get("room", "Classroom"),
                meets_at=entry.get("meets_at", "08:30"),
                capacity=int(entry.get("capacity", 0)),
                effects={k: float(v) for k, v in (entry.get("effects") or {}).items()},
            )
            if club.club_id:
                self._clubs[club.club_id] = club

    @property
    def clubs(self) -> Iterable[Club]:
        return self._clubs.values()

    def get(self, club_id: Optional[str]) -> Optional[Club]:
        if not club_id:
            return None
        return self._clubs.get(club_id)

    def assign_student(self, student, club_id: str) -> bool:
        club = self._clubs.get(club_id)
        if not club:
            return False

        if getattr(student, "club_id", None) == club_id:
            return True

        cost = int(self._costs.get("assign_student", 0))
        if cost:
            reason = f"Club assignment: {student.name} -> {club.name}"
            if not self._budget_callback(-cost, reason=reason):
                return False

        if getattr(student, "club_id", None):
            self.remove_student(student, student.club_id)

        student.club_id = club_id
        if student.name not in club.members:
            club.members.append(student.name)
        return True

    def remove_student(self, student, club_id: str) -> None:
        club = self._clubs.get(club_id)
        if not club:
            return
        if student.name in club.members:
            club.members.remove(student.name)
        if getattr(student, "club_id", None) == club_id:
            student.club_id = None

    def apply_club_tick(self, world, dt_minutes: float) -> None:
        self._start_sessions(world.time_minutes)
        finished = []
        for club_id, remaining in list(self._active_sessions.items()):
            club = self._clubs.get(club_id)
            if not club:
                finished.append(club_id)
                continue
            self._process_club_meeting(world, club, dt_minutes)
            remaining -= dt_minutes
            if remaining <= 0:
                finished.append(club_id)
            else:
                self._active_sessions[club_id] = remaining
        for club_id in finished:
            self._active_sessions.pop(club_id, None)

    def _start_sessions(self, time_minutes: int) -> None:
        for club in self._clubs.values():
            if club.has_meeting_at(time_minutes):
                self._active_sessions[club.club_id] = 30.0

    def _process_club_meeting(self, world, club: Club, dt_minutes: float) -> None:
        if not club.members:
            return

        attendees: List = []
        for name in club.members:
            student = world.get_student(name)
            if student:
                attendees.append(student)
        if not attendees:
            return

        total = len(attendees)
        effective_capacity = club.capacity if club.capacity > 0 else total
        engaged = min(effective_capacity, total)

        for idx, student in enumerate(attendees):
            if student.target_room != club.room:
                student.target_room = club.room

            over_capacity = club.capacity > 0 and idx >= club.capacity
            if over_capacity:
                self._apply_overflow_penalty(world, student, dt_minutes)
                continue

            for need, delta in club.effects.items():
                if need in student.needs:
                    student.needs[need] = _clamp(student.needs[need] + delta * dt_minutes)

        if total > 0:
            ratio = engaged / total if total else 0.0
            world.register_club_engagement(ratio)

    def _apply_overflow_penalty(self, world, student, dt_minutes: float) -> None:
        student.needs["stress"] = _clamp(student.needs["stress"] + 0.5 * dt_minutes)
        world.record_event(
            event_id="club_overflow",
            caption=f"{student.name} overwhelmed by club overflow.",
            time_str=minutes_to_timestr(world.time_minutes),
        )
        world.apply_club_penalty(0.3 * (dt_minutes / 10.0))


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
