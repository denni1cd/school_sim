"""
School Simulation core package exports.
"""

from .bootstrap import load_rooms, load_students, load_timetable
from .headless import run_headless
from .main import main

__all__ = [
    "load_rooms",
    "load_students",
    "load_timetables",
    "run_headless",
    "main",
]
