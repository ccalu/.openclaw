# MEMORY.md - Memória de Longo Prazo (Tobias)

_Última actualização: 2026-04-02_

---

## 🏭 Content Factory - O que sei

A Content Factory tem hoje um pipeline automatizado funcional (`content_factory_v3`), mas ainda demasiado rígido: cada conta tende a repetir o mesmo processo criativo. O objectivo é migrar de automação engessada para um sistema de agentes que decidem melhor o processo editorial de cada vídeo.

### Sistemas importantes
- **KMS**: gestor centralizado de chaves API, cooldowns, disponibilidade e custos.
- **Dataset System**: pesquisa imagens reais em arquivos públicos; hoje ainda com uso limitado.
- **ComfyUI**: geração local de imagens (SDXL + Flux), custo marginal ~0.
- **WhisperX local**: existe como serviço local para transcrição/alinhamento, mas deve ser usado com cuidado por custo de GPU.

### Situação actual
- O V3 continua a ser a principal fonte de semântica operacional real.
- O foco actual não é "inventar tudo de novo", mas extrair do V3 o que já funciona e reestruturar isso em arquitectura de agentes mais limpa, modular e evolutiva.
- **Viragem de 2 Apr 2026**: o foco saiu de S1/S2 e passou a ser o **Bloco 2 — produção visual**, com agentes OpenClaw + Playwright.
- Bloco 1 e Bloco 3 ficam como CFV3 existente, expostos como mini-orquestradores invocáveis pelo Paperclip.

---

## 🤖 Arquitectura de Agentes

### Arquitectura-alvo
4 níveis hierárquicos:
- **Nível 1**: Tobias (CEO) → estratégia, arquitectura, supervisão
- **Nível 2**: Production Manager → orquestra produção
- **Nível 3**: Managers/supervisores de sector → coordenam sub-departamentos
- **Nível 4**: agentes/operators/skills → execução específica

Uma equipa, múltiplos clientes, com config por conta e workspaces/documentação separados onde fizer sentido.

### Estado real actual
A implementação está agora focada no **Bloco 2 — Produção Visual**, composto por:
- **S3 — Visual Planning** (em curso — base arquitectural criada)
- **S4 — Asset Research** (a destrinchar a seguir)
- **S5 — Visual Direction** (a destrinchar — ainda não fechado)
- **S6 — Image/Video Generation** (a destrinchar — ainda não fechado)

O trabalho anterior em PM/VO/S1 foi descontinuado operacionalmente. Esses agentes foram removidos. O Bloco 1 e o Bloco 3 serão wrappados pelo Claude Code como mini-orquestradores invocáveis pelo Paperclip.

---

## ⚙️ Model Routing

### Princípios
- começar com o modelo mais leve que resolva bem
- escalar só quando necessário
- optimizar resultado/custo, não prestígio
- usar substrate determinístico primeiro; LLM semântico só onde acrescenta julgamento real

### Distribuição prática
- **GPT-5.4 (Tobias)** → estratégia, arquitectura, decisões de alto nível
- **Modelos baratos / leves** → research, parsing, validação auxiliar, subtarefas exploratórias
- **Claude / modelos de maior qualidade** → análise mais complexa ou judgment calls quando necessário
- **Modelos locais (Qwen/Ollama, quando alinhados)** → tarefas repetitivas e custo-eficiente
- **ComfyUI / Flux / SDXL** → imagem local
- **Gemini TTS via KMS** → geração de áudio

### Regra importante
Protótipos funcionais podem usar soluções temporárias, mas não devem virar padrão de produção por acidente. Ex.: operator LLM implementado por chamada directa em Python pode servir para validar pipeline, mas não substitui automaticamente a arquitectura final esperada.

---

## 🖥️ Esta Máquina

Máquina pessoal do Lucca + principal de produção. Tratar com cuidado máximo.
- Ryzen 9 5950X / RTX 4070 Super / 128GB RAM / Windows 10
- ComfyUI + modelos de imagem locais instalados
- Claude Code roda em paralelo na mesma máquina
- Infra local relevante para produção e experimentação de agentes

---

## 📓 Decision Log

Máx ~20 entradas. Comprimir as antigas quando necessário.

- [2026-03-25] [SETUP] OpenClaw instalado e Tobias configurado
- [2026-03-25] [SECURITY] Exec ask on-miss + regras de segurança reforçadas no workspace
- [2026-03-25] [DECISÃO] OpenClaw como framework de agentes
- [2026-03-25] [DECISÃO] GPT-5.4 Pro como modelo principal do Tobias
- [2026-03-26] [DECISÃO] Hierarquia de 4 níveis: CEO → PM → managers/supervisores → agentes
- [2026-03-26] [DECISÃO] Implementação incremental: 2 → 5 → 12 → 42 agentes
- [2026-03-30] [DECISÃO] PM deve tratar a PUB sheet como verdade operacional, não como soberania estratégica
- [2026-03-30] [DECISÃO] PM formalizado com modos `auto_select`, `filtered_select` e `direct_select`
- [2026-03-30] [REGRA] `filtered_select` não pode cair silenciosamente em auto irrestrito
- [2026-03-30] [REGRA] `direct_select` não pode trocar silenciosamente para outro canal inválido
- [2026-03-30] [DECISÃO] VO deve falhar explicitamente com `run_already_exists` se o run root já existir
- [2026-03-30] [DECISÃO] S1 aceite como protótipo funcional para validação de pipeline, mas não como arquitectura final de runtime
- [2026-03-30] [DECISÃO] S2 deve seguir a direcção `tts_generator` → `audio_transcriber` → validator → `timestamp_aligner` → `bible_updater`
- [2026-04-02] [DECISÃO] Viragem estratégica: Bloco 2 visual é o foco central; Bloco 1 e Bloco 3 preservados como CFV3 invocável
- [2026-04-02] [DECISÃO] Paperclip como orquestrador global; pipeline dividido em mini-orquestradores paperclip-facing
- [2026-04-02] [DECISÃO] Regra central: Paperclip invoca workflows → workflows invocam supervisores → supervisores invocam operadores
- [2026-04-02] [DECISÃO] S3 input-base: `video_context` + `script_overview` + `scenes[]`, derivado de `screenplay_analysis.json`
- [2026-04-02] [DECISÃO] Output dos operadores S3 vive no disco (output_path JSON), não em resposta conversacional
- [2026-04-02] [LIMPEZA] Workspace e agents do ciclo S1/PM/VO removidos; só `main` existe em `.openclaw/agents/`

---

## 🧠 Lições Aprendidas

- [2026-03-27] [PREFERENCE] Quando Tobias lançar subagentes ou tarefas longas, Lucca quer sempre ser avisado quando terminar e receber updates a cada 10 minutos enquanto estiver em execução.
- [2026-03-27] [PREFERENCE] Quando houver incerteza operacional/técnica real, Tobias deve parar, pensar melhor e, se ainda não souber, acionar pesquisa barata antes de responder com confiança.
- [2026-03-27] [PREFERENCE] Em perguntas com forte componente de research, Tobias tem liberdade para lançar múltiplos subagentes baratos e priorizar docs oficiais + sinais recentes de comunidade.
- [2026-03-30] [PREFERENCE] Ao desenhar agentes, supervisores, operators, skills, workflows ou arquitectura, Lucca quer um processo component-first / discussion-first / boundary-first.
- [2026-03-30] [LESSON] O processo correcto é: primeiro destrinchar missão, limites, responsabilidades, dependências e documentação; só depois implementar.
- [2026-03-30] [LESSON] Quando uma decisão envolve repo docs vs workspace docs vs implementação vs operação do agente, Tobias deve separar explicitamente essas camadas.
- [2026-03-31] [PREFERENCE] Quando Lucca pedir trabalho futuro, nocturno, periódico ou em background, Tobias deve explicitar e, quando fizer sentido, validar qual mecanismo operacional vai usar: `TASKS.md`, `HEARTBEAT.md`, `cron` ou sessão persistente/subagente.
- [2026-04-01] [DECISÃO] O contract obrigatório do `scene_director` foi simplificado para um modelo text-first: `scene_local_id`, `scene_title`, `scene_summary`, `narrative_function`, `narration_original`; a garantia mecânica passou para o substrate Python.
- [2026-04-01] [LESSON] É preciso distinguir explicitamente o workspace principal do Tobias (`.openclaw/workspace`) dos workspaces individuais dos agents (`.openclaw/agents/...`) e actualizar também a memória/contexto do workspace principal quando houver marcos importantes.
- [2026-04-01] [STATUS] S1 saiu da fase de arquitectura frouxa e avançou bastante; PM e VO já foram realizados como agents OpenClaw reais, o fluxo `PM -> VO -> ready_for_s1` já foi provado, o gargalo antigo do screenplay foi vencido, e o choke point activo deslocou-se para o lane `tts_polish`.
- [2026-04-02] [STATUS] S3 tem base arquitectural criada em `.openclaw/workspace/S3/`: `inputs.md`, `architecture.md`, `workflow_bootstrap.md`, `supervisor.md`. Próximo: monitorização de operadores, retries, compilação, handoff para S4.
- [2026-04-03] [DECISÃO] Bloco 2 passa a ser uma unidade paperclip-facing única; o interior (`S3 -> S4 -> S5 -> S6`) deve ser orquestrado no OpenClaw por um `b2_director` e não sector a sector no Paperclip.
- [2026-04-03] [DECISÃO] O primeiro teste do B2 será deliberadamente **S3-only**, para validar a integração real Paperclip -> B2 -> S3 antes de expandir para S4/S5/S6.
- [2026-04-03] [DECISÃO] O modelo correcto do B2 no ambiente actual é uma state machine baseada em estado persistido, checkpoints e reentradas discretas; não depende de sessões persistentes thread-bound.
- [2026-04-03] [DECISÃO] O actor do lado Paperclip para o Bloco 2 chamar-se-á **Perseus**; o actor interno do OpenClaw manter-se-á como `b2_director`.
- [2026-04-03] [DECISÃO] O S3 foi fechado em 4 operators principais: `op_s3_human_subject_extractor`, `op_s3_environment_location_extractor`, `op_s3_object_artifact_extractor`, `op_s3_symbolic_event_extractor`.
- [2026-04-03] [REGRA] Contexto limpo por activação tornou-se regra obrigatória para director, supervisores e operators do B2/S3.
- [2026-04-03] [DECISÃO] Todos os agents desta fase do B2 devem usar GPT-5.4 mini via OpenAI OAuth.
- [2026-04-03] [STATUS] Foi criado o directório documental `.openclaw/workspace/content_factory_block2/` com docs centrais do B2 e do S3, incluindo `B2_runtime_control_flow.md`, `B2_director.md`, `EXECUTION_PLAN.md`, `EXECUTION_STATE.md` e a pasta `S3/`.
- [2026-04-03] [STATUS] Foi materializado o workspace local base de `.openclaw/agents/b2_director/` com `IDENTITY.md`, `MISSION.md`, `CONTEXT.md`, `CONTRACT.md` e `OPERATIONS.md`.
- [2026-04-03] [LESSON] WebChat / Control UI / Nerve não suportam hoje `sessions_spawn` persistente com `mode:"session" + thread:true` para subagents normais; no ambiente actual a continuidade correcta deve apoiar-se em estado persistido, reentradas discretas, tasks/cron/sessões nomeadas quando necessário, e não em thread binding.
- [2026-04-03] [LESSON] ACP não deve ser tratado como substrate central do B2; no ambiente actual o hop correcto supervisor -> operator provou-se via `exec -> openclaw agent --agent <id> --message ... --json`, enquanto a arquitectura macro correcta continua a ser state-machine com checkpoints e verdade no disco.
- [2026-04-03] [LESSON] Pasta de agent e docs locais não bastam: um agent só conta como materializado quando aparece em `openclaw agents list` e executa um turno real. Isto foi um erro real no `b2_director` e deve virar checklist obrigatória para todos os sectores futuros.
- [2026-04-03] [LESSON] Resumos conversacionais dos agents não são fonte de verdade operacional. Para B2/S3, checkpoints, outputs persistidos, `status.json`, `checkpoint.json` e artefactos compilados no disco devem sempre prevalecer sobre o que o agent diz que fez.
- [2026-04-03] [LESSON] Um operator pode correr “de verdade” e ainda assim violar o contract actual. `environment_location_extractor` e `symbolic_event_extractor` inicialmente escreveram shapes antigos; a validação correcta precisa exigir runtime real + schema canónico, não apenas existência de output.
- [2026-04-03] [STATUS] O `b2_director` ficou finalmente provado em runtime real para: bootstrap activo, bootstrap idempotente/no-op, e resume `s3_completed -> b2_completed` em `mode=s3_only`.
- [2026-04-03] [STATUS] Os 4 operators do S3 ficaram provados em runs reais via primitive canónica (`human_subject`, `environment_location`, `object_artifact`, `symbolic_event`), após corrigir shapes legados e pipeline de dispatch.
- [2026-04-03] [STATUS] O bloqueio central que faltava para o Perseus caiu: o hop real `sm_s3_visual_planning -> operator` foi finalmente provado sem ACP, via CLI `openclaw agent`, e o remaining `degraded_completed` dos narrow runs passou a significar escopo parcial de teste, não falha infra/runtime.
- [2026-04-03] [LESSON] Antes de abrir qualquer novo sector do B2, deve ser usado o checklist oficial `content_factory_block2/SECTOR_PREFLIGHT_CHECKLIST.md` para congelar runtime materialization, contracts, dispatch, operator validation, supervisor validation, director validation e readiness gate para Paperclip/Perseus.
- [2026-04-06] [STATUS] O S4 foi refactorado de um miolo textual fragmentado (`research_worker` + `candidate_evaluator` + `asset_materializer`) para um core visual unificado com `target_builder` a consolidar o handoff S3->S4 e `s4_asset_pipeline` a fazer context extraction, query generation, image collection e visual evaluation.
- [2026-04-06] [STATUS] O actor map real do S4 ficou reduzido: `sm_s4_asset_research` delega para `supervisor_shell.py`; `op_s4_coverage_analyst` e `op_s4_pack_compiler` permanecem como actors activos; `op_s4_target_builder`, `op_s4_web_investigator`, `op_s4_target_research_worker` e `op_s4_candidate_evaluator` ficaram deprecated / não canónicos.
- [2026-04-06] [STATUS] O artefacto canónico do novo core do S4 passou a ser `asset_materialization_report.json`; coverage e pack precisaram ser adaptados para ler o novo formato com fallback legado.
- [2026-04-06] [STATUS] O fluxo S3 -> S4 com target consolidation via helper-direct foi provado E2E, e também o fluxo W3 -> S3 -> S4 -> B2 completed ficou confirmado em runtime real.
- [2026-04-06] [LESSON] O S4 mostrou que over-materialization de actors no miolo pode piorar clareza e robustez; quando o substrate determinístico + helper-direct controla melhor paths, artefactos e validação, essa simplificação pode ser a arquitectura mais correcta do sector.
- [2026-04-06] [LESSON] Shortcuts tácticos que funcionam (ex.: OpenAI/Serper keys hardcoded em Python) devem ser documentados como desvios temporários, não como padrão aprovado para sectores futuros.
- [2026-04-07] [STATUS] O S4 ganhou uma nova camada real de `reference readiness`: o evaluator passou a gerar sidecar `.reference_ready.json` por asset aprovado e um compilado sector-level `s4_reference_ready_asset_pool.json` com grouped views para consumo downstream.
- [2026-04-07] [STATUS] Esta nova camada do S4 foi provada em E2E sem degradação relevante de custo/latência (~7m34s, ~$0.14, 93 chamadas GPT-5.4-nano), com 61 sidecars gerados e 1 compiled pool útil para o S5.
- [2026-04-07] [STATUS] O output de reference readiness do S4 ficou semanticamente forte para V1: `depicts`, `depiction_type`, `reference_value`, `preserve_if_used`, `scene_relevance` e `reasoning_summary` mostraram-se úteis e accionáveis para selecção downstream de `reference_inputs[]`.
- [2026-04-07] [LESSON] A arquitectura correcta desta camada do S4 é em duas camadas: sidecar por asset como verdade granular local + compiled pool como selection surface downstream. O pool não deve virar verdade independente; deve ser derivado dos sidecars.
- [2026-04-07] [LESSON] O principal refinement pendente desta frente não é arquitectural, mas de calibragem semântica: evitar over-tagging em `reference_value` (especialmente `composition_hint` e `mood_reference`) sem reabrir o desenho da solução.
- [2026-04-07] [STATUS] O S5 deixou de ser pensado como “visual direction” no sentido estreito e foi consolidado como sector de **scene kit design**: S4 fornece grounding factual/referências, S5 desenha o `scene_kit_spec`, S6 materializa o kit, S7 resolve editorialmente a cena.
- [2026-04-07] [DECISÃO] O objecto central do S5 em V1 é `scene_kit_spec`, e a sua shape draft foi fechada em 6 secções: `scene_core`, `scene_direction`, `applied_global_constraints`, `kit_strategy`, `asset_families[]`, `delivery_expectations`.
- [2026-04-07] [DECISÃO] A linguagem central de cada família no S5 passou a ser `family_type + family_intent`; `family_type` sozinho foi considerado vago demais para orientar o S6.
- [2026-04-07] [DECISÃO] A camada editorial da família ficou leve em V1: `editorial_notes` texto livre, sem enum editorial pesada.
- [2026-04-07] [DECISÃO] O input do S5 foi fechado como uma **input assembly layer** baseada no upstream real do Quitandinha: cena/narrativa + S3 grounding + S4 reference layer + global direction frame.
- [2026-04-07] [DECISÃO] Em V1, `scene_summary` e `narrative_function` do S5 serão derivados na input assembly; `relevant_targets[]` serão determinísticos; `reference_ready_assets[]` virão deterministicamente do caminho `scene -> linked_target_ids -> reference_ready_asset_pool`.
- [2026-04-07] [DECISÃO] O `video_direction_frame` foi confirmado como artefacto novo do S5; parte pode ser derivada de `video_context.json`, mas grounding baseline / motion policy / kit complexity ceiling / constraints relevantes precisam nascer nesta camada.
- [2026-04-07] [DECISÃO] `motion_allowed` não é decisão livre da LLM do S5 em V1; a política preferida ficou `motion_policy: first_10_scenes_only`, injectada deterministicamente.
- [2026-04-07] [LESSON] O S5 não deve escolher a composição final da cena. O scene kit existe para preparar o espaço de assets e de possibilidade editorial; a resolução composicional final pertence ao S7.
- [2026-04-07] [LESSON] O upstream real do Quitandinha revelou dois regimes operacionais para o S5: cenas com suporte de referência do S4 e cenas com pouca/nenhuma referência, onde o S5 terá de apoiar-se mais em texto + S3 grounding + global frame e orientar o S6 para geração mais livre.

