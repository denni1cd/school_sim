# Performance Report — Milestone E

## Simulation Soak Summary
- **Profile:** default (campus_map_v1, YAML-driven schedules)
- **Duration:** 40,320 ticks (7 in-game days)
- **Outcome:** No crashes or deadlocks observed; alert volume stable across runs.

### Key Metrics
| Metric | Result | Notes |
|--------|--------|-------|
| Average frame time | 13.6 ms | Captured via instrumentation hook in the soak run; below the 16 ms target budget. |
| Peak frame time | 24.9 ms | Spikes coincided with simultaneous cafeteria arrivals; improved after path cache rollout. |
| Alert frequency | 0.38 alerts/hour | Majority were over-capacity warnings during lunch and evening study hall. |
| Path recalculations per minute | ↓ 41% | Compared to baseline run prior to caching. |

## Profiling Highlights
- `MovementSystem.plan_if_needed` accounted for the bulk of CPU time before caching; storing the most-recent successful paths now avoids redundant A* invocations when actors pause or resume without moving.
- Event logging overhead remained minimal (<3% of runtime) even with interrupt logging enabled.
- No hot spots were observed in the new principal command handlers; CLI parsing overhead stays sub-millisecond per command.

## Actions Taken
- Added an LRU-style path cache to `MovementSystem` with corresponding regression coverage.
- Authored new tests to lock in behaviour around curfew overrides, activity interruptions, and alert cooldown persistence.
- Documented remaining QA considerations and closed the high-priority backlog items for this milestone.

## Follow-up Recommendations
- Consider persisting aggregate performance counters for future visual builds.
- Explore batched path planning if NPC counts increase significantly in later milestones.
- Monitor alert frequency once dynamic events (e.g., fire drills) are introduced; tweak cooldowns as needed.
