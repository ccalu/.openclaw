# S3 — Supervisor (`sm_s3_visual_planning`)

## Objectivo

Este documento descreve o papel do supervisor do S3 e o que acontece **depois que ele é activado** pelo workflow paperclip-facing do sector.

O foco aqui é:

- o momento em que o supervisor acorda
- a sequência inicial de trabalho do supervisor
- como ele decide quais operators activar
- como ele invoca os operators reais do OpenClaw
- que artefactos ele prepara antes da execução semântica da operator layer

Este documento ainda não detalha o ciclo completo de validação, retries, compilação final e fecho do sector. O foco é o arranque operativo do supervisor e o wiring com os operators.

---

## Papel do supervisor

O `sm_s3_visual_planning` é o **control plane interno** do sector S3.

Ele não é a boundary layer com o Paperclip. Essa responsabilidade pertence ao workflow paperclip-facing do sector.

O supervisor também não deve executar directamente a semântica especializada dos operators.

O seu papel é:

- validar o arranque do sector
- assumir formalmente o controlo do S3 naquele job
- resolver o activation plan do sector
- preparar os payloads de dispatch
- invocar os operators correctos
- acompanhar o estado da execução interna do sector
- posteriormente agregar, validar e compilar o output do sector

---

## O que o supervisor recebe no arranque

O supervisor deve ser activado com um bootstrap message contract estruturado, preparado pelo workflow do sector.

Exemplo conceptual:

```json
{
  "kind": "s3_start",
  "job_id": "job_006_pt_guinle_001",
  "run_root": "...",
  "sector_root": ".../b2_s3_visual_planning",
  "source_package_path": ".../b2_s3_visual_planning/inputs/s3_source_package.json",
  "checkpoints_dir": ".../b2_s3_visual_planning/checkpoints",
  "operators_dir": ".../b2_s3_visual_planning/operators",
  "compiled_dir": ".../b2_s3_visual_planning/compiled",
  "logs_dir": ".../b2_s3_visual_planning/logs",
  "dispatch_dir": ".../b2_s3_visual_planning/dispatch"
}
```

---

## Sequência inicial do supervisor

Quando o supervisor acorda, ele **não deve começar imediatamente pela semântica**.

A sequência correcta começa assim:

### Fase 1 — Validate bootstrap

O supervisor valida:

- se o bootstrap message contract está completo
- se os paths recebidos existem
- se o `s3_source_package.json` abre correctamente
- se a estrutura mínima do sector está presente
- se o job está num estado consistente para o S3 começar

Se esta validação falhar:

- o supervisor deve falhar limpo
- deve escrever um artefacto de erro/checkpoint correspondente
- não deve prosseguir para dispatch de operators

---

### Fase 2 — Assume sector

Depois da validação do bootstrap, o supervisor deve marcar que o S3 foi formalmente assumido.

Exemplo de artefacto conceptual:

- `s3_supervisor_started.json`
- ou `s3_step1_supervisor_started.json`

Este artefacto deve registar:

- timestamp de arranque do supervisor
- payload de arranque recebido
- paths principais do sector
- estado de bootstrap validado

Isto separa claramente:

- fim do bootstrap do workflow
- início do controlo interno do sector pelo supervisor

---

### Fase 3 — Resolve activation plan

Só depois do arranque validado o supervisor deve decidir quais operators entram neste vídeo.

Para isso, ele precisa de:

- `s3_source_package.json`
- config da conta
- regras de `entity_focus`

A função desta fase é resolver:

- quais operators ficam activos
- quais ficam inactivos
- com que prioridade/foco cada operator entra
- que famílias semânticas são particularmente prioritárias neste vídeo/conta

O activation plan deve ser lido como uma decisão de dispatch do sector, não como uma lista fixa e cega.

---

### Fase 4 — Write activation plan artifact

A decisão de activação deve ser persistida em artefacto próprio.

Exemplo conceptual:

- `operator_activation_plan.json`

Este ficheiro deve registar:

- operators activos
- operators inactivos
- `entity_focus` resolvido
- prioridades derivadas da conta
- contexto mínimo da decisão

Isto melhora:

- observabilidade
- debugging
- recovery
- auditabilidade da decisão do supervisor

---

### Fase 5 — Prepare operator dispatch payloads

Depois do activation plan, o supervisor prepara os payloads operacionais de cada operator activo.

O modelo correcto passa a ser:

- um **common dispatch envelope** partilhado por todos os operators
- um **operator-specific payload** por operator

O supervisor deve escrever um payload de dispatch por invocação.

Exemplo conceptual de directório:

```text
{sector_root}/dispatch/
  human_subject_extractor_job.json
  environment_location_extractor_job.json
  object_artifact_extractor_job.json
  symbolic_event_extractor_job.json
```

---

## Operator layer do S3

A operator layer do S3 foi simplificada estruturalmente para 4 operators principais, mantendo uma taxonomy semântica rica.

### Operators actuais

1. `human_subject_extractor`
2. `environment_location_extractor`
3. `object_artifact_extractor`
4. `symbolic_event_extractor`

### Princípio estrutural

Os operators são responsáveis por:

- análise semântica delimitada
- extração/estruturação por família semântica
- escrita do output canónico no disco

Os operators **não** são responsáveis por:

- compile global do sector
- merge entre famílias
- dedupe inter-operator global
- handoff do sector

Essas responsabilidades pertencem preferencialmente ao supervisor + substrate.

---

## Wiring: como o supervisor invoca os operators

### Princípio-base

O supervisor **não deve invocar os operators como funções internas Python**.

Ele deve invocar **agents reais do OpenClaw**.

Exemplos conceptuais de agent ids:

- `op_s3_human_subject_extractor`
- `op_s3_environment_location_extractor`
- `op_s3_object_artifact_extractor`
- `op_s3_symbolic_event_extractor`

---

### Primitive de invoke

Arquitecturalmente, o supervisor precisa de uma primitive equivalente a um **agent turn invoke**.

Para o ambiente actual do primeiro run narrow, esse detalhe técnico já está fechado:

```text
exec -> openclaw agent --agent <operator_agent_id> --session-id <unique-run-operator-session> --message "..." --json --timeout 1800
```

Ou seja, nesta fase o supervisor deve usar um launch real via CLI/OpenClaw agent e não ACP/sessions_spawn para este hop.

Regras obrigatórias deste hop:

- não tentar ACP como caminho primário
- o registry canónico desta fase é fechado em 4 operators: `human_subject_extractor`, `environment_location_extractor`, `object_artifact_extractor`, `symbolic_event_extractor`
- não cair silenciosamente para subset de 1 operator se o activation plan pediu mais operators activos
- usar `session-id` único por run e por operator para evitar contexto acumulado entre vídeos/runs
- usar timeout explícito de 1800 segundos nas chamadas aos operators
- usar literalmente os paths declarados no bootstrap/dispatch, sem reconstrução heurística nem normalização Unicode “parecida”
- não absorver internamente o trabalho semântico dos operators como substituto do dispatch real
- não tratar outputs paralelos/derivados (`locations`, `artifacts`, `atmosphere`, `era_context`) como substitutos dos outputs canónicos dos operators
- espelhar o resultado final do sector no macro checkpoint do bloco (`b2/checkpoints/s3_completed.json` ou `s3_failed.json`)

O que está definido aqui é o contrato arquitectural:

- target agent
- mensagem estruturada curta
- path para dispatch payload
- output path esperado

---

### O que o supervisor envia ao operator

O supervisor deve usar um modelo em duas camadas:

#### 1. artefacto de dispatch no disco

Exemplo:

```text
{sector_root}/dispatch/human_subject_extractor_job.json
```

#### 2. mensagem curta do turn

A mensagem enviada ao operator deve apontar para esse dispatch payload.

Exemplo conceptual:

> Execute o job descrito em `.../dispatch/human_subject_extractor_job.json`. Leia esse payload, use o `source_package_path` como base do vídeo, produza o output canónico em `output_path` e termine apenas quando o ficheiro final estiver escrito.

Isto é preferível a embutir todo o conteúdo do job inline na mensagem.

---

## Common dispatch envelope

O dispatch do supervisor para qualquer operator deve seguir um envelope comum.

### Objectivo do envelope

Dar ao operator um contrato padronizado de:

- identidade da execução
- contexto do vídeo/conta
- foco semântico da invocação
- referência explícita ao source package
- scope de análise
- snapshot de config da conta
- paths de output/checkpoint/status/log
- execution policy

### Estrutura conceptual v1

```json
{
  "contract_version": "s3.operator_dispatch.v1",
  "workflow_run_id": "wf_2026_04_03_001",
  "sector_run_id": "s3_2026_04_03_001",
  "supervisor_run_id": "sup_s3_001",
  "operator_run_id": "op_human_subject_001",
  "operator_name": "human_subject_extractor",

  "account_id": "acc_06",
  "channel_id": "channel_06_pt",
  "project_id": "cf_visual_v1",
  "video_id": "video_abc123",
  "language": "pt-BR",

  "entity_focus": {
    "families": ["characters", "human_figures", "groups"],
    "priority_mode": "strict_precision",
    "coverage_mode": "balanced"
  },

  "source_package": {
    "path": "runs/video_abc123/b2_s3_visual_planning/inputs/s3_source_package.json",
    "format": "s3_source_package.v1"
  },

  "analysis_scope": {
    "scene_ids": ["scene_001", "scene_002", "scene_003"],
    "full_video": true
  },

  "account_rules": {
    "precision_profile": "strict_specificity",
    "priority_entities": ["historical_figures", "specific_locations", "palaces"],
    "salience_threshold": "high",
    "notes": "Prefer exact historical specificity over generic category labeling."
  },

  "output": {
    "output_path": "runs/video_abc123/b2_s3_visual_planning/operators/human_subject_extractor/output.json",
    "expected_schema": "s3.human_subject_extractor.output.v1",
    "write_mode": "replace"
  },

  "runtime": {
    "checkpoint_path": "runs/video_abc123/b2_s3_visual_planning/operators/human_subject_extractor/checkpoint.json",
    "status_path": "runs/video_abc123/b2_s3_visual_planning/operators/human_subject_extractor/status.json",
    "log_path": "runs/video_abc123/b2_s3_visual_planning/operators/human_subject_extractor/log.md"
  },

  "execution_policy": {
    "max_attempt": 1,
    "timeout_seconds": 900,
    "failure_mode": "explicit",
    "partial_output_allowed": false
  },

  "operator_payload": {}
}
```

O detalhe e a evolução deste contract ficam documentados em `operators.md`.

---

## Registry conceptual de operators

O supervisor deve conhecer o mapeamento entre `operator_name` e `agent_id` correspondente.

Exemplo conceptual:

```json
{
  "human_subject_extractor": "op_s3_human_subject_extractor",
  "environment_location_extractor": "op_s3_environment_location_extractor",
  "object_artifact_extractor": "op_s3_object_artifact_extractor",
  "symbolic_event_extractor": "op_s3_symbolic_event_extractor"
}
```

Este mapeamento pode existir como config local do supervisor ou artefacto equivalente.

---

## Critério de sucesso de um operator

O supervisor não deve considerar um operator concluído só porque ele respondeu textual ou conversationalmente com “done”.

O critério real de sucesso deve ser:

1. o `output_path` esperado existe
2. o JSON abre sem erro
3. o output corresponde ao `operator_name`
4. o schema mínimo esperado está presente

Só depois dessa verificação o supervisor deve considerar o operator como concluído.

---

## Modelo inicial de execução

Nesta fase do desenho, o supervisor deve assumir:

- dispatch paralelo dos operators activos
- um payload de dispatch por operator
- um output canónico por operator
- validação posterior pelo supervisor

Ou seja:

- 1 operator activo
- 1 dispatch job
- 1 invoke turn
- 1 `output_path`

---

## Resumo operativo do supervisor ao acordar

Quando o `sm_s3_visual_planning` acorda, a sequência esperada é:

1. validar bootstrap recebido
2. assumir formalmente o sector
3. resolver activation plan
4. gerar `operator_activation_plan.json`
5. preparar dispatch payloads por operator
6. resolver `agent_id` correspondente a cada operator
7. invocar os operators activos via agent-turn primitive do OpenClaw

---

## O que este documento ainda não cobre

Este documento pára no momento em que:

- os operators já foram preparados para execução
- e o wiring de dispatch já está definido

Ainda não cobre em detalhe:

- monitorização dos operators em execução
- retries selectivos
- validação completa dos outputs
- compilação de `compiled_entities.json`
- artefacto final do sector
- handoff para o S4

Esses pontos devem ser tratados separadamente.

---

## Estado desta definição

**Status:** v2 da activação operativa do supervisor do S3

Esta definição fecha:

- o papel do supervisor ao arrancar
- a separação entre bootstrap workflow e runtime interno do S3
- a lógica de activation plan
- o wiring conceptual de dispatch dos operators
- o common dispatch envelope v1
- o mapa actual de 4 operators principais

Ainda falta fechar as fases posteriores do sector e o contract exacto de cada operator.
