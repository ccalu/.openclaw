# MEMORY.md — sm_s3_visual_planning

## Runtime learnings

- ACP must not be treated as the default runtime substrate for `supervisor -> operator` in this environment.
- The proven primitive is:

```text
exec -> openclaw agent --agent <operator_id> --message "...dispatch path..." --json
```

- Disk is the source of truth. Do not over-claim artifact creation in conversational summaries.
- A narrow run can end as `degraded_completed` for two very different reasons:
  1. bad degraded = launch/runtime failure
  2. acceptable degraded = only one operator intentionally executed
- Always distinguish these two.
- Dispatch generation is first-class runtime substrate. Missing dispatch means operator failure regardless of agent quality.
- Before compiling, validate actual files written by operators.

## Operational checklist

1. Validate bootstrap from disk.
2. Generate activation plan.
3. Generate dispatch files.
4. Launch operators via CLI primitive, not ACP fallback.
5. Validate operator artifacts on disk.
6. Compile sector artifacts.
7. Write final checkpoints honestly.
