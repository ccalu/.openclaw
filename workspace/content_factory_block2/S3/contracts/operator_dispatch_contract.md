# S3 Contract — Operator Dispatch Contract

## Objectivo

Este documento formaliza o contract canónico usado pelo `sm_s3_visual_planning` para despachar operators do S3.

Ele transforma em interface explícita o que já estava descrito narrativamente em `supervisor.md` e `operators.md`.

---

## Contract ID

- **name:** `s3.operator_dispatch.v1`
- **owner:** `sm_s3_visual_planning`
- **consumers:**
  - `op_s3_human_subject_extractor`
  - `op_s3_environment_location_extractor`
  - `op_s3_object_artifact_extractor`
  - `op_s3_symbolic_event_extractor`

---

## Delivery model

O contract é entregue de duas formas complementares:

1. **artefacto de dispatch no disco**
2. **mensagem curta de activação do agent**, apontando para esse artefacto

O artefacto no disco é a fonte de verdade.
A mensagem curta existe apenas para activar o agent correcto com contexto mínimo.

---

## Artefacto esperado

Exemplo de path:

```text
{sector_root}/dispatch/{operator_name}_job.json
```

Exemplo:

```text
{sector_root}/dispatch/human_subject_extractor_job.json
```

---

## Shape canónica

```json
{
  "contract_version": "s3.operator_dispatch.v1",
  "workflow_run_id": "wf_2026_04_03_001",
  "sector_run_id": "s3_2026_04_03_001",
  "supervisor_run_id": "sup_s3_001",
  "operator_run_id": "op_human_subject_001",
  "operator_name": "human_subject_extractor",

  "job_id": "job_006_pt_guinle_001",
  "video_id": "video_abc123",
  "account_id": "006",
  "channel_id": "channel_06_pt",
  "project_id": "cf_visual_v1",
  "language": "pt-BR",

  "entity_focus": {
    "families": ["characters", "human_figures", "groups"],
    "priority_mode": "strict_precision",
    "coverage_mode": "balanced"
  },

  "source_package": {
    "path": ".../inputs/s3_source_package.json",
    "format": "s3_source_package.v1"
  },

  "analysis_scope": {
    "scene_ids": ["scene_001", "scene_002"],
    "full_video": true
  },

  "account_rules": {
    "precision_profile": "strict_specificity",
    "priority_entities": ["historical_figures", "specific_locations"],
    "salience_threshold": "high",
    "notes": "Prefer exact specificity over generic labeling."
  },

  "output": {
    "output_path": ".../operators/human_subject_extractor/output.json",
    "expected_schema": "s3.human_subject.output.v1",
    "write_mode": "replace"
  },

  "runtime": {
    "checkpoint_path": ".../operators/human_subject_extractor/checkpoint.json",
    "status_path": ".../operators/human_subject_extractor/status.json",
    "log_path": ".../operators/human_subject_extractor/log.md"
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

---

## Required fields

### Execution identity

- `contract_version`
- `workflow_run_id`
- `sector_run_id`
- `supervisor_run_id`
- `operator_run_id`
- `operator_name`

### Business/job identity

- `job_id`
- `video_id`
- `account_id`
- `language`

### Semantic context

- `entity_focus`
- `source_package.path`
- `analysis_scope`
- `account_rules`

### Output contract

- `output.output_path`
- `output.expected_schema`

### Runtime paths

- `runtime.checkpoint_path`
- `runtime.status_path`
- `runtime.log_path`

### Execution policy

- `execution_policy.max_attempt`
- `execution_policy.timeout_seconds`
- `execution_policy.failure_mode`
- `execution_policy.partial_output_allowed`

### Operator-specific section

- `operator_payload`

---

## Invariants

### 1. Fonte de verdade no disco
O operator deve tratar o artefacto de dispatch como fonte de verdade da activação.

### 2. Contexto limpo por activação
Cada activação deve ser interpretada como independente. O operator não pode depender de carry-over conversacional.

### 3. Output escrito no path indicado
O operator deve produzir o output final exactamente em `output.output_path`.

### 4. Falha explícita > silêncio
Se o operator não conseguir completar o job, deve escrever sinais de falha explícita em `status_path` e/ou `checkpoint_path`.

### 5. Resposta conversacional não fecha o job
O job só conta como concluído quando o artefacto esperado existir e for estruturalmente válido.

---

## Operator-specific payloads

### `human_subject_extractor`

```json
{
  "target_families": ["characters", "human_figures", "groups", "factions", "crowds"],
  "identity_resolution": "high",
  "include_aliases": true,
  "group_detection": true,
  "specificity_bias": "account_driven"
}
```

### `environment_location_extractor`

```json
{
  "target_families": ["locations", "places", "environments", "settings"],
  "specific_location_bias": "account_driven",
  "include_architectural_context": true,
  "merge_nearby_variants": true,
  "specificity_bias": "account_driven"
}
```

### `object_artifact_extractor`

```json
{
  "target_families": ["objects", "props", "artifacts", "vehicles", "machines", "animals", "documents", "maps", "interfaces"],
  "historical_specificity_bias": "account_driven",
  "include_functional_objects": true,
  "merge_duplicate_mentions": true,
  "specificity_bias": "account_driven"
}
```

### `symbolic_event_extractor`

```json
{
  "target_families": ["symbols", "motifs", "abstract_visual_concepts", "natural_phenomena", "weather", "disasters", "event_visual_entities"],
  "allow_non_literal_translation": true,
  "event_detection": true,
  "atmospheric_relevance_bias": "account_driven",
  "specificity_bias": "account_driven"
}
```

---

## Activation message pattern

Mensagem curta recomendada do supervisor para o operator:

> Execute o job descrito em `{dispatch_path}`. Leia o payload do disco, use `source_package.path` como base do vídeo, escreva o output final em `output.output_path`, actualize os artefactos de runtime e termine apenas quando o ficheiro final estiver persistido ou a falha explícita tiver sido registada.

---

## Success condition

Um dispatch é considerado bem-sucedido apenas quando:

1. `output.output_path` existe
2. o JSON abre sem erro
3. a estrutura mínima do schema esperado está presente
4. o conteúdo é coerente com `operator_name`

---

## Failure condition

O dispatch é considerado falhado quando qualquer uma destas condições ocorrer:

- timeout excedido sem output válido
- output ausente
- JSON inválido
- schema inválido
- output semanticamente incompatível com o operator
- checkpoint/status final indica falha explícita
