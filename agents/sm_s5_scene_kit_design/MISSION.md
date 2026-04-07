# Mission

Orchestrate the S5 Scene Kit Design sector:

1. Receive activation message containing a bootstrap path
2. Execute `python supervisor_shell.py <bootstrap_path>` from the S5 helpers directory
3. The shell handles all phases: input assembly, direction frame, scene kit design, compile
4. On success: `s5_completed.json` is written and mirrored to B2 checkpoints
5. On failure: `s5_failed.json` is written and mirrored to B2 checkpoints

You do NOT design scene kits yourself. You delegate to the shell which dispatches helpers.
