# Local docs read

Primary local docs read from `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory`:

1. `README.md`
2. `docs/04_BRANCH_ARCHITECTURE.md`
3. `docs/05_MULTI_MACHINE_ARCHITECTURE.md`
4. `docs/06_MODEL_STRATEGY.md`
5. `docs/07_BRAINDUMP_OPENCLAW.md`
6. `docs/09_HIERARCHY_AND_STRUCTURE.md`

Ignored on purpose:
- `docs/KnowledgeBase/**` lesson-note dumps
- `workspace_mirror/**` mirrored workspace docs
- unrelated macmini workspace research

## Key local findings

- Target org is explicitly 4 layers: CEO (Tobias) -> Production Manager -> Branch Managers -> specialist agents.
- Department design is shared across clients; account-specific behaviour lives in `accounts/` config, not new agent orgs per channel.
- Context isolation is already a first-class principle: each agent should only load markdown inside its own folder.
- The 10 branch map is already fairly mature and totals about 43 specialists.
- Branch 8 (assembly/render) should remain mostly deterministic.
- QA and Monitoring are separate branches, which is good because evaluation and observability should not be hidden inside production workers.
- Multi-machine design is centralized control plane on M1 with remote execution on M2-M6.
- Model strategy already assumes premium top layer + cheap lower layers + local generation/tooling where possible.

## Tension/ambiguity found

- Some docs describe one central `orchestrator/`; newer docs separate Tobias (CEO) from Production Manager. The newer split is better.
- Local docs state branch managers have isolated workspaces, but shared artefacts are still global. This needs stricter write contracts so agents do not stomp each other.
- The branch list is strong functionally, but org rules for routing, retries, escalation, and approval boundaries are still underspecified.
