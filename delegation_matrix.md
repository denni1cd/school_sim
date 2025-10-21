# Delegation Matrix — Boarding School Simulation Upgrade

## Roles
- **Product Lead (PL):** Owns vision, prioritization, stakeholder alignment.
- **Engineering Lead (EL):** Architects systems, ensures OOP consistency, oversees code quality.
- **Gameplay Engineer (GE):** Implements map logic, scheduling, and activities.
- **Systems Engineer (SE):** Handles infrastructure, tooling, and performance tuning.
- **Content Designer (CD):** Defines room purposes, schedule templates, activity descriptions, placeholder assets.
- **QA Lead (QA):** Plans and executes automated/manual testing, maintains regression suite.
- **Producer (PR):** Coordinates milestone progress, aligns contributors, removes blockers.

## Milestones & RACI Assignments
| Milestone | Description | PL | EL | GE | SE | CD | QA | PR |
|-----------|-------------|----|----|----|----|----|----|----|
| **A. Campus Layout & Navigation** | Design and implement the realistic campus map with updated navigation metadata. | A | C | R | C | R | I | A |
| **B. Comprehensive Scheduling** | Build daily schedules, templates, conflict resolution, and variation. | C | A | R | C | R | I | A |
| **C. Activity Tracking & Reporting** | Map activities to rooms, expose status reporting, update placeholders. | C | A | R | C | R | C | A |
| **D. Player Management Hooks** | Deliver principal-facing APIs for monitoring and interventions. | A | R | C | C | I | C | A |
| **E. QA & Polish** | Stabilize systems, expand tests, finalize documentation for this level. | C | C | R | C | C | A | A |

Legend: **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed.

## Milestone Exit Criteria
- **Milestone A:** Map loaded in engine, room metadata validated, placeholder labels visible, pathfinding smoke tests pass.
- **Milestone B:** All NPC archetypes receive end-to-end schedules, simulation completes 24-hour cycle without deadlocks.
- **Milestone C:** Activities broadcast room-level context, interaction text updated, logging captures start/end events.
- **Milestone D:** Principal hooks allow schedule overrides, alerts surface via CLI/UI stubs, documentation updated.
- **Milestone E:** Regression suite green, performance targets met, release notes and onboarding guides published.

Refer to the dedicated tactical plan for each milestone (`tactical_plans/`) for the detailed step-by-step execution owned by the assigned personas above.

