import json
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class Room:
    name: str
    rect: Tuple[int, int, int, int]
    doors: Tuple[Tuple[int, int], ...]
    room_type: str | None = None
    capacity: int | None = None
    default_activity: str | None = None

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
            rooms[room_data['name']] = Room(
                room_data['name'],
                rect,
                doors,
                room_data.get('room_type'),
                room_data.get('capacity'),
                room_data.get('default_activity'),
            )
        self.rooms = rooms

        spawns: Dict[str, Tuple[Tuple[int, int], ...]] = {}
        for key, points in data.get('spawns', {}).items():
            spawns[key.lower()] = tuple(tuple(pt) for pt in points)
        self.spawns = spawns

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.passability[y][x] == 1

    def room_center(self, name: str) -> Tuple[int, int]:
        rx, ry, rw, rh = self.rooms[name].rect
        return rx + rw // 2, ry + rh // 2

    def room_entry_points(self, name: str) -> Tuple[Tuple[int, int], ...]:
        return self.rooms[name].doors

    def room_interior_targets(self, name: str) -> Tuple[Tuple[int, int], ...]:
        room = self.rooms[name]
        rx, ry, rw, rh = room.rect
        interior: list[Tuple[int, int]] = []
        for door_x, door_y in room.doors:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = door_x + dx, door_y + dy
                if not (rx <= nx < rx + rw and ry <= ny < ry + rh):
                    continue
                if self.walkable(nx, ny):
                    interior.append((nx, ny))
        return tuple(dict.fromkeys(interior))

    def random_room_tile(self, name: str, rng) -> Tuple[int, int]:
        rx, ry, rw, rh = self.rooms[name].rect
        x = rng.randint(rx, rx + rw - 1)
        y = rng.randint(ry, ry + rh - 1)
        if self.walkable(x, y):
            return x, y

        # Fallback: search for the nearest walkable tile inside the room.
        for radius in range(1, max(rw, rh) + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if not (rx <= nx < rx + rw and ry <= ny < ry + rh):
                        continue
                    if self.walkable(nx, ny):
                        return nx, ny
        return x, y

    def room_for_position(self, x: int, y: int):
        for room in self.rooms.values():
            if room.contains(x, y):
                return room
        return None

    def spawn_points(self, role: str | None = None) -> Tuple[Tuple[int, int], ...]:
        candidates: list[Tuple[int, int]] = []
        if role:
            role_key = role.lower()
            candidates.extend(self.spawns.get(role_key, ()))
        candidates.extend(self.spawns.get('default', ()))
        return tuple(candidates)

