# Campus Layout Notes

## Required Rooms & Capacities
- **Dorm_North** (12 students) — bunk layout for first-year students with two exits into the west corridor.
- **Dorm_South** (12 students) — mirrors Dorm_North for upper-class students and sits closer to the gym for after-hours routines.
- **Dorm_Commons** (16 capacity) — shared lounge linking dormitories to the main hall.
- **Gymnasium** (20 capacity) — practice and club events with dual doors onto the west connector.
- **Library** (18 capacity) — quiet stacks positioned on the mezzanine overlooking the central atrium.
- **Infirmary** (4 beds) — small nurse station adjacent to Counseling for quick referrals.
- **Counseling** (3 offices) — guidance staff with rapid access to classrooms and the atrium.
- **Cafeteria** (32 seats) — central dining hall with dedicated Kitchen service entrance.
- **Kitchen** (6 staff) — hot line prep area connected to Cafeteria and the east service hall.
- **Administration** (6 staff) — principal and admin support cluster.
- **Security** (4 staff) — overnight monitoring desk with sightlines to the courtyard exit.
- **Courtyard** (24 capacity) — open-air garden for free periods and evening walks.
- **Classroom_STEM** (16 seats) — lab benches plus storage on the north-east wing.
- **Classroom_Humanities** (18 seats) — seminar classroom with movable desks in the mid-east wing.
- **Classroom_Arts** (14 seats) — studio and club activities near the auditorium entry.
- **Faculty_Offices** (8 staff) — planning space adjacent to the east stairwell.

## Traffic Flow Summary
- Morning: Dorm wings → Dorm_Commons → Cafeteria → east classrooms.
- Midday: Classrooms → Cafeteria → Courtyard or Library for study blocks.
- Afternoon Clubs: Cafeteria → Classroom_Arts / Gymnasium → Courtyard cooldown.
- Evening: Courtyard → Dorm_Commons → respective Dorm wing.
- Staff circulation: Faculty_Offices/Kitchen/Security feed into Administration and Counseling across the atrium spine.

## Placeholder Asset Hooks
- Tile atlas: `data/tilesets/placeholder.tsx` (48px grid) used for all layers.
- Layers expected by editor tooling: `Ground`, `Decor`, `Collision`, `RoomBounds`, `SpawnPoints`, `Waypoints`, `RoomLabels`.
- Room label anchors correspond to `rooms[].name` so placeholder text overlays align with debug rendering.

## Pathfinding Anchors
- Wayfinding relies on wide (2-tile minimum) connectors at `(12, 9-21)` for the west wing and `(26, 7-22)` for the east wing.
- Courtyard, Administration, and Security share a continuous southern concourse to avoid bottlenecks when schedules overlap.
- Door coordinates are embedded within walkable tiles; every spawn point resides on a walkable tile inside its owning room.
