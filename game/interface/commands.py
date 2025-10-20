from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import MutableMapping, Sequence

from .principal_controls import PrincipalControls


class CommandError(RuntimeError):
    """Raised when a command cannot be parsed or executed."""


@dataclass
class CommandResult:
    message: str


class CommandDispatcher:
    """Parses textual commands and forwards them to principal controls."""

    def __init__(self, controls: PrincipalControls) -> None:
        self._controls = controls

    def execute(self, command: str) -> CommandResult:
        tokens = shlex.split(command)
        if not tokens:
            raise CommandError("Empty command")
        head = tokens[0].lower()
        if head == "schedule":
            return self._handle_schedule(tokens[1:])
        if head == "summon":
            return self._handle_summon(tokens[1:])
        if head == "alerts":
            return self._handle_alert(tokens[1:])
        if head == "broadcast":
            return self._handle_broadcast(tokens[1:])
        raise CommandError(f"Unknown command '{head}'")

    def _handle_schedule(self, tokens: Sequence[str]) -> CommandResult:
        if len(tokens) < 2 or tokens[0].lower() != "override":
            raise CommandError("Usage: schedule override <npc> key=value ...")
        npc_id = tokens[1]
        block_tokens = tokens[2:]
        if not block_tokens:
            raise CommandError("Provide at least one key=value pair for the override block")
        block: MutableMapping[str, object] = {}
        for token in block_tokens:
            if "=" not in token:
                raise CommandError(f"Expected key=value segment, received '{token}'")
            key, value = token.split("=", 1)
            key = key.strip().lower()
            if key in {"start", "activity", "room", "duration", "notes"}:
                block[key] = value.strip()
            elif key.startswith("meta."):
                block.setdefault("metadata", {})
                metadata = block["metadata"]
                assert isinstance(metadata, dict)
                metadata[key.split(".", 1)[1]] = value.strip()
            else:
                raise CommandError(f"Unsupported override attribute '{key}'")
        overrides = [block]
        updated = self._controls.override_schedule(npc_id, overrides)
        return CommandResult(message=f"Override applied to {npc_id} with {len(updated)} block(s)")

    def _handle_summon(self, tokens: Sequence[str]) -> CommandResult:
        if len(tokens) < 2:
            raise CommandError("Usage: summon <npc> <room> [duration=HH:MM]")
        npc_id, room_id = tokens[0], tokens[1]
        duration_minutes = 30
        for token in tokens[2:]:
            if token.startswith("duration="):
                _, value = token.split("=", 1)
                parts = value.split(":")
                if len(parts) != 2:
                    raise CommandError("Duration must use HH:MM format")
                hours, minutes = map(int, parts)
                duration_minutes = hours * 60 + minutes
            else:
                raise CommandError(f"Unknown summon argument '{token}'")
        self._controls.summon_student(npc_id, room_id, duration_minutes=duration_minutes)
        return CommandResult(message=f"Summoning {npc_id} to {room_id}")

    def _handle_alert(self, tokens: Sequence[str]) -> CommandResult:
        if len(tokens) < 2 or tokens[0].lower() != "resolve":
            raise CommandError("Usage: alerts resolve <alert_id>")
        alert_id = tokens[1]
        self._controls.mark_alert_resolved(alert_id)
        return CommandResult(message=f"Alert {alert_id} acknowledged")

    def _handle_broadcast(self, tokens: Sequence[str]) -> CommandResult:
        if not tokens:
            raise CommandError("Usage: broadcast message=<text> [audience.key=value ...]")
        message = None
        audience: MutableMapping[str, object] = {}
        for token in tokens:
            if "=" not in token:
                if message is None:
                    message = token
                else:
                    message = f"{message} {token}"
                continue
            key, value = token.split("=", 1)
            key = key.strip().lower()
            if key == "message":
                message = value.strip()
            elif key.startswith("audience."):
                audience[key.split(".", 1)[1]] = value.strip()
            elif key == "audience":
                audience["group"] = value.strip()
            else:
                raise CommandError(f"Unknown broadcast attribute '{key}'")
        if not message:
            raise CommandError("Broadcast requires a message=<text> argument")
        self._controls.broadcast_message(message, audience if audience else None)
        return CommandResult(message=f"Broadcast queued: {message}")
