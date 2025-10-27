# Onboarding Checklist — Art & Audio Teams

Use this checklist to transition placeholder assets to production-quality visuals and sound once the engine is finalised.

## Access & Environment
- [ ] Obtain repo access and review `project_plan.md` plus tactical guides for Milestones A–E.
- [ ] Install Python 3.12 environment; confirm `pygame` placeholder client launches with `python -m game.play`.
- [ ] Review `docs/campus_layout_notes.md` for room naming conventions and collision expectations.

## Visual Asset Replacement
- [ ] Replace placeholder tiles with concept-approved art, matching current dimensions (tile size auto-scales with the window).
- [ ] Supply layered source files so hit boxes and walkable tiles can be regenerated if map sizes change.
- [ ] Update `config/interactions.yaml` strings if new signage or room labels are introduced.

## Character & Animation Guidelines
- [ ] Provide idle, walking, and activity-specific sprites for students, faculty, and the principal; follow naming conventions documented in `docs/activity_catalog.md`.
- [ ] Keep silhouette readability high at current zoom levels; verify sprites align with tile centres defined in `data/campus_map_v1.json`.
- [ ] Flag any activities lacking bespoke animations so design can prioritise replacements.

## Audio Pass
- [ ] Deliver ambience loops per major zone (dorms, cafeteria, classrooms) and note looping points.
- [ ] Supply alert stingers that map to existing categories (`Overcapacity`, `CurfewViolation`, etc.).
- [ ] Document volume baselines and ducking expectations to inform future mixer implementation.

## Handoff
- [ ] Update this checklist with asset status and repository locations.
- [ ] Log outstanding art/audio requests in `docs/qa_backlog.md` under a new section tagged for presentation.
- [ ] Notify the Producer persona once assets are staged for review.
