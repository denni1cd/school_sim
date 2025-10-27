import time
import yaml
from room import Room
from student import Student
from timetable import Timetable
from world import World

def load_rooms(path="configs/rooms.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    rooms = {}
    for name, info in data["rooms"].items():
        rooms[name] = Room(
            name=name,
            room_type=info["room_type"],
            x=info["x"],
            y=info["y"],
            width=info["width"],
            height=info["height"],
        )
    return rooms

def load_students(path="configs/students.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    students = []
    for s in data["students"]:
        students.append(
            Student(
                name=s["name"],
                homeroom=s["homeroom"],
                current_room=s["current_room"],
            )
        )
    return students

def load_timetable(path="configs/schedule.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Timetable(homeroom_schedules=data)

def main():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    world = World(rooms, students, timetable)

    # Simple loop: 20 ticks = 20 minutes
    for _ in range(20):
        world.tick(dt_minutes=1)
        snapshot = world.get_debug_snapshot()

        # clear screen-ish
        print("\n" + "=" * 60)
        print(f"Time: {snapshot['time']}")
        for s in snapshot["students"]:
            print(
                f"{s['name']:6} | room={s['room']:10} -> target={s['target']:10} "
                f"| hunger={s['needs']['hunger']:.1f} "
                f"energy={s['needs']['energy']:.1f} "
                f"stress={s['needs']['stress']:.1f} "
                f"| discipline_risk={s['discipline_risk']:.1f}"
            )

        time.sleep(0.25)

if __name__ == "__main__":
    main()
