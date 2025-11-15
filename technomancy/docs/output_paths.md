# Output Paths (Authoritative, v1.2)

**Production (final deliverables):**
- Code & tests: `/school_sim/**`
- Documentation: `/docs/**`
- Runtime data: `/school_sim/runtime/{logs,saves,scenes}`
- Configs: `/school_sim/configs/{events.yaml,game.yaml}`
- Assets: `/school_sim/assets/{images,audio}`

**Technomancy (staging & artifacts):**
- Staging (temporary): `/technomancy/deliverables/{src,tests,docs}`
- Merge scripts (kept): `/technomancy/deliverables/scripts/merge_m<id>.py|.sh`
- Artifacts kept (persist): `/technomancy/{logs,plans,matrix}`
- Runtime (ephemeral; auto-clean): `/technomancy/runtime/**`

**Rules:**
- No shippable deliverables may remain under `/technomancy/deliverables/**` after a milestone completes.
- Merge scripts must copy staged files into `/school_sim/**` and `/docs/**`, then remove duplicates/obsoletes.
