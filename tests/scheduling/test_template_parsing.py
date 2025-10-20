from pathlib import Path

from game.core.map import MapGrid
from game.simulation.schedule_generator import (
    DailySchedule,
    ScheduleAssignment,
    ScheduleTemplate,
    TravelEstimator,
    parse_hhmm,
)


def test_schedule_template_instantiation():
    template = ScheduleTemplate(
        'boarding',
        {
            'weekday': [
                {
                    'slot': 'wake',
                    'start': '06:30',
                    'duration': '00:30',
                    'activity': 'wake',
                    'room': 'Dorm_North',
                },
                {
                    'slot': 'class',
                    'start': '08:30',
                    'duration': '03:00',
                    'activity': 'class',
                    'room': 'Classroom_STEM',
                },
            ]
        },
        day_length_minutes=1440,
    )
    slots = template.instantiate('Alice', 'weekday')
    assert len(slots) == 2
    assert slots[0].actor_id == 'Alice'
    assert slots[0].start_tick == parse_hhmm('06:30')
    assert slots[1].room_id == 'Classroom_STEM'


def test_assignment_overrides_change_activity():
    template = ScheduleTemplate(
        'boarding',
        {
            'weekday': [
                {'slot': 'clubs', 'start': '16:00', 'duration': '01:30', 'activity': 'club', 'room': 'Classroom_Arts'}
            ]
        },
        day_length_minutes=1440,
    )
    assignment = ScheduleAssignment(
        actor_id='Dana',
        template_name='boarding',
        template=template,
        overrides=[
            {
                'slot': 'clubs',
                'activity': 'study',
                'room': 'Library',
                'duration': '01:45',
                'notes': 'Override to study hall',
            }
        ],
    )
    slots = assignment.apply()
    assert slots[0].activity_id == 'study'
    assert slots[0].room_id == 'Library'
    assert slots[0].duration_minutes == 105
    assert slots[0].notes == 'Override to study hall'


def test_travel_estimator_updates_expected_path():
    grid = MapGrid(str(Path('data') / 'campus_map_v1.json'))
    estimator = TravelEstimator(grid)
    blocks = {
        'Alice': [
            DailySchedule(
                actor_id='Alice',
                slot='wake',
                activity_id='wake',
                room_id='Dorm_North',
                start_tick=parse_hhmm('06:30'),
                duration_minutes=30,
                day_length_minutes=1440,
            ),
            DailySchedule(
                actor_id='Alice',
                slot='class',
                activity_id='class',
                room_id='Classroom_STEM',
                start_tick=parse_hhmm('08:30'),
                duration_minutes=180,
                day_length_minutes=1440,
                travel_buffer=5,
            ),
        ]
    }
    estimator.annotate(blocks, adjust_buffers=True)
    second = blocks['Alice'][1]
    assert second.expected_travel is not None
    assert second.travel_buffer >= second.expected_travel
