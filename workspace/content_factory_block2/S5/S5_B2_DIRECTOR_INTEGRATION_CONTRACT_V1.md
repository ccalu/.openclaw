# S5 ↔ B2 Director Integration Contract V1

_Status: runtime contract draft_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the preferred **macro integration contract** between:
- the Block 2 control plane (`b2_director` + boundary workflow)
- and S5 as a sector runtime unit

Its purpose is to ensure that S5 enters the Block 2 runtime using the **same macro pattern already validated for earlier sectors**, rather than introducing a new one-off integration style.

This document does **not** define the internal runtime of S5.
It defines the boundary between:
- B2 state progression
- S5 bootstrap
- S5 completion/failure checkpoints
- S5 handoff into S6

---

## 2. Integration principle

The correct integration principle is:

> copy the **shape** of the validated B2 -> sector integration pattern, not the internal content of another sector.

This means S5 should integrate into Block 2 using the same macro rules already used elsewhere:
- `b2_director` decides the next sector
- the director writes a sector request checkpoint
- the boundary launches the sector supervisor
- the sector runs internally behind its supervisor
- the sector writes completion/failure checkpoints
- the boundary reactivates the director
- the director validates the sector handoff and decides the next step

So S5 should be a normal sector in the B2 runtime model, not a special-case integration.

---

## 3. Entry condition for S5

The S5 request checkpoint should be emitted when:
- `b2_director` is reactivated because `s4_completed.json` appeared
- the director validates the macro handoff of S4
- the current block mode requires progression into S5
- the director updates `b2_state.json`
- the director decides that S5 is the next sector

In other words:

> S4 completion does not directly activate S5 on its own.
> The `b2_director` remains the authority that decides whether S5 should start.

---

## 4. Request checkpoint

The director should write:
- `s5_requested.json`

This checkpoint is the macro signal that the boundary should launch the S5 supervisor.

The boundary should then:
- detect `s5_requested.json`
- launch `sm_s5_scene_kit_design`
- later observe `s5_completed.json` / `s5_failed.json`
- reactivate `b2_director`

---

## 5. External face of the sector

The external S5 face seen by B2 should be:
- `sm_s5_scene_kit_design`

This supervisor is the only sector actor the B2 integration layer should need to know directly.

The internal S5 runtime map remains encapsulated behind that supervisor.
The B2 layer should not need to know about the internal S5 helper-direct phases and operator such as:
- `input_assembly.py`
- `direction_frame_builder.py`
- `op_s5_scene_kit_designer`

---

## 6. Preferred bootstrap contract for S5

The preferred bootstrap payload for S5 should be explicit and filesystem-first.

### Conceptual shape

```json
{
  "kind": "s5_start",
  "run_root": "C:/.../run_x",
  "b2_root": "C:/.../run_x/b2",
  "sector_root": "C:/.../run_x/b2/s5",
  "mode": "full_b2",
  "upstream": {
    "s3_completed_path": "C:/.../b2/checkpoints/s3_completed.json",
    "s4_completed_path": "C:/.../b2/checkpoints/s4_completed.json",
    "compiled_entities_path": "C:/.../b2/s3/compiled/compiled_entities.json",
    "research_intake_path": "C:/.../b2/s4/intake/research_intake.json",
    "reference_ready_asset_pool_path": "C:/.../b2/s4/compiled/s4_reference_ready_asset_pool.json",
    "s4_research_pack_path": "C:/.../b2/s4/compiled/research_pack.json",
    "video_context_path": "C:/.../b2/s4/runtime/video_context.json",
    "source_package_path": "C:/.../b2/s3/source/s3_source_package.json"
  }
}
```

### Contract rules

#### Required upstream paths
The bootstrap should explicitly provide the paths S5 needs to begin correctly, especially:
- `compiled_entities_path`
- `research_intake_path`
- `reference_ready_asset_pool_path`
- `video_context_path`
- `source_package_path`
- `s4_completed_path`

#### Optional but preferred upstream path
- `s4_research_pack_path`

This path is useful when available, but should not be treated as a structural hard dependency of the S5 runtime.

---

## 7. Completion checkpoint contract

The preferred macro output checkpoint for successful sector completion is:
- `s5_completed.json`

This checkpoint is the macro handoff contract between S5 and `b2_director`.

### Conceptual shape

```json
{
  "sector": "s5",
  "status": "completed",
  "run_root": "C:/.../run_x",
  "b2_root": "C:/.../run_x/b2",
  "sector_root": "C:/.../run_x/b2/s5",
  "completed_at": "ISO_TIMESTAMP",
  "outputs": {
    "video_direction_frame_path": "C:/.../run_x/b2/s5/compiled/video_direction_frame.json",
    "scene_kit_specs_dir": "C:/.../run_x/b2/s5/scene_kit_specs",
    "scene_kit_pack_path": "C:/.../run_x/b2/s5/compiled/s5_scene_kit_pack.json",
    "sector_report_path": "C:/.../run_x/b2/s5/compiled/s5_sector_report.md"
  },
  "counts": {
    "scene_count_total": 42,
    "scene_kit_specs_generated": 42,
    "scene_kit_specs_valid": 42
  },
  "readiness": {
    "ready_for_s6": true
  }
}
```

---

## 8. Decisions frozen in this contract

### 8.1 `sector_report_path`
`sector_report_path` should be treated as **required** in the completion checkpoint.

Reason:
- it improves inspectability
- it improves operational review/debugging
- it gives the sector a lightweight human-readable summary surface

### 8.2 `s4_research_pack_path`
`s4_research_pack_path` should be treated as **optional but preferred** in the S5 bootstrap.

Reason:
- useful as a compiled upstream context surface
- but should not become a structural hard dependency

### 8.3 Readiness gate
S5 readiness for S6 should be represented by:
- `ready_for_s6 == true`
- plus explicit counts proving macro completeness

So readiness should not rely only on a declarative flag.
It should also carry structural evidence.

---

## 9. Failure checkpoint contract

The preferred macro failure checkpoint is:
- `s5_failed.json`

### Conceptual shape

```json
{
  "sector": "s5",
  "status": "failed",
  "run_root": "C:/.../run_x",
  "sector_root": "C:/.../run_x/b2/s5",
  "failed_at": "ISO_TIMESTAMP",
  "reason": "scene_kit_generation_failed",
  "last_successful_phase": "video_direction_frame_completed",
  "retryable": true
}
```

This checkpoint should give `b2_director` enough macro information to decide:
- retry sectorial
- fail the block
- or later use a degraded path if such a mode is introduced

---

## 10. What `b2_director` should validate on `s5_completed`

When reactivated because `s5_completed.json` appeared, the director should validate at macro level:

### Required output paths exist
- `video_direction_frame_path`
- `scene_kit_specs_dir`
- `scene_kit_pack_path`
- `sector_report_path`

### Readiness flag
- `ready_for_s6 == true`

### Macro completeness evidence
- `scene_kit_specs_generated == scene_count_total`
- `scene_kit_specs_valid == scene_count_total`

This is the correct level of validation for the director.

The director should **not**:
- open every scene kit spec for semantic review
- re-run sector-internal validation logic
- act as a second supervisor of S5

---

## 11. How this should affect `b2_state.json`

When the director decides to open S5, the state should progress to something like:

```json
{
  "block": "b2",
  "status": "running",
  "current_stage": "s5",
  "completed_stages": ["s3", "s4"],
  "failed_stages": [],
  "next_stage": "s6",
  "last_event": "s5_requested",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

After valid `s5_completed` handoff and decision to open S6:

```json
{
  "block": "b2",
  "status": "running",
  "current_stage": "s6",
  "completed_stages": ["s3", "s4", "s5"],
  "failed_stages": [],
  "next_stage": null,
  "last_event": "s5_completed",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

If S5 terminally fails:

```json
{
  "block": "b2",
  "status": "failed",
  "current_stage": "s5",
  "completed_stages": ["s3", "s4"],
  "failed_stages": ["s5"],
  "next_stage": null,
  "last_event": "s5_failed",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

---

## 12. Summary

The preferred B2 ↔ S5 macro contract is now:
- `b2_director` decides S5 entry after validating `s4_completed.json`
- the director writes `s5_requested.json`
- the boundary launches `sm_s5_scene_kit_design`
- S5 runs behind its supervisor and internal runtime
- S5 writes `s5_completed.json` or `s5_failed.json`
- the boundary reactivates `b2_director`
- the director validates the declared handoff paths and readiness evidence
- only then does the director open S6

This preserves the validated Block 2 integration shape while allowing S5 to keep its own internal runtime architecture.
