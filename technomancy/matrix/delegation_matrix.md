# Delegation Matrix

| Milestone ID | Milestone Name | Dependency Milestone IDs | Task ID | Task Description | Owner Role | Acceptance Checks |
|---|---|---|---|---|---|---|
| M1 | Core Simulation Stability | NONE | T1 | Direct architecture for Room effects and needs escalation thresholds and stub required tests. | High Technomancer | Deliverables D1 and D2 acceptance criteria defined and referenced in tactical plan. |
| M1 | Core Simulation Stability | NONE | T2 | Implement Room.apply_effects, finalize student decision overrides, and ship automated tests proving thresholds. | Technomancer | D1 Room Effects acceptance criteria; D2 Needs Overrides acceptance criteria. |
| M2 | Event Interaction Framework | M1 | T3 | Design event bus contracts, scene overlay integration, and Principal Console control flow in tactical plan. | High Technomancer | D3 Event System acceptance criteria; D4 Principal Console acceptance criteria documented. |
| M2 | Event Interaction Framework | M1 | T4 | Build events package, scene overlay, console interactions, and associated automated tests. | Technomancer | D3 Event System acceptance criteria; D4 Principal Console acceptance criteria. |
| M3 | Persistence and Verification | M1,M2 | T5 | Specify save/load schema, headless logging strategy, and comprehensive test coverage expectations. | High Technomancer | D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria cited. |
| M3 | Persistence and Verification | M1,M2 | T6 | Implement persistence, logging, and full automated test suite ensuring runbook commands succeed. | Technomancer | D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria. |
