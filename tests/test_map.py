from pathlib import Path

from pathlib import Path

from game.core.map import MapGrid


def _load_grid() -> MapGrid:
    return MapGrid(str(Path('data') / 'campus_map_v1.json'))


def test_room_tiles_are_walkable():
    grid = _load_grid()
    for room in grid.rooms.values():
        rx, ry, rw, rh = room.rect
        for yy in range(ry, ry + rh):
            for xx in range(rx, rx + rw):
                assert grid.walkable(xx, yy)


def test_room_doors_are_within_bounds_and_walkable():
    grid = _load_grid()
    required_rooms = {'Dorm_North', 'Dorm_South', 'Cafeteria', 'Library', 'Classroom_STEM'}
    for name, room in grid.rooms.items():
        doors = grid.room_entry_points(name)
        if name in required_rooms:
            assert doors, f"Expected door metadata for {name}"
        for door_x, door_y in doors:
            assert room.contains(door_x, door_y)
            assert grid.walkable(door_x, door_y)


def test_spawn_points_are_walkable():
    grid = _load_grid()
    for role in (None, 'student', 'staff'):
        for x, y in grid.spawn_points(role):
            assert grid.walkable(x, y)
