from __future__ import annotations

from typing import Dict, List, Optional

from events.event_bus import EventBus
from room import Room
from student import Student
from timetable import Timetable, minutes_to_timestr


class World:
    def __init__(
        self,
        rooms: Dict[str, Room],
        students: List[Student],
        timetable: Timetable,
        event_bus: Optional[EventBus] = None,
    ):
        self.rooms = rooms
        self.students = students
        self.timetable = timetable
        self.event_bus = event_bus
        self.time_minutes = 8 * 60  # start at 08:00

        for student in self.students:
            room = self.rooms.get(student.current_room)
            if room:
                student.x = room.x + room.width / 2.0
                student.y = room.y + room.height / 2.0

    def tick(self, dt_minutes: int = 1):
        """Advance world by dt_minutes."""
        self.time_minutes += dt_minutes
        timestr = minutes_to_timestr(self.time_minutes)
        hour_slot = f"{timestr[:2]}:00"

        if self.event_bus:
            self.event_bus.emit(
                "time_tick",
                {"time_minutes": self.time_minutes, "time_str": timestr},
            )

        for student in self.students:
            previous_room = student.current_room
            student.decay_needs(dt_minutes)

            homeroom_schedule = self.timetable.homeroom_schedules.get(student.homeroom, {})
            student.choose_target(hour_slot, homeroom_schedule, self.rooms)
            student.move_towards_target(self.rooms, dt_minutes)

            if previous_room != student.current_room:
                self._emit_room_transition(student, previous_room, student.current_room)

            if not student.is_traveling():
                current_room_obj = self.rooms.get(student.current_room)
                if current_room_obj:
                    deltas = current_room_obj.apply_effects(student, dt_minutes)
                    if self.event_bus and deltas:
                        self.event_bus.emit(
                            "needs_update",
                            {
                                "student": student,
                                "room": student.current_room,
                                "deltas": deltas,
                            },
                        )

            expected = self.timetable.expected_room_for(student.homeroom, hour_slot)
            student.record_attendance(hour_slot, expected, traveling=student.is_traveling())

    def _emit_room_transition(self, student: Student, previous_room: Optional[str], current_room: Optional[str]) -> None:
        if not self.event_bus:
            return
        if previous_room:
            self.event_bus.emit(
                "room_exit",
                {"student": student, "room": previous_room},
            )
        if current_room:
            self.event_bus.emit(
                "room_enter",
                {"student": student, "room": current_room},
            )

    def get_debug_snapshot(self):
        """Return lightweight info for rendering / console log."""
        timestr = minutes_to_timestr(self.time_minutes)
        data = {
            "time": timestr,
            "students": []
        }
        for student in self.students:
            data["students"].append({
                "name": student.name,
                "room": student.current_room,
                "target": student.target_room,
                "needs": student.needs.copy(),
                "discipline_risk": student.stats["discipline_risk"],
            })
        return data
