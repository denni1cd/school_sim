from pathlib import Path

from game.core.map import MapGrid
from game.systems.schedule_system import ScheduleSystem
from game.simulation.activities import ActivityCatalog


def test_schedule_loads_and_creates_npcs(tmp_path):
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    catalog = ActivityCatalog.load('config/activities.yaml')
    sched = ScheduleSystem(
        grid,
        str(Path('config') / 'schedules' / 'npc_assignments.yaml'),
        activity_catalog=catalog,
    )
    assert len(sched.npcs) >= 2

    t, act = sched.npcs[0].schedule[0]
    assert isinstance(t, str) and hasattr(act, 'name')
    assert act.profile is not None

    # Ensure spawn points respect role-aware configuration.
    student_spawns = {npc.name: (npc.x, npc.y) for npc in sched.npcs if npc.role == 'student'}
    assert student_spawns, 'Expected at least one student NPC'
    dorm_rooms = {'Dorm_North', 'Dorm_South', 'Dorm_Commons'}
    assert any(
        (room := grid.room_for_position(x, y)) is not None and room.name in dorm_rooms
        for x, y in student_spawns.values()
    )

    # Daily plans should expose travel metadata.
    for npc in sched.npcs:
        assert npc.daily_plan, f"Expected daily plan for {npc.name}"
        for block in npc.daily_plan[1:]:
            assert block.expected_travel is not None

    export_path = tmp_path / 'daily_plan.csv'
    sched.export_daily_plan(export_path)
    assert export_path.exists()
