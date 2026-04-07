# OPERATIONS.md

## Regras operacionais

1. Contexto limpo por activacao.
2. Estado no disco > conversa.
3. Falha explicita > sucesso ambiguo.
4. Nao inventar outputs inexistentes.
5. Nao considerar um operator concluido apenas por resposta textual.

## Modelo de execucao — V3 Pipeline (supervisor_shell.py)

O SM delega TODA a orquestracao ao `supervisor_shell.py`. O SM e um thin delegation layer.

### Sequencia de execucao

1. Ler bootstrap do path recebido na activation message.
2. Validar que o bootstrap path existe no disco.
3. Delegar para o supervisor shell:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\supervisor_shell.py" <bootstrap_path>
   ```
4. O shell faz:
   - Session cleanup para todos os agents S4 (`openclaw sessions cleanup --enforce`)
   - Bootstrap validation + dir creation
   - **Phase 2:** `target_builder.py` (HELPER-DIRECT) — GPT-5.4-nano consolidation
   - **Phase 3:** `batch_manifest_builder.py` (HELPER-DIRECT) — deterministic
   - **Phase 4:** `web_investigator.py` (HELPER-DIRECT) — target briefs
   - **Phase 5:** `s4_asset_pipeline.py` (HELPER-DIRECT) — context extraction + query gen + Serper image collect + GPT-5.4-nano vision eval
   - **Phase 6:** `op_s4_coverage_analyst` (OPENCLAW CLI) — coverage report
   - **Phase 7:** `op_s4_pack_compiler` (OPENCLAW CLI) — research pack + sector report
   - **Phase 8:** completion checkpoint + B2 mirror
   - Schema validation gate entre cada phase
   - Checkpoint per-phase em `runtime/phase_checkpoints.json`
   - Resume automatico a partir do ultimo checkpoint se re-executado
5. Verificar resultado: se o shell saiu com exit 0, confirmar que `s4_completed.json` existe.
   Se saiu com exit != 0, confirmar que `s4_failed.json` existe e reportar.

## Dispatch policy — V3

Apenas 2 actors sao dispatchados via OpenClaw CLI:
- `op_s4_coverage_analyst` (phase 6)
- `op_s4_pack_compiler` (phase 7)

Os restantes 4 actors estao DEPRECATED — substituidos por helper-direct:
- ~~op_s4_target_builder~~ -> `target_builder.py`
- ~~op_s4_web_investigator~~ -> `web_investigator.py`
- ~~op_s4_target_research_worker~~ -> `s4_query_generator.py` + `s4_image_collector.py`
- ~~op_s4_candidate_evaluator~~ -> `s4_visual_evaluator.py`

## Failure table

| Phase | Falha | Accao |
|-------|-------|-------|
| target_builder | sector FAILS | s4_failed.json |
| web_investigator | sector FAILS | s4_failed.json |
| asset_pipeline (partial) | sector CONTINUES | gaps explicitados no coverage/pack |
| coverage_analyst | sector FAILS | s4_failed.json |
| pack_compiler | sector FAILS | s4_failed.json |

## Stack V3

- GPT-5.4-nano via OpenAI API (consolidation, query gen, vision eval)
- Serper.dev Google Images API (image discovery)
- pHash dedup (near-duplicate detection)
- Video context injection (era/style coherence)
- ~3 min, ~$0.14/video

## Limites

- Nao es boundary Paperclip-facing
- Nao es o `b2_director`
- Nao deves fazer o trabalho semantico dos helpers internamente
- Nao deves chamar operators fora do registry oficial
- Nao deves tentar orquestrar phases manualmente — delega ao supervisor_shell
