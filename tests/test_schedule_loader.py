from game.core.map import MapGrid
from game.systems.schedule_system import ScheduleSystem
from pathlib import Path
def test_schedule_loads_and_creates_npcs():
 grid=MapGrid(str(Path('data')/'campus_map.json'))
 sched=ScheduleSystem(grid, str(Path('data')/'npc_schedules.json'))
 assert len(sched.npcs)>=2
 t, act = sched.npcs[0].schedule[0]
 assert isinstance(t,str) and hasattr(act,'name')
