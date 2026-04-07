# S4 Contract — Operator Registry

_Status: canonical (V3)_
_Last updated: 2026-04-06_

---

## Registry ID

- **name:** `s4.operator_registry.v3`
- **owner:** `supervisor_shell.py`

---

## Active Actors (2)

These actors are dispatched via OpenClaw CLI by `supervisor_shell.py`:

```json
{
  "contract_version": "s4.operator_registry.v3",
  "active_operators": {
    "op_s4_coverage_analyst": {
      "agent_id": "op_s4_coverage_analyst",
      "role": "Assesses target/scene coverage from asset materialization reports",
      "dispatch_contract": "s4.coverage_analyst_dispatch.v1",
      "input_contract": "s4.asset_materialization_report.v1 (new) or s4.evaluated_candidate_set.v1 (legacy fallback)",
      "output_contract": "s4.coverage_report.v1",
      "output_schema": "coverage_report.schema.json",
      "invocation": "openclaw_cli",
      "phase": 6
    },
    "op_s4_pack_compiler": {
      "agent_id": "op_s4_pack_compiler",
      "role": "Compiles final research pack and sector report from all sector artifacts",
      "dispatch_contract": "s4.pack_compiler_dispatch.v1",
      "input_contract": "s4.coverage_report.v1 + materialization reports",
      "output_contract": "s4.research_pack.v1",
      "output_schema": "research_pack.schema.json",
      "invocation": "openclaw_cli",
      "phase": 7
    }
  }
}
```

---

## Deprecated Actors (4)

These actors are **no longer dispatched**. Their work is performed by helper-direct Python calls from `supervisor_shell.py`:

| Deprecated Actor | Agent ID | Replaced by | Reason | Phase (was) |
|-----------------|----------|-------------|--------|-------------|
| `op_s4_target_builder` | `op_s4_target_builder` | `target_builder.py` helper-direct | LLM actor invented own logic instead of calling helper | 2 |
| `op_s4_web_investigator` | `op_s4_web_investigator` | `web_investigator.py` helper-direct | LLM actor mangled paths | 4 |
| `op_s4_target_research_worker` | `op_s4_target_research_worker` | `s4_query_generator.py` + `s4_image_collector.py` | Entire retrieval approach replaced (Brave -> Serper + GPT-5.4-nano vision) | 5 |
| `op_s4_candidate_evaluator` | `op_s4_candidate_evaluator` | `s4_visual_evaluator.py` | Textual classification replaced by vision evaluation | 5 |

---

## Active pipeline order

```
Phase 2: target_builder.py          (HELPER-DIRECT) S3 entities -> intake + consolidation
Phase 3: batch_manifest_builder.py  (HELPER-DIRECT) intake -> batch manifest
Phase 4: web_investigator.py        (HELPER-DIRECT) intake -> target briefs
Phase 5: s4_asset_pipeline.py       (HELPER-DIRECT) briefs -> query gen + image collect + visual eval
Phase 6: op_s4_coverage_analyst     (OPENCLAW CLI)  materialization reports -> coverage report
Phase 7: op_s4_pack_compiler        (OPENCLAW CLI)  all artifacts -> research pack + sector report
```

---

## Operational rules

### 1. Supervisor dispatches by registry
`supervisor_shell.py` resolves active actors from this registry. No hardcoded names scattered in implementation.

### 2. Schema expectation is part of the registry
The structural expectation of each operator's output is part of the operational contract.

### 3. Helper-direct phases have no dispatch artifact
Only OpenClaw-dispatched actors receive a `{operator_name}_job.json` dispatch artifact. Helper-direct phases are called with explicit arguments.

### 4. Deprecated actors retain agent workspace
Agent workspaces for deprecated actors remain on disk but are not activated. Sessions are cleaned before each run for safety.
