# Determinism & Procedure (This Run Only)

Follow this phased loop for **reproducible** behavior without cross-run memory:

1) **PLAN** — Propose a step-by-step plan tied directly to Acceptance IDs (e.g., AC-001). Do not write code yet.
2) **APPROVE** — Wait for explicit approval (or an automated approval hook) before proceeding.
3) **APPLY** — Implement exactly the approved steps, referencing file paths. Create or update tests first where feasible.
4) **VERIFY** — Run tests; report pass/fail per Acceptance ID. If failing, propose a minimal corrective plan and loop.

**Rules**  
- Respect only the current repo, the spec, and files in `runtime/`. Ignore any external memory or past runs.  
- When in doubt, cite the source file path or Acceptance ID you used.  
- Do not introduce conventions beyond what the repo/spec dictates.
