from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .events.event_bus import EventBus
from .clubs import ClubsManager
from .policies import PolicyApplication, apply_policy_effects, change_discipline, change_uniform
from .curriculum import apply_classroom_modifiers, current_track as curriculum_current_track, set_track as set_curriculum_track
from .economy import Transaction, adjust_budget as economy_adjust_budget, record_transaction, serialise_history
from .rating import DEFAULT_BASELINES, DEFAULT_WEIGHTS, compute_rating
from .room import Room
from .student import (
    CRITICAL_ENERGY,
    CRITICAL_HUNGER,
    CRITICAL_HYGIENE,
    CRITICAL_STRESS,
    Student,
)
from .timetable import Timetable, minutes_to_timestr


class World:
    def __init__(
        self,
        rooms: Dict[str, Room],
        students: List[Student],
        timetable: Timetable,
        event_bus: Optional[EventBus] = None,
        *,
        game_config: Optional[dict] = None,
        policy_config: Optional[dict] = None,
        clubs_config: Optional[dict] = None,
        curriculum_config: Optional[dict] = None,
    ):
        self.rooms = rooms
        self.students = students
        self.timetable = timetable
        self.event_bus = event_bus
        self.time_minutes = 8 * 60  # start at 08:00
        config = game_config or {}
        self.config = config
        self.needs_overrides: Dict[str, dict] = config.get("needs_overrides", {})
        self.room_effects_config: Dict[str, dict] = config.get("room_effects", {})
        self.rating_config: Dict[str, float] = config.get("rating", {})
        self.needs_baseline: float = float(
            self.rating_config.get("needs_baseline", DEFAULT_BASELINES["needs"])
        )
        self.club_baseline: float = float(
            self.rating_config.get("club_baseline", DEFAULT_BASELINES["clubs"])
        )
        self.attendance_baseline: float = float(
            self.rating_config.get("attendance_baseline", DEFAULT_BASELINES["attendance"])
        )
        self.rating_weights: Dict[str, float] = dict(self.rating_config.get("weights", {}))
        self.rating_smoothing: float = float(self.rating_config.get("smoothing", 0.25))
        self.rating: float = float(
            self.rating_config.get("base", config.get("start_rating", 75.0))
        )
        self.budget: int = int(config.get("start_budget", 1000))
        self.economy_history: List[Transaction] = []
        self.policy_config: dict = policy_config or {}
        self.curriculum_config: dict = curriculum_config or {}
        self.policy_state: dict = {
            "uniforms": "moderate",
            "discipline": "fair",
        }
        self.policy_state.update(config.get("policy", {}) or {})
        self.curriculum_state: dict = {"active_track": "General"}
        self._initialise_curriculum_state(config.get("curriculum", {}), curriculum_config or {})
        self.save_system = None
        self.rating_delta: float = 0.0
        self.rating_flash: bool = False
        self.rating_breakdown: Dict[str, float] = {}
        self._event_history: List[dict] = []
        self._pending_events: List[dict] = []
        self._tick_compliance: List[float] = []
        self.last_compliance_score: float = 0.0
        self._compliance_baseline: float = float(
            self.policy_config.get("baseline_compliance", 0.97)
        )
        self._compliance_weight: float = float(self.policy_config.get("compliance_weight", 1.0))
        self._club_engagement_samples: List[float] = []
        self.last_club_engagement: float = self.club_baseline
        self._club_penalty_accumulator: float = 0.0
        self.clubs_manager = ClubsManager(
            clubs_config or {},
            budget_callback=self._adjust_budget,
        )
        self.policy_history: List[dict] = []

        if self.event_bus:
            self.event_bus.subscribe("event_fired", self._on_event_fired)

        self._apply_room_effect_config()

        for student in self.students:
            room = self.rooms.get(student.current_room)
            if room:
                student.x = room.x + room.width / 2.0
                student.y = room.y + room.height / 2.0
        self.refresh_club_memberships()
        self._spread_students_in_rooms()

    def tick(self, dt_minutes: int = 1):
        """Advance world by dt_minutes."""
        self.time_minutes += dt_minutes
        timestr = minutes_to_timestr(self.time_minutes)
        hour_slot = f"{timestr[:2]}:00"

        if self.event_bus:
            self.event_bus.emit(
                "time_tick",
                {"time_minutes": self.time_minutes, "time_str": timestr},
            )

        self._tick_compliance = []
        self._club_engagement_samples = []
        for student in self.students:
            previous_room = student.current_room
            student.decay_needs(dt_minutes)

            homeroom_schedule = self.timetable.homeroom_schedules.get(student.homeroom, {})
            student.choose_target(hour_slot, homeroom_schedule, self.rooms, self.needs_overrides)
            student.move_towards_target(self.rooms, dt_minutes)

            if previous_room != student.current_room:
                self._emit_room_transition(student, previous_room, student.current_room)

            if not student.is_traveling():
                current_room_obj = self.rooms.get(student.current_room)
                if current_room_obj:
                    deltas = current_room_obj.apply_effects(student, dt_minutes) or {}
                    if current_room_obj.room_type == "classroom":
                        curriculum_delta = apply_classroom_modifiers(
                            student,
                            state=self.curriculum_state,
                            dt_minutes=dt_minutes,
                        )
                        if curriculum_delta:
                            for key, value in curriculum_delta.items():
                                deltas[key] = deltas.get(key, 0.0) + value
                    if self.event_bus and deltas:
                        self.event_bus.emit(
                            "needs_update",
                            {
                                "student": student,
                                "room": student.current_room,
                                "deltas": deltas,
                            },
                        )

            expected = self.timetable.expected_room_for(student.homeroom, hour_slot)
            student.record_attendance(hour_slot, expected, traveling=student.is_traveling())

            application: PolicyApplication = apply_policy_effects(
                student,
                self.policy_state,
                dt_minutes=dt_minutes,
            )
            if application.compliance is not None:
                self._tick_compliance.append(application.compliance)

        self.clubs_manager.apply_club_tick(self, dt_minutes)
        self._update_rating()
        self._spread_students_in_rooms()

    def _emit_room_transition(self, student: Student, previous_room: Optional[str], current_room: Optional[str]) -> None:
        if not self.event_bus:
            return
        if previous_room:
            self.event_bus.emit(
                "room_exit",
                {"student": student, "room": previous_room},
            )
        if current_room:
            self.event_bus.emit(
                "room_enter",
                {"student": student, "room": current_room},
            )

    def get_debug_snapshot(self):
        """Return lightweight info for rendering / console log."""
        timestr = minutes_to_timestr(self.time_minutes)
        events = self.consume_recent_events()
        data = {
            "time": timestr,
            "rating": self.rating,
            "rating_delta": self.rating_delta,
            "rating_flash": self.rating_flash,
            "compliance": self.last_compliance_score,
            "club_engagement": self.last_club_engagement,
            "budget": self.budget,
            "policy": self.policy_state.copy(),
            "curriculum": self.curriculum_state.copy(),
            "rating_breakdown": self.rating_breakdown.copy(),
            "economy_history": serialise_history(self.economy_history),
            "policy_history": list(self.policy_history),
            "attendance_ratio": self._attendance_ratio(),
            "students": [],
            "events": events,
            "clubs": [
                {
                    "id": club.club_id,
                    "name": club.name,
                    "capacity": club.capacity,
                    "members": list(club.members),
                    "room": club.room,
                    "meets_at": club.meets_at,
                }
                for club in self.clubs_manager.clubs
            ],
        }
        for student in self.students:
            data["students"].append(
                {
                    "name": student.name,
                    "room": student.current_room,
                    "target": student.target_room,
                    "needs": student.needs.copy(),
                    "discipline_risk": student.stats["discipline_risk"],
                    "club": getattr(student, "club_id", None),
                }
            )
        return data

    def consume_recent_events(self) -> List[dict]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def record_event(self, *, event_id: Optional[str], caption: Optional[str], time_str: Optional[str]) -> None:
        payload = {
            "id": event_id,
            "caption": caption,
            "time": time_str,
        }
        self._event_history.append(payload)
        self._pending_events.append(payload)

    def _on_event_fired(self, payload: dict) -> None:
        event = payload.get("event")
        caption = None
        if event and getattr(event, "scene", None):
            caption = getattr(event.scene, "caption", None)
        self.record_event(
            event_id=getattr(event, "id", None),
            caption=caption,
            time_str=payload.get("time_str"),
        )

    @property
    def event_history(self) -> List[dict]:
        return list(self._event_history)

    def _apply_room_effect_config(self) -> None:
        if not self.room_effects_config:
            return
        for room in self.rooms.values():
            cfg = self.room_effects_config.get(room.room_type)
            if not cfg:
                continue
            effect_map = {k: float(v) for k, v in cfg.items()}
            knowledge_gain = float(effect_map.pop("knowledge", room.knowledge_gain or 0.0))
            room.effects = effect_map
            room.knowledge_gain = knowledge_gain

    def _update_rating(self) -> None:
        flash_threshold = float(self.rating_config.get("flash_threshold", 2.0))

        if self._tick_compliance:
            self.last_compliance_score = sum(self._tick_compliance) / max(1, len(self._tick_compliance))
        else:
            self.last_compliance_score = self.last_compliance_score or self._compliance_baseline
        if self._club_engagement_samples:
            self.last_club_engagement = sum(self._club_engagement_samples) / len(self._club_engagement_samples)

        critical_count = self._count_critical_students()
        attendance_ratio = self._attendance_ratio()
        adjusted_club_engagement = max(0.0, min(1.0, self.last_club_engagement - self._club_penalty_accumulator))

        result = compute_rating(
            previous=self.rating,
            critical_students=critical_count,
            total_students=len(self.students),
            compliance=self.last_compliance_score,
            compliance_baseline=self._compliance_baseline,
            club_engagement=adjusted_club_engagement,
            club_baseline=self.club_baseline,
            needs_baseline=self.needs_baseline,
            attendance_ratio=attendance_ratio,
            attendance_baseline=self.attendance_baseline,
            weights=self.rating_weights or DEFAULT_WEIGHTS,
            flash_threshold=flash_threshold,
            smoothing=self.rating_smoothing,
        )

        self.rating = result.value
        self.rating_delta = result.delta
        self.rating_flash = result.flash
        self.rating_breakdown = result.breakdown

        self._tick_compliance = []
        self._club_engagement_samples = []
        self._club_penalty_accumulator = 0.0

    # -- policy management -----------------------------------------------------

    def change_uniform_policy(self, new_level: str) -> str:
        costs = self.policy_config.get("costs", {})
        budget_after, caption = change_uniform(self.policy_state, new_level, costs=costs, budget=self.budget)
        if budget_after != self.budget:
            delta = budget_after - self.budget
            self.budget = budget_after
            self._record_transaction(delta, f"Policy change: uniforms -> {self.policy_state['uniforms'].title()}")
            self._log_policy_change("uniforms", self.policy_state["uniforms"], delta, caption)
        self._announce_policy_change("uniforms", caption)
        return caption

    def change_discipline_policy(self, new_level: str) -> str:
        costs = self.policy_config.get("costs", {})
        budget_after, caption = change_discipline(
            self.policy_state,
            new_level,
            costs=costs,
            budget=self.budget,
        )
        if budget_after != self.budget:
            delta = budget_after - self.budget
            self.budget = budget_after
            self._record_transaction(delta, f"Policy change: discipline -> {self.policy_state['discipline'].title()}")
            self._log_policy_change("discipline", self.policy_state["discipline"], delta, caption)
        self._announce_policy_change("discipline", caption)
        return caption

    def _announce_policy_change(self, policy_key: str, caption: str) -> None:
        if self.event_bus:
            self.event_bus.emit(
                "policy_overlay",
                {
                    "policy": policy_key,
                    "caption": caption,
                    "time_minutes": self.time_minutes,
                    "time_str": minutes_to_timestr(self.time_minutes),
                },
            )
        self.record_event(event_id=f"policy_{policy_key}", caption=caption, time_str=minutes_to_timestr(self.time_minutes))

    def change_curriculum_track(self, new_track: str) -> str:
        previous = curriculum_current_track(self.curriculum_state)
        caption = set_curriculum_track(new_track, state=self.curriculum_state)
        current = curriculum_current_track(self.curriculum_state)
        if current != previous:
            self._announce_curriculum_change(caption)
        return caption

    def _announce_curriculum_change(self, caption: str) -> None:
        time_str = minutes_to_timestr(self.time_minutes)
        if self.event_bus:
            self.event_bus.emit(
                "curriculum_overlay",
                {
                    "caption": caption,
                    "time_minutes": self.time_minutes,
                    "time_str": time_str,
                },
            )
        self.record_event(event_id="curriculum_change", caption=caption, time_str=time_str)

    # -- clubs management ------------------------------------------------------

    def get_student(self, name: str):
        for student in self.students:
            if student.name == name:
                return student
        return None

    def assign_student_to_club(self, student_name: str, club_id: str) -> bool:
        student = self.get_student(student_name)
        if not student:
            return False
        return self.clubs_manager.assign_student(student, club_id)

    def register_club_engagement(self, ratio: float) -> None:
        self._club_engagement_samples.append(max(0.0, min(1.0, ratio)))

    def apply_club_penalty(self, magnitude: float) -> None:
        self._club_penalty_accumulator += max(0.0, magnitude)

    def refresh_club_memberships(self) -> None:
        for club in self.clubs_manager.clubs:
            club.members.clear()
        for student in self.students:
            if getattr(student, "club_id", None):
                club = self.clubs_manager.get(student.club_id)
                if club and student.name not in club.members:
                    club.members.append(student.name)

    def _initialise_curriculum_state(self, game_payload: Optional[dict], config_payload: Optional[dict]) -> None:
        sources = []
        if isinstance(config_payload, dict) and config_payload:
            sources.append(config_payload)
        if isinstance(game_payload, dict) and game_payload:
            sources.append(game_payload)
        for source in sources:
            track = source.get("active_track")
            if not track:
                continue
            try:
                set_curriculum_track(track, state=self.curriculum_state)
            except ValueError:
                continue
        self.curriculum_config["active_track"] = self.curriculum_state.get("active_track", "General")

    def _spread_students_in_rooms(self) -> None:
        occupants: Dict[str, List[Student]] = defaultdict(list)
        for student in self.students:
            if student.current_room:
                occupants[student.current_room].append(student)
        for room_name, students in occupants.items():
            room = self.rooms.get(room_name)
            if not room:
                continue
            static_students = sorted(
                [student for student in students if not student.is_traveling()],
                key=lambda student: student.name,
            )
            if not static_students:
                continue
            positions = self._room_spread_positions(room, len(static_students))
            for student, (x, y) in zip(static_students, positions):
                student.x = x
                student.y = y

    def _room_spread_positions(self, room: Room, count: int) -> List[Tuple[float, float]]:
        if count <= 0:
            return []
        center_x = room.x + room.width / 2.0
        center_y = room.y + room.height / 2.0
        cols = max(1, int(math.ceil(math.sqrt(count))))
        rows = math.ceil(count / cols)
        span_x = min(room.width * 0.8, 160.0)
        span_y = min(room.height * 0.6, 80.0)
        step_x = span_x / (cols - 1) if cols > 1 else 0.0
        step_y = span_y / (rows - 1) if rows > 1 else 0.0
        start_x = center_x - span_x / 2.0 if cols > 1 else center_x
        start_y = center_y - span_y / 2.0 if rows > 1 else center_y
        positions: List[Tuple[float, float]] = []
        for idx in range(count):
            row = idx // cols
            col = idx % cols
            x = start_x + col * step_x if cols > 1 else center_x
            y = start_y + row * step_y if rows > 1 else center_y
            positions.append((x, y))
        return positions

    def _attendance_ratio(self) -> float:
        total, on_time = 0, 0
        for student in self.students:
            for attended in student.attendance_record.values():
                total += 1
                if attended:
                    on_time += 1
        if total == 0:
            return 1.0
        return on_time / total

    def _count_critical_students(self) -> int:
        overrides = self.needs_overrides or {}
        default_thresholds = {
            "hunger": CRITICAL_HUNGER,
            "energy": CRITICAL_ENERGY,
            "hygiene": CRITICAL_HYGIENE,
            "stress": CRITICAL_STRESS,
        }
        critical = 0
        for student in self.students:
            for need_name, value in student.needs.items():
                threshold = overrides.get(need_name, {}).get("critical")
                if threshold is None:
                    threshold = default_thresholds.get(need_name)
                if threshold is None:
                    continue
                threshold = float(threshold)
                low_is_bad = need_name in ("energy", "hygiene")
                if (low_is_bad and value <= threshold) or (not low_is_bad and value >= threshold):
                    critical += 1
                    break
        return critical

    def _record_transaction(self, delta: int, reason: str, *, time_str: Optional[str] = None) -> None:
        if delta == 0:
            return
        record_transaction(
            self.economy_history,
            time=time_str or minutes_to_timestr(self.time_minutes),
            reason=reason,
            delta=delta,
            balance=self.budget,
        )

    def _log_policy_change(self, policy_key: str, value: str, delta: int, caption: str) -> None:
        timestamp = minutes_to_timestr(self.time_minutes)
        entry = {
            "time": timestamp,
            "policy": policy_key,
            "value": value.title(),
            "delta": int(delta),
            "balance": int(self.budget),
            "caption": caption,
        }
        self.policy_history.append(entry)
        if len(self.policy_history) > 5:
            self.policy_history.pop(0)

    def _adjust_budget(self, delta: int, reason: str = "Budget adjustment") -> bool:
        if delta == 0:
            return True
        try:
            self.budget = economy_adjust_budget(self.budget, delta)
        except ValueError:
            return False
        self._record_transaction(delta, reason)
        return True
