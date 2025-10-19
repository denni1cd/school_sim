from pathlib import Path

import pytest

from game.core.map import MapGrid
from game.core.pathfinding import astar

MAP_PATH = Path('data') / 'campus_map_v1.json'
EXPECTED_ROOMS = {
    'Dorm_North',
    'Dorm_South',
    'Dorm_Commons',
    'Gymnasium',
    'Library',
    'Cafeteria',
    'Kitchen',
    'Classroom_STEM',
    'Classroom_Humanities',
    'Classroom_Arts',
    'Administration',
    'Courtyard',
    'Security',
    'Faculty_Offices',
}


@pytest.fixture(scope='module')
def campus_grid() -> MapGrid:
    return MapGrid(str(MAP_PATH))


def test_required_rooms_present(campus_grid: MapGrid) -> None:
    missing = EXPECTED_ROOMS - set(campus_grid.rooms)
    assert not missing, f'Missing rooms: {sorted(missing)}'


def test_room_lookup_matches_door_tiles(campus_grid: MapGrid) -> None:
    for room in campus_grid.rooms.values():
        for door_x, door_y in room.doors:
            found = campus_grid.room_for_position(door_x, door_y)
            assert found is room


def test_key_routes_have_paths(campus_grid: MapGrid) -> None:
    routes = [
        ('Dorm_North', 'Cafeteria'),
        ('Dorm_South', 'Classroom_STEM'),
        ('Library', 'Classroom_Arts'),
        ('Gymnasium', 'Courtyard'),
    ]
    for start_name, end_name in routes:
        start = campus_grid.room_center(start_name)
        end = campus_grid.room_center(end_name)
        path = astar(campus_grid, start, end)
        assert path, f'No path between {start_name} and {end_name}'
        assert path[0] == start
        assert path[-1] == end
