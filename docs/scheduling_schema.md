# Scheduling Schema Overview

This document captures the structure used by the Milestone B scheduling system.

## Files
- `config/schedules/activities.yaml` — canonical activity definitions including default duration, location, and optional notes.
- `config/schedules/student_templates.yaml` — persona-driven schedule templates with `slot`, `start`, `duration`, `activity`, optional `room`, `travel_buffer`, and free-form `notes` per entry.
- `config/schedules/npc_assignments.yaml` — roster describing which template each NPC uses along with slot-level overrides.

## Daily Slot Fields
| Field | Description |
| --- | --- |
| `slot` | Stable identifier for overrides and analytics. |
| `start` | HH:MM time the slot begins. |
| `duration` | HH:MM duration of the slot. Required except for anchor rows. |
| `activity` | Activity key mapping to `activities.yaml`. |
| `room` | Optional override for the activity’s default location. |
| `travel_buffer` | Optional HH:MM buffer allocated for travel before the slot. |
| `notes` | Optional human-readable description.

## Assignment Overrides
Each override entry can modify an instantiated slot:
```
- slot: evening_social
  start: "21:00"        # optional new start time
  duration: "01:00"      # optional new duration
  activity: evening_walk  # optional new activity id
  room: Courtyard         # optional new location
  travel_buffer: "00:10" # optional new buffer
  notes: "Sunset walk"
```
Overrides are applied after template instantiation.

## Conflict Resolution
- Room capacities are sourced from the campus map metadata.
- When multiple NPCs exceed a room’s capacity, `resolve_with_staggering` pushes later slots forward in five-minute increments until the overlap clears.
- Travel estimation recomputes after conflicts resolve so buffers and analytics reflect the final timeline.

## CSV Export
The schedule system can export the normalized daily plan via `ScheduleSystem.export_daily_plan(path)`.
Columns:
`actor_id,start_time,end_time,slot,activity,room,expected_travel_minutes,travel_buffer_minutes,notes`
