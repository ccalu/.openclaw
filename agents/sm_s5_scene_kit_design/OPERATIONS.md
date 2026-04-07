# OPERATIONS.md

## Regras operacionais

1. Contexto limpo por activacao.
2. Estado no disco > conversa.
3. Falha explicita > sucesso ambiguo.
4. Nao inventar outputs inexistentes.

## Modelo de execucao — supervisor_shell.py

O SM delega TODA a orquestracao ao `supervisor_shell.py`. O SM e um thin delegation layer.

### Sequencia de execucao

1. Ler bootstrap path da activation message.
2. Validar que o bootstrap path existe no disco.
3. Delegar para o supervisor shell:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S5\helpers\supervisor_shell.py" <bootstrap_path>
   ```
4. O shell faz:
   - Session cleanup para todos os agents S5 (`openclaw sessions cleanup --enforce`)
   - Bootstrap validation + dir creation
   - **Phase 1:** `input_assembly.py` (HELPER-DIRECT) — MiniMax M2.7-HS scene summaries + deterministic linkage
   - **Phase 2:** `direction_frame_builder.py` (HELPER-DIRECT) — MiniMax M2.7-HS global direction frame
   - **Phase 3:** `scene_kit_designer.py` (HELPER-DIRECT) — MiniMax M2.7-HS per-scene kit specs (retry waves)
   - **Phase 4:** `pack_compiler.py` (HELPER-DIRECT) — deterministic compile + sector report
   - **Phase 5:** completion checkpoint + B2 mirror
   - Schema validation gate entre cada phase
   - Checkpoint per-phase em `runtime/phase_checkpoints.json`
   - Resume automatico a partir do ultimo checkpoint se re-executado
5. Verificar resultado: se o shell saiu com exit 0, confirmar que `s5_completed.json` existe.
   Se saiu com exit != 0, confirmar que `s5_failed.json` existe e reportar.

## Dispatch policy

Nenhum actor e dispatchado via OpenClaw CLI em V1.
Tudo e helper-direct com MiniMax M2.7-HS.
O `op_s5_scene_kit_designer` existe para uso futuro mas NAO e usado na V1.

## Failure table

| Phase | Falha | Accao |
|-------|-------|-------|
| input_assembly | sector FAILS | s5_failed.json |
| direction_frame | sector FAILS | s5_failed.json |
| scene_kit_design (partial) | sector CONTINUES | retry waves (ate 3x), scenes faltantes em warnings |
| pack_compiler | sector FAILS | s5_failed.json |

## Stack

- MiniMax M2.7-highspeed via Token Plan Plus-HS (summaries, frame, scene kits)
- Semaphore(10) concurrency + retry/backoff
- Auto-fix de outputs LLM (sequence_position, family_type, null refs, string→array)
- Retry waves automaticas (ate 3x) para scene_kit_designer
- ~8 min, ~$0.15/video (flat rate)

## Limites

- Nao es boundary Paperclip-facing
- Nao es o `b2_director`
- Nao deves fazer o trabalho semantico dos helpers internamente
- Nao deves tentar orquestrar phases manualmente — delega ao supervisor_shell
