import json
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class Room:
    name: str
    rect: Tuple[int, int, int, int]
    doors: Tuple[Tuple[int, int], ...]

    def contains(self, x: int, y: int) -> bool:
        rx, ry, rw, rh = self.rect
        return rx <= x < rx + rw and ry <= y < ry + rh


class MapGrid:
    def __init__(self, path: str):
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        self.tile_size = data['tile_size']
        self.width = data['width']
        self.height = data['height']
        self.passability = data['passability']

        rooms: Dict[str, Room] = {}
        for room_data in data.get('rooms', []):
            rect = tuple(room_data['rect'])
            doors = tuple(tuple(pt) for pt in room_data.get('doors', []))
            rooms[room_data['name']] = Room(room_data['name'], rect, doors)
        self.rooms = rooms

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.passability[y][x] == 1

    def room_center(self, name: str) -> Tuple[int, int]:
        rx, ry, rw, rh = self.rooms[name].rect
        return rx + rw // 2, ry + rh // 2

    def room_entry_points(self, name: str) -> Tuple[Tuple[int, int], ...]:
        return self.rooms[name].doors

    def random_room_tile(self, name: str, rng) -> Tuple[int, int]:
        rx, ry, rw, rh = self.rooms[name].rect
        x = rng.randint(rx, rx + rw - 1)
        y = rng.randint(ry, ry + rh - 1)
        return x, y

    def room_for_position(self, x: int, y: int):
        for room in self.rooms.values():
            if room.contains(x, y):
                return room
        return None

