# Milestone D & E Release Notes

## Highlights
- Principal management loop is now feature-complete with schedule overrides, summons, alerts, and broadcast tooling.
- Milestone E closes out QA and polish goals with targeted regression tests, performance improvements, and documentation.

## What Changed
1. **Reliability Enhancements**
   - Locked in curfew enforcement against late overrides and ensured activity interruptions clean up room state.
   - Strengthened alert cooldown guarantees so acknowledged incidents do not spam the principal dashboard.

2. **Performance Optimisation**
   - Added an LRU path cache to the movement system, reducing redundant A* computations during peak traffic.
   - Captured soak-test metrics to baseline frame times and alert volume for future comparison.

3. **Documentation & Process**
   - Published QA backlog, performance report, and sign-off checklist to make verification auditable.
   - Authored onboarding guidance for upcoming art/audio teams so placeholder assets can be swapped rapidly.

## Known Issues / Deferred Work
- Performance measurements were taken in headless mode; visual builds may require additional tuning once graphics land.
- Advanced alert routing (e.g., recipient groups) remains scheduled for a future milestone.
- Further automation around long-run soak tests is deferred until CI resources are provisioned.

## Next Steps
- Kick off the next level by layering in presentation assets and expanding dynamic events.
- Continue capturing QA findings in `docs/qa_backlog.md` to track regressions as features scale.
