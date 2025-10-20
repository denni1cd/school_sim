# Principal Controls

Milestone D introduces interactive hooks that let the principal persona guide
the simulation while placeholder visuals remain minimal. The controls operate
both in the headless CLI (`python -m game.simulation`) and in the pygame viewer
(`python -m game.play`).

## Command Summary

| Command | Description |
| --- | --- |
| `schedule override <npc> start=HH:MM activity=<id> room=<room> [duration=HH:MM]` | Replace upcoming blocks for the specified NPC. Notes may be appended via `notes=...`. |
| `summon <npc> <room> [duration=HH:MM]` | Interrupts the NPC and routes them to the target room for the specified duration (default 30 minutes). |
| `alerts resolve <alert_id>` | Acknowledges the alert and removes it from the active queue. |
| `broadcast message=<text> [audience.role=role_name]` | Logs a campus broadcast with optional audience metadata. |

The command processor accepts a text file via `--commands`. Each non-empty,
non-comment line is executed in order before the simulation advances.

```
python -m game.simulation --ticks 600 --commands scripts/principal_demo.txt
```

## Pygame Overlay

Press `P` in the pygame viewer to toggle the principal console overlay. While
visible you can:

- Press `1`-`9` to acknowledge the corresponding alert.
- Press `Shift+B` to trigger a placeholder campus-wide broadcast.
- Review the five most recent schedule overrides alongside the active alert
  list.

Room-level overlays remain available while holding `Tab`.

## Alert Types

Alerts use a ten-minute cooldown window per `(category, room, npc set)` key to
avoid spamming repeat notifications. Current categories include:

- **Overcapacity** – triggered when a room exceeds its declared capacity.
- **MissedClass** – a student fails to reach a class block within a grace
  period (travel buffer + 10 minutes).
- **CurfewViolation** – a student is outside the dormitories between 22:00 and
  06:00 while not engaged in a sleeping activity.

Alerts can be acknowledged via CLI or the overlay; acknowledgements are logged
through the event logger for audit trails.

## Override Semantics

Schedule overrides rebuild the NPC’s daily plan and apply travel annotations via
the scheduling system. Overrides persist for the current session and are marked
in the export pipeline via the `notes` column so later tooling can detect
principal intervention.
