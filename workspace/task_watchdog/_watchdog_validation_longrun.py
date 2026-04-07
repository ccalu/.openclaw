import sys, time
sys.path.append(r"C:\Users\User-OEM\.openclaw\workspace")
from task_watchdog.registry_helpers import register_task, update_task, finish_task

task_id = "watchdog_validation_longrun_001"
register_task({
    "taskId": task_id,
    "taskName": "Watchdog validation long-run test",
    "type": "exec",
    "model": "deterministic/python-local",
    "originChat": "telegram:1962323981",
    "originSession": "telegram_current_session",
    "replyTarget": "current_chat",
    "notifyEveryMinutes": 10,
    "status": "running",
    "summaryHint": "teste controlado do watchdog com duração > 10 min",
    "lastKnownStep": "started",
    "launcher": "Tobias"
})

for minute, step in [(3, "phase_1_waiting"), (7, "phase_2_still_running"), (11, "phase_3_ready_to_finish")]:
    time.sleep(60 * (minute - (0 if step == "phase_1_waiting" else 3 if step == "phase_2_still_running" else 7)))
    update_task(task_id, lastKnownStep=step)

finish_task(task_id, result_summary="teste controlado finalizado com sucesso")
print("done")
