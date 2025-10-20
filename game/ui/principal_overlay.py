from __future__ import annotations

from typing import Iterable, List, Sequence

from ..interface.principal_controls import OverrideRecord
from ..notifications import Alert


def format_overlay(alerts: Sequence[Alert], overrides: Iterable[OverrideRecord]) -> List[str]:
    lines: List[str] = ["Principal Console", "=================="]
    lines.append("[Tab] Room overlay    [P] Principal console")
    lines.append("[1-9] Acknowledge alert")
    lines.append("[Shift+B] Broadcast reminder (placeholder)")
    lines.append("")
    lines.append("Active Alerts:")
    if not alerts:
        lines.append("  (none)")
    else:
        for idx, alert in enumerate(alerts[:9], start=1):
            marker = f"{idx}. "
            detail = f"{alert.category} — {alert.message}"
            room_info = f" ({alert.room_id})" if alert.room_id else ""
            lines.append(f"  {marker}{detail}{room_info}")
    lines.append("")
    lines.append("Recent Overrides:")
    history = list(overrides)
    if not history:
        lines.append("  (none)")
    else:
        for entry in history[-5:]:
            block_list = ', '.join(block.activity_id for block in entry.blocks)
            lines.append(f"  {entry.timestamp} — {entry.npc_id}: {block_list}")
    return lines
