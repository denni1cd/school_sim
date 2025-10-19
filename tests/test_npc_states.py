from game.actors.npc import NPC
from game.actors.base_actor import NPCState


def test_npc_state_cycle():
    n = NPC(name='N', x=0, y=0)
    class A:
        duration = 10
        location = 'Dorm_North'
        name = 'dummy'
    a = A()
    n.assign_activity(a)
    assert n.pending_schedule is a


def test_begin_activity_with_late_start_adjusts_duration():
    class Activity:
        duration = 120
        location = 'Classroom_STEM'
        name = 'class'
    npc = NPC(name='Alice', x=0, y=0)
    activity = Activity()
    npc.assign_activity(activity, start_minutes=60)
    npc.begin_activity(activity, current_minutes=90, day_length_minutes=1440)
    assert npc.activity_remaining == 90
    assert npc.state == NPCState.PERFORMING_TASK
    assert npc.pending_schedule is None
