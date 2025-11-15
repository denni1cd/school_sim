# School Sim — Specification

**Version:** 1.4 (Expanded gameplay: Office, Policies, Clubs, Curriculum)  
**Python:** 3.12  
**App Root (production):** `/school_sim`  
**Technomancy Staging (temporary only):** `/technomancy/deliverables/{src,tests,docs}`  
**Technomancy Artifacts (persist):** `/technomancy/{logs,plans,matrix,docs}`  
**Technomancy Artifacts (ephemeral, auto-clean):** `/technomancy/runtime/**`  
**Entry Commands:** `make run`, `make simulate`, `make test`  
**Platforms:** Windows 10/11, macOS, Linux (headless allowed)

> **Goal (vertical slice → management slice):** Bootable, clean, deterministic school-management game where the **player (Headmistress) makes decisions from an Office screen** that materially affect student behaviors and the School Rating. This version adds **Policies (uniforms & discipline), Clubs, Curriculum** and a basic **Budget**. Placeholder graphics only; focus on systems, tests, and headless determinism.

---

## 0) Hard Rules (Global, Output Locations)  _(unchanged)_

- **R0.0 Output Locations (authoritative):**
  - **Production code & tests** under **`/school_sim/**`**.  
  - **Technomancy docs & planning** under **`/technomancy/docs/**`, plus **`/technomancy/{logs,plans,matrix}`**.  
  - **Technomancy staging** only under **`/technomancy/deliverables/{src,tests,docs}`**.  
  - **Technomancy runtime (ephemeral):** **`/technomancy/runtime/**`** must be cleaned by milestone end.  
  - **No shippables in** `/technomancy/deliverables/**` after a milestone.
- **R0.1–R0.6** as v1.3 (determinism, test-first, idempotent merge, Windows-safe paths, etc.).

---

## 1) Authoritative Directory Layout (Production) _(adds modules)_

```
/school_sim
  /assets/{images,audio}
  /configs
    events.yaml
    game.yaml
    policies.yaml
    clubs.yaml
    curriculum.yaml
    staff.yaml
  /runtime/{logs,saves,scenes}
  /tests
  main.py
  world.py
  student.py
  room.py
  timetable.py
  renderer.py
  rating.py
  economy.py
  office.py
  policies.py
  clubs.py
  curriculum.py
  staff.py
  /events
    __init__.py
    event_models.py
    event_loader.py
    event_bus.py
    event_rules.py
    scene_overlay.py
```

**Hygiene rules:** exactly one `configs/`, `tests/`, `runtime/` under `/school_sim`; no duplicate classes; no backups.

---

## 2) Functional Specification (Expanded)

### 2.1 Time & World _(as v1.3)_
- Start `08:00` (`time_minutes = 8*60`), ≥3 students, core rooms unchanged.

### 2.2 Needs & Drift _(as v1.3)_
- Per-minute base drift; room effects; clamp 0..100.

### 2.3 Targeting Overrides _(as v1.3, configurable in game.yaml)_

### 2.4 HUD _(expanded)_
- Clock `HH:MM`
- **School Rating 0..100**
- **Budget** display (integer currency; default ₵ = credits)
- Flash if rating delta ≥ 2.0 this tick

### 2.5 Player Actions _(expanded)_
- `P` toggle console
- `T` +15 minutes
- `E` fire first event
- `B` broadcast (log-only)
- `L` load latest save (dev)
- **`O` open Office screen**
- `ESC`/`ENTER` dismiss overlay/office dialogs

### 2.6 **Office Screen (Management UI)** — **`office.py`**
A modal tabbed interface (keyboard driven; mouse optional in future) with tabs:
- **Policies** (Uniform & Discipline)
- **Clubs**
- **Curriculum**
- **Staff** (read-only in v1.4)
- **Reports** (Budget + KPIs)

A) **Policies** (`policies.py`, `configs/policies.yaml`)
- Two categories in v1.4: **Uniforms** and **Discipline**.
- **Uniforms:** `strict | moderate | relaxed`  
  Effects per tick (additive to base drift, per student):
  - strict: `hygiene += +0.1`, `stress += +0.15`
  - moderate: no effect
  - relaxed: `hygiene += -0.1`, `stress += -0.05`
  Compliance chance (affects **Rating** and **Detentions**): strict 92%, moderate 97%, relaxed 99%.
- **Discipline:** `tough | fair | lenient`  
  Effects per tick (if student is above/below thresholds):
  - tough: decrease `stress` when misbehavior caught (−0.2), increase base stress (+0.05), boosts compliance.
  - fair: baseline
  - lenient: lower stress (+0.0), lower compliance (−5%).
- Policy changes trigger a **scene overlay** summarizing impact and a **budget cost** (admin overhead).

B) **Clubs** (`clubs.py`, `configs/clubs.yaml`)
- Clubs defined with: `id`, `name`, `room`, `meets_at (HH:MM)`, `capacity`, `effects` (needs deltas).
- Student assignment: simple preference matching; max 1 club in v1.4.
- Attendance: when time matches `meets_at`, assigned students route to club room; apply `effects` for 30 minutes.
- If capacity exceeded, excess students receive `stress += +0.5` and a small rating penalty.

C) **Curriculum** (`curriculum.py`, `configs/curriculum.yaml`)
- Tracks: `STEM`, `Arts`, `General` (v1.4)
- Each track modifies per-minute **classroom** effects when student is in `Classroom`:
  - STEM: `stress +0.05`, `hygiene -0.05`, `energy -0.05`
  - Arts: `stress -0.05`, `energy -0.05`
  - General: baseline
- Player can set the school-wide focus: one active track (v1.4).

D) **Reports & Budget** (`economy.py`)
- **Budget**: integer. Defaults to `1000` in `game.yaml`.
- Costs (examples, configurable in `game.yaml`):
  - Changing policy: `50`
  - Creating a club: `100`
  - Assigning student to a club: `5`
- **Rating** (`rating.py`) components:
  - Needs health (inverse of avg criticals) 60%
  - Compliance 20%
  - Club engagement 10%
  - Attendance punctuality 10%

### 2.7 Events & Scenes _(extended hooks)_
- Events can be triggered by **policy changes**, **club capacity overflows**, **curriculum change**, and keep time-based examples.
- `SceneOverlay.show(image, caption)` is reused for these.

### 2.8 Save / Load _(extended)_
- JSON save stores: time, students (needs, room, target, club assignment), active **policy**, active **curriculum**, **budget**.
- `load_latest()` restores these.

### 2.9 Headless Simulation _(unchanged interface)_
- Log includes `rating`, `budget`, selected `policy` & `curriculum` every minute.

---

## 3) Configuration Schemas (YAML)

### 3.1 `configs/policies.yaml`
```yaml
uniforms: strict   # strict | moderate | relaxed
discipline: fair   # tough | fair | lenient
costs:
  change_policy: 50
```

### 3.2 `configs/clubs.yaml`
```yaml
clubs:
  - id: "art_club"
    name: "Art Club"
    room: "Classroom"
    meets_at: "08:30"
    capacity: 8
    effects: { stress: -0.3, energy: -0.1 }
  - id: "track_team"
    name: "Track & Field"
    room: "Gym"
    meets_at: "08:45"
    capacity: 6
    effects: { energy: -0.4, stress: -0.1, hygiene: -0.2 }
costs:
  create_club: 100
  assign_student: 5
```

### 3.3 `configs/curriculum.yaml`
```yaml
active_track: "General"   # STEM | Arts | General
```

### 3.4 `configs/staff.yaml` (v1.4 read-only; future behavior hooks)
```yaml
staff:
  - id: "hm"
    role: "Headmistress"
    name: "E. Sterling"
  - id: "coach"
    role: "Coach"
    name: "R. Vega"
```

### 3.5 `configs/game.yaml` (extend)
```yaml
tick_ms: 100
win_time: "09:00"
start_budget: 1000
rating_drop_per_crit: 0.5
critical_thresholds: { hunger: 85, energy: 25, hygiene: 30, stress: 90 }
```

---

## 4) Technical Contracts (APIs) — **new modules**

- `policies.apply_policy_effects(student, policy_state) -> None`  
- `policies.change_uniform(policy_state, new_level) -> budget_after, scene_caption`
- `clubs.assign_student(student_id, club_id) -> bool` (checks capacity; adjusts budget)  
- `clubs.apply_club_tick(world) -> None` (applies effects at meeting times)
- `curriculum.set_track(track_name) -> None`  
- `curriculum.apply_classroom_modifiers(student) -> None`  
- `office.toggle(open: bool) -> None` and `office.handle_input(key)` to switch tabs & make changes
- `economy.adjust_budget(delta:int) -> int`  
- `rating.compute(world) -> float`

All new modules must be pure-Python, deterministic, and testable headless.

---

## 5) Tooling & Runtime _(unchanged interface)_
- `requirements.txt`: `pygame`, `pyyaml`, `pytest` (+ actually used libs)
- Makefile (as v1.3)

---

## 6) Acceptance Criteria (Gates) — **add Golden Tests**

### 6.1 Runtime Gates
- v1.3 gates still hold: 60s run without exceptions; overlay at 08:02.
- Office opens with `O`, tabs change with arrow keys (or `1..5`) and ENTER triggers an action.

### 6.2 Repo Hygiene Gates
- As v1.3 plus presence of the new config files in `/school_sim/configs/`.

### 6.3 Golden Tests (must exist & pass)
- `test_policies_uniforms.py`: switching uniforms `moderate→strict` changes per-tick hygiene/stress deltas and deducts budget by configured amount.
- `test_discipline_effects.py`: discipline `tough` increases compliance-derived rating component vs `lenient` after a few ticks (deterministic).
- `test_clubs_capacity.py`: over-capacity assignment logs penalty and increases average stress when meeting time occurs.
- `test_club_assignment_budget.py`: assigning student deducts `assign_student` cost.
- `test_curriculum_modifiers.py`: STEM active track raises classroom stress relative to General.
- `test_office_navigation.py`: `O` opens Office; `Policies` tab visible; pressing ENTER on “Uniform: strict” applies and persists.
- (carry-over) v1.3 Golden Tests all still present and pass.

---

## 7) Milestones (Extended)

- **M0 — Grounding & Hygiene (same)**  
- **M1 — Events + Overlay + HUD (same)**  
- **M2 — Needs Overrides + Rating (same)**  
- **M3 — Actions + Save/Load (same)**  
- **M4 — Office Shell:** `office.py` modal with tab switching + read-only summaries from configs  
- **M5 — Policies:** implement uniforms & discipline effects; budget costs; tests  
- **M6 — Clubs:** config-driven clubs; assignment; capacity effects; tests  
- **M7 — Curriculum:** tracks + classroom modifiers; tests  
- **M8 — Budget & Reports:** economy plumbing + rating breakdown report; tests; final polish

Milestone completion requires merge + post-merge verification + `final_report.md` as defined in v1.3.

---

## 8) Save/Load Format (JSON fields, minimum)
```json
{
  "time_minutes": 480,
  "budget": 1000,
  "policy": {"uniforms": "moderate", "discipline": "fair"},
  "curriculum": {"active_track": "General"},
  "students": [
    {"id":"alice","needs":{"hunger":30.5,"energy":79.2,"stress":19.0,"hygiene":64.5},"room":"Lounge","target":"Lounge","club":"art_club"}
  ]
}
```

---

## 9) Completion Definition
All v1.3 criteria plus: Office opens; at least one policy change and one club meeting impacts student needs and School Rating in a 60s run; budget changes are reflected; all new Golden Tests pass; repo is deterministic, clean, and runnable from a fresh checkout.
