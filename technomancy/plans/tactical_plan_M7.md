# Tactical Plan M7

## Objectives
- Ensure the curriculum documentation and handbook instructions capture how to add/monitor tracks (General/STEM/Arts) so new additions reuse the config structure and the Office `Curriculum` tab already shows track effects.
- Keep acceptance statements tied to the spec: curriculum modifiers, Office interaction tests and headless logging must remain in the golden suite (per `test_curriculum_modifiers.py` and `test_office_curriculum.py`), and the README should mention the config-driven nature and any required commands.

## Tasks

- **Task T7.1** – Curriculum documentation focus (High Technomancer)
  - Description: Verify the existing curriculum behaviors, and formalize instructions for adding new tracks/config entries plus the golden tests that cover them; record that knowledge in the plan and tactical notes.
  - Assigned Role: High Technomancer
  - Required Paths: `/technomancy/plans/m7_plan.md`, `/technomancy/plans/tactical_plan_M7.md`
  - Acceptance Checks: Plan references curriculum instructions, and the README addition mentions the config schema plus the corresponding tests.

- **Task T7.2** – Document rewrite and verification (Technomancer)
  - Description: Embed curriculum guidance into `README.md` (how to add tracks, required config keys, tests to run), stage it under `/technomancy/deliverables/docs/readme.md`, and cite the acceptance checks in new office/curriculum reference text.
  - Assigned Role: Technomancer
  - Required Paths: `/technomancy/deliverables/docs/readme.md`
  - Acceptance Checks: README contains a curriculum deep dive + instructions to rerun the key golden tests.

## Risks and Blockers
- Curriculum behavior is already implemented, so document-only work must not introduce drift; double-check the README copy to avoid mismatching instructions with actual `curriculum.py`.
- Ensure the staged doc path is cleaned after the merge to satisfy hygiene rules.

## Standards
- Keep instructions in README concise yet complete (config keys, track effects, repository commands).
- Tests referred to in the README must already exist under `school_sim/tests/` and remain passing without path tweaks.

## Deliverables
- `technomancy/deliverables/docs/readme.md`
  - Purpose: Update the README’s “Curriculum Deep Dive” with config guidance, track effects, and testing commands.
  - Acceptance Criteria Covered:
    - “Curriculum documentation plus golden test references” per Milestone M7 acceptance.

---
artifact: Tactical-Plan-Deliverables
milestone_id: "M7"
deliverables:
  - path: "technomancy/deliverables/docs/readme.md"
    purpose: "Describe curriculum tracks, config keys, and tests in the README."
    covers_acceptance_criteria:
      - "Curriculum documentation plus golden test references (Milestone M7 acceptance)."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
