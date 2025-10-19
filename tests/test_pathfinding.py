from pathlib import Path

from game.core.map import MapGrid
from game.core.pathfinding import astar


def test_astar_finds_path():
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    start = grid.room_center('Dorm_North')
    goal = grid.room_center('Cafeteria')
    path = astar(grid, start, goal)
    assert path and path[0] == start and path[-1] == goal
