from school_sim.room import Room
from school_sim.student import Student
from school_sim.timetable import Timetable
from school_sim.world import World


def test_students_spread_positions():
    room = Room(name="ClassroomA", room_type="classroom", x=50, y=70, width=180, height=140)
    students = [
        Student(name="Alice", homeroom="homeroom_A", current_room="ClassroomA"),
        Student(name="Becca", homeroom="homeroom_A", current_room="ClassroomA"),
        Student(name="Chloe", homeroom="homeroom_A", current_room="ClassroomA"),
    ]
    timetable = Timetable({"homeroom_A": {"08:00": "ClassroomA"}})
    world = World({room.name: room}, students, timetable)

    world._spread_students_in_rooms()
    positions = {(round(student.x, 2), round(student.y, 2)) for student in students}
    assert len(positions) == len(students)
    for student in students:
        assert room.x <= student.x <= room.x + room.width
        assert room.y <= student.y <= room.y + room.height
