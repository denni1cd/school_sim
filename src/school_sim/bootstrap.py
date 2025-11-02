"""
Core configuration loaders shared across interactive and headless modes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .room import Room
from .student import Student
from .timetable import Timetable


def load_rooms(path: str = "configs/rooms.yaml") -> Dict[str, Room]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {
        name: Room(
            name=name,
            room_type=info["room_type"],
            x=info["x"],
            y=info["y"],
            width=info["width"],
            height=info["height"],
        )
        for name, info in data["rooms"].items()
    }


def load_students(path: str = "configs/students.yaml") -> List[Student]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Student(**entry) for entry in data["students"]]


def load_timetable(path: str = "configs/schedule.yaml") -> Timetable:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Timetable(homeroom_schedules=data)
