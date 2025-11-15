import pygame

from school_sim.bootstrap import load_game_config, load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.principal_console import PrincipalConsole
from school_sim.save_system import SaveSystem
from school_sim.world import World


def build_world(tmp_path):
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    config = load_game_config()
    bus = EventBus()
    world = World(rooms, students, timetable, event_bus=bus, game_config=config)
    save_system = SaveSystem(tmp_path)
    world.save_system = save_system
    console = PrincipalConsole(bus, [])
    return world, save_system, console


def test_console_save_and_load_cycle(tmp_path):
    pygame.init()
    try:
        world, save_system, console = build_world(tmp_path)
        initial_time = world.time_minutes

        console.toggle()
        console.handle_key(pygame.K_s, world)
        assert console.log[0].startswith("Saved game")
        saves = list(tmp_path.glob("save_*.json"))
        assert saves, "Save file was not created"

        world.time_minutes += 120
        console.handle_key(pygame.K_l, world)
        assert "Loaded game" in console.log[0]
        assert world.time_minutes == initial_time
    finally:
        pygame.quit()
