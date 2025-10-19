# Suggestions Log

## Milestone 6 – Room Metadata & Doors
- Add optional door directionality/labels so routing can pick sensible entry/exit sides for future multi-room wings.
- Support scenario/profile toggles to swap between campus datasets without editing YAML (e.g., CLI flag or layered config files).
- Extend interaction text to incorporate room context now that entry metadata exists (different greetings in dorm vs. library).
- Consider door weighting or congestion tracking to bias NPCs toward less crowded entry tiles during peak periods.
## Milestone 7 – Config Profiles
- Expose a --list-profiles CLI flag and Make targets so testers can discover/launch scenarios quickly.
- Support profile inheritance or layering to reduce duplication as more datasets arrive.
- Validate profile overrides (schema or key whitelist) to catch typos before runtime.
- Allow profiles to tweak broader settings (movement speed, timeflow) once additional scenarios demand it.
## Milestone 8 – Contextual Interactions
- Provide per-profile overrides for interaction text so new scenarios can adjust tone without editing the base file.
- Consider caching room lookups for interactions to avoid scanning all rooms once maps scale up.
- Add optional variables (time of day, player name) to the message formatter for richer responses.
- Explore plugging in a dialogue tree system that can consume the existing metadata when narrative depth expands.

