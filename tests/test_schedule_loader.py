from pathlib import Path

from game.core.map import MapGrid
from game.systems.schedule_system import ScheduleSystem


def test_schedule_loads_and_creates_npcs():
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    sched = ScheduleSystem(grid, str(Path('data') / 'npc_schedules.json'))
    assert len(sched.npcs) >= 2

    t, act = sched.npcs[0].schedule[0]
    assert isinstance(t, str) and hasattr(act, 'name')

    # Ensure spawn points respect role-aware configuration.
    student_spawns = {npc.name: (npc.x, npc.y) for npc in sched.npcs if npc.role == 'student'}
    assert student_spawns, 'Expected at least one student NPC'
    dorm_rooms = {'Dorm_North', 'Dorm_South', 'Dorm_Commons'}
    assert any(
        (room := grid.room_for_position(x, y)) is not None and room.name in dorm_rooms
        for x, y in student_spawns.values()
    )
