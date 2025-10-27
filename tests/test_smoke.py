from room import Room
from student import Student
from timetable import Timetable
from world import World

def test_world_ticks_without_crashing():
    rooms = {
        "ClassroomA": Room("ClassroomA", "classroom", 0, 0, 10, 10),
        "Cafeteria": Room("Cafeteria", "cafeteria", 0, 0, 10, 10),
        "DormA": Room("DormA", "dorm", 0, 0, 10, 10),
        "Lounge": Room("Lounge", "lounge", 0, 0, 10, 10),
        "BathroomA": Room("BathroomA", "bathroom", 0, 0, 10, 10),
    }

    students = [
        Student(name="TestGirl", homeroom="homeroom_A", current_room="DormA")
    ]

    timetable = Timetable(
        homeroom_schedules={
            "homeroom_A": {
                "08:00": "ClassroomA",
                "09:00": "ClassroomA",
            }
        }
    )

    world = World(rooms, students, timetable)

    for _ in range(5):
        world.tick(dt_minutes=1)

    snapshot = world.get_debug_snapshot()
    assert "students" in snapshot
    assert len(snapshot["students"]) == 1
