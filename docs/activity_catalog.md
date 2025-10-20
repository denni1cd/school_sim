# Activity Catalog

This catalog enumerates the canonical activities used throughout the boarding school simulation. Each entry lists the
supported room types, the default duration (expressed as HH:MM), an interaction text key, and baseline state metadata
that activity classes may expose to placeholder UIs or analytics systems.

## Canonical Activities

### Sleeping
- **Room Types:** Dormitory, Infirmary
- **Default Duration:** 08:00
- **Interaction Key:** `activity.sleeping`
- **State Metadata:**
  - `posture`: `lying`
  - `lights`: `off`
  - `intensity`: `quiet`

### Eating
- **Room Types:** Cafeteria, DiningHall
- **Default Duration:** 01:00
- **Interaction Key:** `activity.eating`
- **State Metadata:**
  - `noise_level`: `moderate`
  - `seating`: `communal`

### Studying
- **Room Types:** Classroom, Library, StudyHall
- **Default Duration:** 02:00
- **Interaction Key:** `activity.studying`
- **State Metadata:**
  - `focus`: `high`
  - `materials`: `books`

### Teaching
- **Room Types:** Classroom, Auditorium, Lab
- **Default Duration:** 02:00
- **Interaction Key:** `activity.teaching`
- **State Metadata:**
  - `focus`: `instruction`
  - `audience`: `students`

### Recreation
- **Room Types:** Gymnasium, Courtyard, Commons
- **Default Duration:** 01:30
- **Interaction Key:** `activity.recreation`
- **State Metadata:**
  - `noise_level`: `lively`
  - `equipment`: `varies`

### Maintenance
- **Room Types:** Maintenance, Administration, Grounds
- **Default Duration:** 01:00
- **Interaction Key:** `activity.maintenance`
- **State Metadata:**
  - `task`: `upkeep`
  - `tools`: `basic`

### Medical
- **Room Types:** Infirmary, Counseling
- **Default Duration:** 00:45
- **Interaction Key:** `activity.medical`
- **State Metadata:**
  - `focus`: `care`
  - `privacy`: `elevated`

### Discipline
- **Room Types:** Administration, Counseling
- **Default Duration:** 00:30
- **Interaction Key:** `activity.discipline`
- **State Metadata:**
  - `focus`: `reflection`
  - `tone`: `serious`

### Idle
- **Room Types:** Any
- **Default Duration:** 00:15
- **Interaction Key:** `activity.idle`
- **State Metadata:**
  - `focus`: `light`
  - `posture`: `standing`

## Aliases

Schedule and interaction content may refer to variant activity names ("breakfast", "lights_out_north"). These aliases
map to the canonical activities above and may add state overrides such as the dorm wing or meal type. The structured
mapping lives in `config/activities.yaml` and feeds the activity factory at runtime.
