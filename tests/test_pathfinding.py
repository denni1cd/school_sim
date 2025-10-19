from game.core.map import MapGrid
from game.core.pathfinding import astar
from pathlib import Path
def test_astar_finds_path():
 grid=MapGrid(str(Path('data')/'campus_map.json'))
 s=grid.room_center('Dorm'); g=grid.room_center('ClassA')
 p=astar(grid,s,g)
 assert p and p[0]==s and p[-1]==g
