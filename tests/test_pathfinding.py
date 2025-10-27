from pathlib import Path

from game.actors.npc import NPC
from game.core.map import MapGrid
from game.core.pathfinding import astar
from game.systems.movement_system import MovementSystem


def test_astar_finds_path():
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    start = grid.room_center('Dorm_North')
    goal = grid.room_center('Cafeteria')
    path = astar(grid, start, goal)
    assert path and path[0] == start and path[-1] == goal


def test_movement_system_reuses_cached_paths(monkeypatch) -> None:
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    system = MovementSystem(grid, cache_size=4)
    start = grid.room_center('Dorm_North')
    goal = grid.room_center('Library')
    actor = NPC(name='TestNPC', x=start[0], y=start[1], role='student', schedule=[])
    actor.set_target(*goal)

    calls = {'count': 0}

    def fake_astar(grid_arg, start_arg, goal_arg, blocked=None):  # type: ignore[unused-argument]
        calls['count'] += 1
        return [start, goal]

    monkeypatch.setattr('game.systems.movement_system.astar', fake_astar)

    system.plan_if_needed(actor)
    assert calls['count'] == 1

    actor.path.clear()
    system.plan_if_needed(actor)
    assert calls['count'] == 1
