from typing import Dict, List
from room import Room
from student import Student
from timetable import Timetable, minutes_to_timestr

class World:
    def __init__(self, rooms: Dict[str, Room], students: List[Student], timetable: Timetable):
        self.rooms = rooms
        self.students = students
        self.timetable = timetable
        self.time_minutes = 8 * 60  # start at 08:00

    def tick(self, dt_minutes: int = 1):
        """Advance world by dt_minutes."""
        self.time_minutes += dt_minutes
        timestr = minutes_to_timestr(self.time_minutes)

        for s in self.students:
            # 1. Passive need decay
            s.decay_needs(dt_minutes)

            # 2. Decide where to go
            homeroom_schedule = self.timetable.homeroom_schedules.get(s.homeroom, {})
            s.choose_target(timestr, homeroom_schedule, self.rooms)

            # 3. Move to the target (instant in Milestone 2)
            s.move_towards_target()

            # 4. Apply room effects
            current_room_obj = self.rooms.get(s.current_room)
            if current_room_obj:
                current_room_obj.apply_effects(s, dt_minutes)

            # 5. Record attendance / discipline tracking
            expected = self.timetable.expected_room_for(s.homeroom, timestr)
            s.record_attendance(timestr, expected)

    def get_debug_snapshot(self):
        """Return lightweight info for rendering / console log."""
        timestr = minutes_to_timestr(self.time_minutes)
        data = {
            "time": timestr,
            "students": []
        }
        for s in self.students:
            data["students"].append({
                "name": s.name,
                "room": s.current_room,
                "target": s.target_room,
                "needs": s.needs.copy(),
                "discipline_risk": s.stats["discipline_risk"],
            })
        return data
