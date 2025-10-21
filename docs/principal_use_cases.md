# Principal Use Cases

This catalog summarizes the hands-on scenarios the principal persona must handle
during daily operations. Each case maps to simulation hooks that Milestone D
introduces so later AI-driven agents can execute these tasks automatically.

## Schedule Overrides
- **Trigger**: A teacher requests schedule adjustments or an event conflicts with
  existing plans.
- **Action**: Replace the affected student’s upcoming blocks with a curated
  sequence (e.g., move a class, insert study hall, add detention).
- **Outcome**: Daily plan updates immediately, conflicts are recalculated, and
  the NPC begins following the injected blocks.

## Student Summons
- **Trigger**: The principal needs to meet a student in the office or redirect
  them after an incident.
- **Action**: Interrupt the current activity (if any), assign a short
  "summoned" block to the destination room, and reroute the NPC with elevated
  priority.
- **Outcome**: The student travels directly to the requested room and resumes
  their routine once the meeting concludes.

## Alert Resolution
- **Trigger**: Simulation raises an incident (missed class, room overcrowding,
  curfew violation).
- **Action**: Inspect alert details, take appropriate follow-up (override,
  summon, broadcast), and mark the alert as acknowledged.
- **Outcome**: Alerts remain visible until acknowledged, enabling auditability
  and ensuring other automation agents do not duplicate work.

## Campus Broadcasts
- **Trigger**: A message must reach a subset of the community (e.g., dorm
  curfew reminder, fire drill announcement).
- **Action**: Issue a text broadcast filtered by roles or rooms. The message is
  captured in the event log for later review.
- **Outcome**: NPCs receive the placeholder signal (logged event) so later
  narrative/AI systems can hook into the broadcast pipeline.
