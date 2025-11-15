from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass(frozen=True)
class OfficeView:
    key: str
    title: str
    lines: List[str]


@dataclass(frozen=True)
class OfficeTab:
    key: str
    title: str
    builder: Callable[[Optional[dict]], List[str]]


@dataclass(frozen=True)
class OfficeActionResult:
    message: Optional[str] = None
    overlay_caption: Optional[str] = None


class OfficeScreen:
    """Modal state manager for the Headmistress Office."""

    def __init__(
        self,
        *,
        policies: Optional[dict] = None,
        clubs: Optional[dict] = None,
        curriculum: Optional[dict] = None,
        staff: Optional[dict] = None,
    ) -> None:
        self.visible: bool = False
        self._active_index: int = 0
        self._policy_cursor: int = 0
        self._curriculum_cursor: int = 0
        self._pending_policy_values: dict[str, Optional[str]] = {"uniforms": None, "discipline": None}
        self._pending_curriculum_track: Optional[str] = None
        self._world = None
        self.policies_config = self._normalise_policies(policies)
        self.clubs_config = self._normalise_clubs(clubs)
        self.curriculum_config = self._normalise_curriculum(curriculum)
        self.staff_config = self._normalise_staff(staff)
        self._tabs: List[OfficeTab] = [
            OfficeTab("policies", "Policies", self._build_policies_lines),
            OfficeTab("clubs", "Clubs", self._build_clubs_lines),
            OfficeTab("curriculum", "Curriculum", self._build_curriculum_lines),
            OfficeTab("staff", "Staff", self._build_staff_lines),
            OfficeTab("reports", "Reports", self._build_reports_lines),
        ]
        self._policy_sequences = {
            "uniforms": ["moderate", "strict", "relaxed"],
            "discipline": ["fair", "tough", "lenient"],
        }
        self._curriculum_options: List[str] = ["General", "STEM", "Arts"]
        self._sync_curriculum_cursor()

    @property
    def active_index(self) -> int:
        return self._active_index

    def tab_titles(self) -> List[str]:
        return [tab.title for tab in self._tabs]

    def toggle(self) -> None:
        self.visible = not self.visible

    def bind_world(self, world) -> None:
        self._world = world

    def open(self) -> None:
        self.visible = True

    def close(self) -> None:
        self.visible = False
        self._policy_cursor = 0

    def next_tab(self) -> None:
        self._active_index = (self._active_index + 1) % len(self._tabs)
        if self._tabs[self._active_index].key == "curriculum":
            self._sync_curriculum_cursor()

    def previous_tab(self) -> None:
        self._active_index = (self._active_index - 1) % len(self._tabs)
        if self._tabs[self._active_index].key == "curriculum":
            self._sync_curriculum_cursor()

    def select_tab(self, index: int) -> None:
        if 0 <= index < len(self._tabs):
            self._active_index = index
            if self._tabs[index].key != "policies":
                self._policy_cursor = 0
            if self._tabs[index].key == "curriculum":
                self._sync_curriculum_cursor()

    def focus_policy_option(self, direction: int) -> None:
        active_key = self._tabs[self._active_index].key
        if active_key == "curriculum":
            count = len(self._curriculum_options)
            if count:
                self._curriculum_cursor = (self._curriculum_cursor + direction) % count
            return
        count = len(self._policy_sequences)
        self._policy_cursor = (self._policy_cursor + direction) % max(count, 1)

    def set_policy_target(self, key: str, value: Optional[str]) -> None:
        lowered = key.lower()
        if lowered not in self._pending_policy_values:
            raise ValueError(f"Unknown policy key: {key}")
        self._pending_policy_values[lowered] = value.lower() if value else None

    def set_curriculum_target(self, track: Optional[str]) -> None:
        if track is None:
            self._pending_curriculum_track = None
            return
        candidate = str(track).strip().title()
        if candidate not in self._curriculum_options:
            raise ValueError(f"Unknown curriculum track: {track}")
        self._pending_curriculum_track = candidate
        self._curriculum_cursor = self._curriculum_options.index(candidate)

    def activate(self, world) -> Optional[OfficeActionResult]:
        """Trigger the active tab's primary action."""
        if not self.visible:
            return None
        if world is not None and self._world is None:
            self._world = world
        active_tab = self._tabs[self._active_index]
        if self._world is None:
            return None
        if active_tab.key == "policies":
            option_key = "uniforms" if self._policy_cursor == 0 else "discipline"
            return self._apply_policy_change(option_key)
        if active_tab.key == "curriculum":
            target = self._pending_curriculum_track
            if not target and self._curriculum_options:
                target = self._curriculum_options[self._curriculum_cursor]
            self._pending_curriculum_track = None
            if not target:
                return None
            try:
                caption = self._world.change_curriculum_track(target)
            except ValueError as exc:
                return OfficeActionResult(message=str(exc))
            self.curriculum_config["active_track"] = self._world.curriculum_state.get("active_track", target)
            self._sync_curriculum_cursor()
            return OfficeActionResult(message=caption, overlay_caption=caption)
        return None

    def get_active_view(self, snapshot: Optional[dict] = None) -> OfficeView:
        tab = self._tabs[self._active_index]
        lines = tab.builder(snapshot or {})
        return OfficeView(key=tab.key, title=tab.title, lines=lines)

    # -- config normalisation helpers -------------------------------------------------

    def _normalise_policies(self, payload: Optional[dict]) -> dict:
        config = {
            "uniforms": "moderate",
            "discipline": "fair",
            "costs": {"change_policy": 50},
        }
        if not payload:
            return config
        config["uniforms"] = str(payload.get("uniforms", config["uniforms"]))
        config["discipline"] = str(payload.get("discipline", config["discipline"]))
        incoming_costs = payload.get("costs") or {}
        config["costs"].update({k: int(v) for k, v in incoming_costs.items()})
        return config

    def _normalise_clubs(self, payload: Optional[dict]) -> dict:
        config = {
            "clubs": [],
            "costs": {"create_club": 100, "assign_student": 5},
        }
        if not payload:
            return config
        clubs = payload.get("clubs") or []
        normalised: List[dict] = []
        for entry in clubs:
            if not isinstance(entry, dict):
                continue
            normalised.append(
                {
                    "id": entry.get("id"),
                    "name": entry.get("name"),
                    "room": entry.get("room"),
                    "meets_at": entry.get("meets_at"),
                    "capacity": int(entry.get("capacity", 0)),
                    "effects": dict(entry.get("effects", {}) or {}),
                }
            )
        config["clubs"] = normalised
        incoming_costs = payload.get("costs") or {}
        config["costs"].update({k: int(v) for k, v in incoming_costs.items()})
        return config

    def _normalise_curriculum(self, payload: Optional[dict]) -> dict:
        config = {"active_track": "General"}
        if not payload:
            return config
        config["active_track"] = str(payload.get("active_track", config["active_track"]))
        return config

    def _normalise_staff(self, payload: Optional[dict]) -> dict:
        config = {"staff": []}
        if not payload:
            return config
        staff_members = payload.get("staff") or []
        config["staff"] = [dict(entry) for entry in staff_members if isinstance(entry, dict)]
        return config

    # -- view builders -----------------------------------------------------------------

    def _build_policies_lines(self, snapshot: dict) -> List[str]:
        state = self._current_policy_state()
        uniforms = state.get("uniforms", "moderate").title()
        discipline = state.get("discipline", "fair").title()
        cost = self.policies_config.get("costs", {}).get("change_policy")
        lines = [
            self._policy_line("uniforms", uniforms, cost),
            self._policy_line("discipline", discipline, cost),
        ]
        if cost is not None:
            lines.append(f"Change policy cost: {cost}")
        lines.append("Adjust policy levels in future milestones to impact compliance and stress.")
        return lines

    def _build_clubs_lines(self, snapshot: dict) -> List[str]:
        config_clubs = self.clubs_config.get("clubs", [])
        snapshot_data = {
            club.get("id"): club
            for club in (snapshot.get("clubs") or [])
            if club.get("id")
        }
        if not config_clubs:
            return ["No clubs configured yet."]

        lines: List[str] = ["Available clubs:"]
        for club in config_clubs:
            club_id = club.get("id")
            name = club.get("name") or club_id or "Club"
            room = club.get("room", "TBD")
            meets_at = club.get("meets_at", "--:--")
            capacity = int(club.get("capacity", 0))
            lines.append(f"{name} ({room}) @ {meets_at}")
            members = list(snapshot_data.get(club_id, {}).get("members") or [])
            member_count = len(members)
            if capacity > 0:
                lines.append(f"  Members: {member_count}/{capacity}")
                if member_count > capacity:
                    overflow = member_count - capacity
                    lines.append(f"  OVER CAPACITY by {overflow}")
            else:
                lines.append(f"  Members: {member_count} (no capacity limit)")

            effects = club.get("effects") or {}
            if effects:
                effect_text = ", ".join(f"{k} {v:+.2f}" for k, v in effects.items())
                lines.append(f"  Effects: {effect_text}")
            if members:
                roster = ", ".join(members)
                lines.append(f"  Roster: {roster}")
        lines.append(
            f"Create club cost: {self.clubs_config['costs'].get('create_club', 0)} | "
            f"Assign student cost: {self.clubs_config['costs'].get('assign_student', 0)}"
        )
        engagement = snapshot.get("club_engagement")
        if engagement is not None:
            lines.append(f"Current engagement quality: {engagement:.2f}")
        return lines

    def _build_curriculum_lines(self, snapshot: dict) -> List[str]:
        active = self._current_curriculum_track()
        lines: List[str] = []
        for idx, option in enumerate(self._curriculum_options):
            marker = " (active)" if option.lower() == active.lower() else ""
            cursor = ">" if idx == self._curriculum_cursor else " "
            lines.append(f"{cursor} {option}{marker}".rstrip())
        if self._pending_curriculum_track and self._pending_curriculum_track.lower() != active.lower():
            lines.append(f"Pending change: {self._pending_curriculum_track}")
        lines.append("Enter applies highlighted track; Up/Down cycles options.")
        lines.append("Effects:")
        lines.append("  STEM: stress +0.05, hygiene -0.05, energy -0.05")
        lines.append("  Arts: stress -0.05, energy -0.05")
        lines.append("  General: baseline classroom modifiers")
        return lines

    def _build_staff_lines(self, snapshot: dict) -> List[str]:
        staff = self.staff_config.get("staff", [])
        if not staff:
            return ["No staff roster defined."]
        lines = ["Staff Roster:"]
        for member in staff:
            role = member.get("role", "Role")
            name = member.get("name", "Unknown")
            lines.append(f"- {role}: {name}")
        lines.append("Staff interactions arrive in later milestones.")
        return lines

    def _build_reports_lines(self, snapshot: dict) -> List[str]:
        time_str = snapshot.get("time", "--:--")
        budget = snapshot.get("budget")
        rating = snapshot.get("rating")
        rating_delta = snapshot.get("rating_delta")
        students = snapshot.get("students", [])
        events = snapshot.get("events", [])
        breakdown = snapshot.get("rating_breakdown", {})
        attendance_ratio = snapshot.get("attendance_ratio")
        history = snapshot.get("economy_history", [])
        lines = [
            f"Current Time: {time_str}",
            f"Budget: {budget if budget is not None else 'N/A'}",
        ]
        if rating is not None:
            lines.append(f"Rating: {rating:.1f}")
        if rating_delta not in (None, 0):
            lines.append(f"Rating delta: {rating_delta:+.1f}")
        if attendance_ratio is not None:
            lines.append(f"Attendance ratio: {attendance_ratio:.2f}")
        if breakdown:
            lines.append("Rating components:")
            component_labels = [
                ("needs", "Needs"),
                ("compliance", "Compliance"),
                ("clubs", "Clubs"),
                ("attendance", "Attendance"),
            ]
            for key, label in component_labels:
                lines.append(f"  {label}: {breakdown.get(key, 0.0):.1f}")
        lines.append(f"Enrolled Students: {len(students)}")
        if events:
            latest = events[-1]
            caption = latest.get("caption") or latest.get("id") or "Recent event"
            lines.append(f"Last Event: {caption}")
        policy_history = snapshot.get("policy_history") or []
        if policy_history:
            lines.append("Recent policy changes:")
            for record in policy_history[-3:]:
                delta = int(record.get("delta", 0))
                policy_label = (record.get("policy") or "policy").title()
                value = record.get("value", "")
                time_str = record.get("time", "--:--")
                caption = (record.get("caption") or "").strip()
                description = f"  {time_str} {policy_label}: {value} ({delta:+d})"
                if caption:
                    description += f" - {caption}"
                lines.append(description)
        if history:
            lines.append("Recent Transactions:")
            for entry in reversed(history[-3:]):
                reason = entry.get("reason") or "Change"
                delta = int(entry.get("delta", 0))
                balance = int(entry.get("balance", 0))
                lines.append(f"  {entry.get('time', '--:--')} {delta:+} -> {balance}")
                lines.append(f"    {reason}")
        return lines

    # -- internal helpers ---------------------------------------------------------------

    def _current_curriculum_track(self) -> str:
        if self._world is not None:
            return self._world.curriculum_state.get("active_track", "General")
        return self.curriculum_config.get("active_track", "General")

    def _sync_curriculum_cursor(self) -> None:
        active = self._current_curriculum_track().strip().title()
        if active in self._curriculum_options:
            self._curriculum_cursor = self._curriculum_options.index(active)
        else:
            self._curriculum_cursor = 0

    def _current_policy_state(self) -> dict:
        if self._world is not None:
            return {
                "uniforms": self._world.policy_state.get("uniforms", "moderate"),
                "discipline": self._world.policy_state.get("discipline", "fair"),
            }
        return {
            "uniforms": self.policies_config.get("uniforms", "moderate"),
            "discipline": self.policies_config.get("discipline", "fair"),
        }

    def _policy_line(self, key: str, value: str, cost: Optional[int]) -> str:
        cursor = ">" if (self._policy_cursor == 0 and key == "uniforms") or (
            self._policy_cursor == 1 and key == "discipline"
        ) else " "
        pending = self._pending_policy_values.get(key)
        next_value = pending or self._next_policy_value(key, value.lower()).title()
        suffix = f"(next: {next_value})" if next_value else ""
        if cost is not None and suffix:
            suffix += f" | cost {cost}"
        elif cost is not None:
            suffix = f"(cost {cost})"
        return f"{cursor} {key.title()}: {value} {suffix}".strip()

    def _next_policy_value(self, key: str, current: str) -> str:
        sequence = self._policy_sequences.get(key, [])
        if not sequence:
            return current
        if current not in sequence:
            return sequence[0]
        index = (sequence.index(current) + 1) % len(sequence)
        return sequence[index]

    def _apply_policy_change(self, key: str) -> Optional[OfficeActionResult]:
        if self._world is None:
            return None
        target = self._pending_policy_values.get(key)
        current_state = self._current_policy_state()
        if not target:
            target = self._next_policy_value(key, current_state.get(key, ""))
        self._pending_policy_values[key] = None

        try:
            if key == "uniforms":
                caption = self._world.change_uniform_policy(target)
            else:
                caption = self._world.change_discipline_policy(target)
        except ValueError as exc:
            return OfficeActionResult(message=str(exc))

        return OfficeActionResult(message=caption, overlay_caption=caption)

