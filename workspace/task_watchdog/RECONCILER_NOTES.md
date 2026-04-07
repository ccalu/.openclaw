# Reconciler MVP — Notes

## 1. Diagnóstico do Problema Original

O `watchdog.py` original:
- Lê `active_tasks.json` e confia cegamente no campo `status`
- Envia notificação de "running" a cada N minutos enquanto `status == "running"`
- Nunca consulta o estado real do runtime
- Resultado: tasks zombie ficam como `running` para sempre

**Caso concreto encontrado:**
- Task `retest_claude_code_sidecar_20260328_160800` (childSessionKey: `agent:main:subagent:f45bf7bf-f558-4aa8-b227-ed4c626ae536`)
- Presente em `active_tasks.json` como `status: running` desde 28 Mar 2026
- Em `subagents/runs.json`: `endedAt` definido, `endedReason: subagent-complete`, `outcome: {status: ok}`
- A task estava morta há +2 dias mas continuava a gerar notificações falsas

## 2. Estados Mínimos Implementados

| Estado | Significado |
|--------|-------------|
| `spawned` | Registada mas ainda sem `startedAt` no runtime |
| `running` | Runtime confirma sessão activa |
| `stalled` | Sem registo de runtime após STALL_MINUTES (30 min) |
| `orphaned` | Sem registo de runtime após ORPHAN_MINUTES (60 min) — terminal |
| `completed` | Runtime confirma `endedReason: subagent-complete` ou `outcome.status: ok` |
| `failed` | Runtime confirma erro/timeout |

## 3. Arquitectura do Reconciler

### Ficheiros adicionados
- `task_watchdog/reconciler.py` — lógica de reconciliação independente

### Ficheiros alterados
- `task_watchdog/watchdog.py` — main() integra reconciler antes do evaluate_tasks; evaluate_tasks suporta os novos estados

### Fluxo de execução
```
watchdog.main()
  ├── load active_tasks.json
  ├── reconcile_all(tasks) → [reconciler.py]
  │     ├── load subagents/runs.json
  │     ├── para cada task: find_run_for_session(childSessionKey)
  │     │     ├── run encontrado + endedAt → completed/failed
  │     │     ├── run encontrado + sem endedAt → running (confirmado)
  │     │     └── run não encontrado:
  │     │           ├── < 30 min → keep as-is (spawned/running)
  │     │           ├── 30-60 min → stalled
  │     │           └── > 60 min → orphaned (terminal)
  │     └── retorna {remaining, archived, notifications}
  ├── evaluate_tasks(remaining) → notificações periódicas normais
  ├── merge notifications (reconciler tem prioridade, dedup por taskId)
  └── save active_tasks.json (só remaining)
```

### Deduplicação de notificações
- Notificações terminais (completed/failed/orphaned): controladas por `terminalNotifiedStatus` no task
- Notificações periódicas (running/stalled): controladas por `lastNotifiedAt` + `notifyEveryMinutes`
- Merge no main: tasks notificadas pelo reconciler não recebem notificação adicional do evaluate_tasks

## 4. Runtime Source of Truth

Ficheiro lido: `C:\Users\User-OEM\.openclaw\subagents\runs.json`
- Formato: `{"version": 1, "runs": {<runId>: {childSessionKey, endedAt, outcome, endedReason, ...}}}`
- Indexado por `runId` mas o reconciler pesquisa por `childSessionKey`
- Sem acesso a infra externa — puramente local

## 5. Notas de Teste/Uso

### Testar com task viva
```json
// Adicionar a active_tasks.json:
[{
  "taskId": "test_live_001",
  "taskName": "Test live task",
  "type": "subagent",
  "status": "running",
  "childSessionKey": "agent:main:subagent:SOME-ACTIVE-UUID",
  "startedAt": "2026-03-30T10:00:00-03:00"
}]
```
→ Se o UUID existir em runs.json sem endedAt: permanece running
→ Se o UUID não existir: stalled após 30 min, orphaned após 60 min

### Testar com task zombie
```json
[{
  "taskId": "test_zombie_001",
  "taskName": "Zombie task",
  "status": "running",
  "childSessionKey": "agent:main:subagent:f45bf7bf-f558-4aa8-b227-ed4c626ae536"
}]
```
→ O reconciler detecta o run em `runs.json`, vê `endedAt` definido, → completed

### Testar sem childSessionKey (tasks manuais)
- Tasks sem `childSessionKey` não têm lookup no runtime
- Behavior: stalled/orphaned baseado apenas em tempo decorrido

### Executar
```bash
cd C:\Users\User-OEM\.openclaw\workspace
python -m task_watchdog.watchdog
```

### Thresholds (ajustáveis em reconciler.py)
```python
STALL_MINUTES = 30   # sem runtime record → stalled
ORPHAN_MINUTES = 60  # sem runtime record → orphaned (terminal)
```

## 6. Limitações Conhecidas do MVP

1. **Tasks sem `childSessionKey`**: só podem ser reconciliadas por tempo, não por runtime lookup. Se o agente não registar o key, ficam zombies até ORPHAN_MINUTES.

2. **runs.json cresce infinitamente**: o reconciler lê o ficheiro inteiro a cada run. Para volumes grandes (>10k runs), adicionar índice invertido por `childSessionKey` ao ficheiro.

3. **Runs muito antigos**: runs.json pode ter entradas de semanas atrás. O reconciler não filtra por data — mas isso é bom: garante que tasks antigas são reconciliadas correctamente.

4. **Races**: se watchdog cron e manual run coincidirem, pode haver double-write em `active_tasks.json`. O write já usa `.tmp` + rename (atómico) — risco baixo.

5. **`resultSummary` truncado**: o reconciler pega nos primeiros 300 chars do `frozenResultText`. Para o summary completo, ver `task_history.jsonl`.
