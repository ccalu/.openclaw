# CONTEXT.md

## Estado actual — 2026-04-06

O foco operacional imediato continua no **Bloco 2 — produção visual**, com avanço material no **S4 — Asset Research**.

### Situação consolidada do S4
- O S4 deixou de usar como core o pipeline antigo centrado em `research_worker` + `candidate_evaluator` + `asset_materializer`.
- O handoff **S3 -> S4** foi fortalecido com uma camada real de **target consolidation** em `target_builder.py`, em vez de conversão quase 1:1 das entidades do S3.
- O miolo actual do S4 passou a ser um **asset pipeline visual unificado**, mais orientado a retrieval e avaliação visual real.
- A execução longa do sector está concentrada em `supervisor_shell.py` como orquestrador determinístico com checkpoint-resume, com o agent `sm_s4_asset_research` a funcionar como delegador para esse substrate.

### Shape actual do S4
Fases actuais do sector:
1. bootstrap
2. target_builder (helper-direct)
3. batch_manifest (determinístico)
4. web_investigator (helper-direct)
5. asset_pipeline (helper-direct)
   - context extraction via GPT-5.4-nano
   - query generation via GPT-5.4-nano
   - image collection via Serper.dev + download paralelo + pHash dedup
   - visual evaluation via GPT-5.4-nano vision
6. coverage_analyst (actor OpenClaw)
7. pack_compiler (actor OpenClaw)
8. completion + B2 mirror

### Actor map actual
- **Activos como actors OpenClaw:** `op_s4_coverage_analyst`, `op_s4_pack_compiler`
- **Activos como helpers/substrate:** `target_builder`, `web_investigator`, `s4_asset_pipeline` e submódulos
- **Actor supervisor:** `sm_s4_asset_research` delega para `supervisor_shell.py`
- **Deprecated / não canónicos:** `op_s4_target_builder`, `op_s4_web_investigator`, `op_s4_target_research_worker`, `op_s4_candidate_evaluator`

### Artefacto canónico do miolo
- O artefacto central do novo miolo passou a ser `asset_materialization_report.json`.
- `candidate_set.json` e `evaluated_candidate_set.json` deixaram de ser a fonte de verdade do core visual.
- Coverage e pack foram/alvo de adaptação para ler o novo formato com fallback legado quando necessário.

### Evidência operacional já provada
- O refactor visual do S4 foi implementado e testado E2E.
- O fluxo **S3 -> S4** ficou provado com target consolidation via helper-direct.
- O fluxo **W3 -> S3 -> S4 -> B2 completed** também foi confirmado E2E.
- A run consolidada reportada em 2026-04-06 ficou em ~6m51s, com 34 entidades S3, 28 targets activos + 6 skipped, 75 assets aprovados, schema PASS, `s4_completed` escrito e mirrored ao B2.

### Questões de arquitectura/documentação agora em curso
- O S4 entrou numa fase de **consolidação documental e absorção de learnings**.
- Já existe um plano V3 para actualizar docs, contracts, runbooks, troubleshooting, padrões reutilizáveis, memória e checklists.
- A regra importante é: **não tratar atalhos tácticos como padrão de sector**.
  - Ex.: OpenAI/Serper keys hardcoded em Python devem ser documentadas como desvio táctico temporário, não arquitectura aprovada.

### Novo estado do S5
A conversa avançou bastante e o S5 já ganhou shape muito mais real.

O que já foi fechado:
- o S5 é o sector de **scene kit design**, não de composição final da cena
- o `scene_kit_spec` é o objecto central do sector
- a shape V1 draft do `scene_kit_spec` já existe e foi validada em revisão conceptual
- a linguagem central das famílias é `family_type + family_intent`
- a camada editorial das famílias ficou leve (`editorial_notes`)
- a `input assembly layer` do S5 foi desenhada com base no upstream real do Quitandinha
- em V1, `relevant_targets[]` ficam determinísticos
- o `video_direction_frame` foi confirmado como artefacto novo real do S5

### Posição estratégica actual
O S4 já não está em estado “falta fazer funcionar”.
O estado actual é:
- S4 core novo funcional
- S4 reference readiness provado em E2E
- S5 input e output já razoavelmente desenhados
- a próxima frente correcta é o **runtime / operational flow do S5**
- só depois faz sentido avançar com materialização/implementação do sector
