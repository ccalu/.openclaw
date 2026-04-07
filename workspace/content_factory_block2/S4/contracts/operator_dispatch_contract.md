# S4 Contract — Operator Dispatch Contract

_Status: canonical (V3)_
_Last updated: 2026-04-06_

---

## Contract ID

- **name:** `s4.operator_dispatch.v1`
- **owner:** `supervisor_shell.py`

---

## V3 Dispatch Model

In V3, `supervisor_shell.py` is the sole dispatcher. Only **2 actors** are dispatched via OpenClaw CLI. The remaining 4 actors are **deprecated** — their work is performed by helper-direct Python calls.

### Active actors (OpenClaw CLI dispatch)

| Actor | Phase | Role |
|-------|-------|------|
| `op_s4_coverage_analyst` | 6 | Reads materialization reports, produces coverage report |
| `op_s4_pack_compiler` | 7 | Compiles final research pack and sector report |

### Deprecated actors (replaced by helper-direct)

| Actor | Replaced by | Reason |
|-------|------------|--------|
| `op_s4_target_builder` | `target_builder.py` | LLM actor invented own logic instead of calling helper |
| `op_s4_web_investigator` | `web_investigator.py` | LLM actor mangled paths |
| `op_s4_target_research_worker` | `s4_query_generator.py` + `s4_image_collector.py` | Entire retrieval approach replaced |
| `op_s4_candidate_evaluator` | `s4_visual_evaluator.py` | Textual classification replaced by vision evaluation |

---

## Delivery model

The dispatch contract is delivered in two forms:

1. **Dispatch artifact on disk** (source of truth)
2. **Short activation message** pointing to that artifact

The artifact on disk is the source of truth. The activation message exists only to activate the correct agent with minimal context.

---

## Dispatch artifact path

```text
{sector_root}/dispatch/{operator_name}_job.json
```

---

## Common fields (active operators)

```json
{
  "contract_version": "s4.{operator}_dispatch.v1",
  "kind": "s4_{operator}_dispatch",
  "job_id": "job_006_pt_guinle_001",
  "video_id": "video_abc123",
  "account_id": "006",
  "language": "pt-BR",
  "operator_name": "op_s4_coverage_analyst",
  "sector_root": "C:/.../b2/sectors/s4_asset_research",

  "runtime": {
    "status_path": "C:/.../runtime/{operator_name}/status.json",
    "checkpoint_path": "C:/.../runtime/{operator_name}/checkpoint.json"
  },

  "execution_policy": {
    "max_attempt": 1,
    "timeout_seconds": 1800,
    "failure_mode": "explicit",
    "partial_output_allowed": false
  }
}
```

---

## Per-operator specifics

### `op_s4_coverage_analyst`

- **Contract version:** `s4.coverage_analyst_dispatch.v1`
- **Input artifacts:** `intake_path` + `target_materialization_report_paths` (new V3 format) + `evaluated_candidate_set_paths` (legacy fallback)
- **Output artifact:** `s4.coverage_report.v1` at `output.coverage_report_path`
- **Schema:** `coverage_report.schema.json`

### `op_s4_pack_compiler`

- **Contract version:** `s4.pack_compiler_dispatch.v1`
- **Input artifacts:** `intake_path` + `target_materialization_report_paths` + `coverage_report_path`
- **Output artifact:** `s4.research_pack.v1` at `output.research_pack_path`
- **Additional output:** `output.sector_report_path` (markdown)
- **Schema:** `research_pack.schema.json`

---

## Invariants

### 1. Source of truth on disk
The operator must treat the dispatch artifact as the source of truth for activation.

### 2. Clean context per activation
Each activation is independent. The operator cannot depend on conversational carry-over.

### 3. Output written to indicated path
The operator must produce final output at exactly the path indicated in the dispatch.

### 4. Explicit failure > silence
If the operator cannot complete the job, it must write explicit failure signals to `runtime.status_path`.

### 5. Conversational response does not close the job
The job is only considered complete when the expected artifact exists and is structurally valid.

---

## Success condition

A dispatch is considered successful when:

1. Output path exists
2. JSON opens without error
3. Minimum schema structure is present
4. Content is coherent with `operator_name`

---

## Failure condition

A dispatch is considered failed when any of these occur:

- Timeout exceeded without valid output
- Output absent
- Invalid JSON
- Invalid schema
- Semantically incompatible output
- Status indicates explicit failure
