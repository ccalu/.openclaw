# S3 Contract — Operator Registry

## Objectivo

Este documento formaliza o registry canónico que liga:

- nome lógico do operator
- agent id OpenClaw correspondente
- família macro coberta
- schema de output esperado

Este registry permite ao `sm_s3_visual_planning` despachar agents reais sem ambiguidade.

---

## Registry ID

- **name:** `s3.operator_registry.v1`
- **owner:** `sm_s3_visual_planning`

---

## Registry canónico

```json
{
  "contract_version": "s3.operator_registry.v1",
  "operators": {
    "human_subject_extractor": {
      "agent_id": "op_s3_human_subject_extractor",
      "family_group": "human_subjects",
      "expected_schema": "s3.human_subject.output.v1",
      "default_enabled": true
    },
    "environment_location_extractor": {
      "agent_id": "op_s3_environment_location_extractor",
      "family_group": "environment_locations",
      "expected_schema": "s3.environment_location.output.v1",
      "default_enabled": true
    },
    "object_artifact_extractor": {
      "agent_id": "op_s3_object_artifact_extractor",
      "family_group": "object_artifacts",
      "expected_schema": "s3.object_artifact.output.v1",
      "default_enabled": true
    },
    "symbolic_event_extractor": {
      "agent_id": "op_s3_symbolic_event_extractor",
      "family_group": "symbolic_events",
      "expected_schema": "s3.symbolic_event.output.v1",
      "default_enabled": true
    }
  }
}
```

---

## Tabela operacional

- `human_subject_extractor`
  - agent id: `op_s3_human_subject_extractor`
  - macro family: `human_subjects`
  - schema: `s3.human_subject.output.v1`

- `environment_location_extractor`
  - agent id: `op_s3_environment_location_extractor`
  - macro family: `environment_locations`
  - schema: `s3.environment_location.output.v1`

- `object_artifact_extractor`
  - agent id: `op_s3_object_artifact_extractor`
  - macro family: `object_artifacts`
  - schema: `s3.object_artifact.output.v1`

- `symbolic_event_extractor`
  - agent id: `op_s3_symbolic_event_extractor`
  - macro family: `symbolic_events`
  - schema: `s3.symbolic_event.output.v1`

---

## Regras obrigatórias

### 1. Um nome lógico -> um agent id
Cada `operator_name` deve apontar para exactamente um `agent_id` canónico.

### 2. O supervisor despacha por registry
O supervisor não deve hardcodar nomes soltos espalhados pela implementação. Deve resolver o target agent por este registry.

### 3. Schema esperado é parte do registry
A expectativa estrutural do output faz parte do contract operacional do operator.

### 4. `default_enabled` não substitui activation plan
O activation plan do vídeo ainda decide se um operator entra ou não. `default_enabled` apenas indica baseline estrutural do sector.

---

## Uso esperado pelo supervisor

Ao resolver o activation plan, o supervisor deve:

1. ler este registry
2. seleccionar os operators activos
3. mapear cada `operator_name` para o `agent_id`
4. injectar o `expected_schema` no dispatch payload
5. invocar o agent correspondente

---

## Fora de escopo

Este documento não define:

- o conteúdo completo do dispatch payload
- a política de retry
- a lógica de compile do sector
- a semântica interna de cada operator
