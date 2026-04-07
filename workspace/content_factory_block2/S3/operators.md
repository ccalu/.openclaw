# S3 — Operators

## Objectivo

Este documento centraliza a definição da operator layer do S3 (Visual Planning).

O seu papel é consolidar:

- a lógica geral da operator layer
- a separação entre analysis operators e compile/merge logic
- a taxonomy rica de entidades visuais cobertas pelo sector
- o mapa actual dos operators do S3
- o common dispatch contract do supervisor -> operator
- o papel do config por conta no comportamento dos operators
- a definição v1 consolidada dos 4 operators principais

Este documento ainda não fecha o contract final e imutável de cada operator individualmente. O objectivo desta versão é fixar uma v1 operacional suficientemente clara para implementação inicial e testes do S3.

---

## Princípio estrutural

A operator layer do S3 segue a seguinte separação:

### Camada A — extraction / normalization operators

Os operators fazem:

- análise semântica delimitada
- extração de entidades visualmente relevantes
- estruturação do output por família semântica
- escrita de output canónico no disco

Os operators não devem ser responsáveis por:

- compile global do sector
- merge inter-operator
- dedupe global entre famílias
- validação final do sector
- handoff para o S4

### Camada B — compile / merge logic

A agregação, dedupe, validação cruzada e compilação do sector devem ficar preferencialmente no:

- supervisor do S3
- substrate / camada mecânica de apoio

Esta separação existe para manter os operators semanticamente focados e evitar distribuir responsabilidade de pipeline por múltiplos agents.

---

## Taxonomy rica de entidades visuais

O S3 deve preservar uma taxonomy rica. O objectivo não é empobrecer o sistema para simplificar a implementação.

Famílias semânticas relevantes incluem:

- characters / human figures
- groups / factions / crowds
- locations / places
- environments / settings
- objects / props
- vehicles / machines
- animals / creatures
- documents / maps / letters / interfaces
- symbols / motifs / abstract visual concepts
- historical artifacts / cultural items
- natural phenomena / weather / disasters
- event-visual entities

Esta lista não precisa ser vista como um conjunto fechado e imutável, mas sim como o universo de cobertura actual que o sector precisa conseguir representar.

---

## Rich taxonomy != operator explosion

Uma decisão estrutural importante do S3 é:

> riqueza da taxonomy semântica não implica explosão do número de operators.

Ou seja:

- o sistema pode reconhecer muitas famílias/tipos de entidades
- o config por conta pode variar bastante
- o `entity_focus` pode mudar fortemente entre contas
- e ainda assim a operator layer pode manter um número controlado de operators estáveis

Esta decisão reduz complexidade operacional sem sacrificar profundidade semântica.

---

## Mapa actual de operators do S3

A operator layer actual do S3 passa a ser composta por 4 operators principais.

1. `human_subject_extractor`
2. `environment_location_extractor`
3. `object_artifact_extractor`
4. `symbolic_event_extractor`

Esta decomposição procura equilibrar:

1. preservação de riqueza semântica
2. fronteiras cognitivas relativamente estáveis
3. facilidade de dispatch e observabilidade
4. menor complexidade de compile/retry

---

## Papel do config por conta

O config por conta é uma peça central do comportamento dos operators.

A função do config não é decidir se um operator existe ou não existe. A função dele é modular o comportamento dos operators existentes.

Isso inclui, entre outros:

- `entity_focus`
- famílias prioritárias
- nível de precisão exigido
- sensibilidade à especificidade histórica/geográfica
- thresholds de salience
- coverage expectations
- viés de extracção compatível com o nicho/canal

### Exemplos conceptuais

#### Conta com foco histórico-arquitectónico
Pode exigir:
- máxima precisão em figuras históricas
- máxima precisão em palácios, casas, edifícios e lugares específicos
- maior rejeição de output genérico

#### Conta de guerra
Pode exigir:
- maior prioridade para armamentos
- navios
- tanques
- facções
- mapas
- locais de batalha

#### Conta com histórias muito antigas
Pode exigir mais sofisticação em:
- artefactos antigos
- contexto civilizacional
- simbologia
- reconstrução plausível
- entidades menos directamente observáveis

O desenho da operator layer deve permitir este grau de especialização por conta sem multiplicar operators à força.

---

## Common dispatch contract

O supervisor deve invocar cada operator através de um contract padronizado.

A ideia é evitar dispatch por prompt improvisado e garantir uma superfície estável entre supervisor e operator.

O modelo base é:

1. **common dispatch envelope**
2. **operator-specific payload**

---

## Common dispatch envelope — v1

### Função

Este envelope carrega o contexto operacional comum necessário para qualquer operator do S3.

Ele deve incluir:

- identidade da execução
- contexto da conta/canal/projecto/vídeo
- `entity_focus`
- source package
- scope de análise
- snapshot de regras da conta
- output contract
- runtime paths
- execution policy

### Estrutura conceptual

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

---

## Interpretação do envelope

### Identidade da execução
- `contract_version`
- `workflow_run_id`
- `sector_run_id`
- `supervisor_run_id`
- `operator_run_id`
- `operator_name`

Serve para rastreabilidade, observabilidade, retries e debug.

### Contexto de negócio
- `account_id`
- `channel_id`
- `project_id`
- `video_id`
- `language`

Serve para situar o operator no universo editorial correcto.

### Contexto semântico
- `entity_focus`

Serve para dizer que famílias estão prioritárias e com que filosofia de cobertura/precisão aquela invocação foi feita.

### Fonte de verdade
- `source_package`

O operator não deve depender de contexto conversacional solto. A fonte de verdade do vídeo deve ser explicitamente referenciada.

### Scope
- `analysis_scope`

Permite controlar se o operator analisa o vídeo inteiro ou um subconjunto explícito de scenes.

### Snapshot de config da conta
- `account_rules`

Congela as regras relevantes daquela conta para aquela execução, melhorando auditabilidade e consistência.

### Output contract
- `output`

Define onde o output final deve ser escrito e que schema é esperado.

### Runtime paths
- `runtime`

Separa output final de checkpoint, status e log de execução.

### Execution policy
- `execution_policy`

Define timeout, política de falha e tolerância (ou não) a output parcial.

### Campo customizável
- `operator_payload`

Aqui entra o contrato específico do operator individual.

---

## Definição v1 dos 4 operators

O objectivo desta secção é fixar uma definição v1 suficientemente clara para implementação inicial e testes do S3.

---

### 1. `human_subject_extractor`

#### Missão
Extrair e estruturar todas as **entidades humanas visualmente relevantes** ao longo das scenes, com foco em identidade, recorrência e especificidade.

#### Cobre
- characters
- named persons
- unnamed but visually important human figures
- groups
- factions
- crowds
- papéis humanos recorrentes
- aliases/títulos quando relevantes

#### Não cobre
- objectos
- lugares
- artefactos físicos não humanos
- símbolos abstractos
- eventos enquanto eventos
- fenómenos naturais

#### Pergunta central
> Quem são os sujeitos humanos que o universo visual deste vídeo precisa representar com clareza?

#### `operator_payload` v1
```json
{
  "target_families": [
    "characters",
    "human_figures",
    "groups",
    "factions",
    "crowds"
  ],
  "identity_resolution": "high",
  "include_aliases": true,
  "group_detection": true,
  "specificity_bias": "account_driven"
}
```

#### Output v1
JSON contendo:
- lista de entidades humanas extraídas
- tipo da entidade (`person`, `group`, `faction`, `crowd`, etc.)
- scenes em que aparece/é relevante
- nome principal ou rótulo canónico
- aliases / títulos
- nível de especificidade/confiança
- nota curta de relevância visual

#### Critério mínimo de sucesso
- output existe
- entidades humanas estão estruturadas
- recorrência/scenes estão mapeadas
- schema mínimo válido

---

### 2. `environment_location_extractor`

#### Missão
Extrair e estruturar os **lugares, ambientes e contextos espaciais** necessários para representar o vídeo visualmente com coerência.

#### Cobre
- locations
- places
- settings
- environments
- arquitectura espacial
- interiores/exteriores
- lugares específicos
- contextos geográficos/históricos relevantes

#### Não cobre
- personagens
- objectos isolados
- artefactos
- símbolos abstractos
- eventos como unidades narrativas
- fenómenos naturais enquanto entidade principal

#### Pergunta central
> Em que espaços físicos ou contextos ambientais este vídeo precisa existir visualmente?

#### `operator_payload` v1
```json
{
  "target_families": [
    "locations",
    "places",
    "environments",
    "settings"
  ],
  "specific_location_bias": "account_driven",
  "include_architectural_context": true,
  "merge_nearby_variants": true,
  "specificity_bias": "account_driven"
}
```

#### Output v1
JSON contendo:
- lista de localizações/ambientes
- tipo (`specific_place`, `general_setting`, `interior`, `exterior`, etc.)
- scenes associadas
- nome canónico
- nível de especificidade
- contexto geográfico/histórico quando aplicável
- nota curta de relevância visual

#### Critério mínimo de sucesso
- output existe
- lugares/ambientes relevantes estão mapeados
- scenes associadas presentes
- schema mínimo válido

---

### 3. `object_artifact_extractor`

#### Missão
Extrair e estruturar os **elementos físicos não humanos** que são importantes para a representação visual do vídeo.

#### Cobre
- objects
- props
- artifacts
- cultural items
- historical artifacts
- vehicles
- machines
- weapons
- animals / creatures
- documents
- maps
- letters
- interfaces

#### Não cobre
- sujeitos humanos
- lugares como contexto espacial principal
- símbolos abstractos
- eventos narrativos
- atmosferas/conceitos visuais não físicos

#### Pergunta central
> Que coisas físicas o universo visual deste vídeo precisa mostrar com precisão ou recorrência?

#### `operator_payload` v1
```json
{
  "target_families": [
    "objects",
    "props",
    "artifacts",
    "vehicles",
    "machines",
    "animals",
    "documents",
    "maps",
    "interfaces"
  ],
  "historical_specificity_bias": "account_driven",
  "include_functional_objects": true,
  "merge_duplicate_mentions": true,
  "specificity_bias": "account_driven"
}
```

#### Output v1
JSON contendo:
- lista de entidades físicas não humanas
- tipo (`weapon`, `vehicle`, `artifact`, `document`, `animal`, etc.)
- scenes associadas
- nome/rótulo canónico
- nível de especificidade
- contexto funcional ou histórico quando relevante
- nota curta de relevância visual

#### Critério mínimo de sucesso
- output existe
- entidades físicas relevantes estão identificadas
- classificação minimamente útil presente
- schema mínimo válido

---

### 4. `symbolic_event_extractor`

#### Missão
Extrair e estruturar os **elementos não literalmente objectificáveis** que ainda assim exigem tradução visual para downstream.

#### Cobre
- symbols
- motifs
- abstract visual concepts
- natural phenomena
- weather
- disasters
- event-visual entities
- acontecimentos que pedem representação visual
- elementos atmosféricos/conceptuais com peso narrativo

#### Não cobre
- pessoas como sujeitos principais
- lugares enquanto espaço físico principal
- objectos físicos estáveis
- artefactos concretos
- entidades já bem cobertas pelos outros 3 operators

#### Pergunta central
> Que elementos simbólicos, atmosféricos ou eventivos precisam de tradução visual para o vídeo funcionar?

#### `operator_payload` v1
```json
{
  "target_families": [
    "symbols",
    "motifs",
    "abstract_visual_concepts",
    "natural_phenomena",
    "weather",
    "disasters",
    "event_visual_entities"
  ],
  "allow_non_literal_translation": true,
  "event_detection": true,
  "atmospheric_relevance_bias": "account_driven",
  "specificity_bias": "account_driven"
}
```

#### Output v1
JSON contendo:
- lista de entidades simbólicas/eventivas/atmosféricas
- tipo (`symbol`, `motif`, `event`, `phenomenon`, `disaster`, etc.)
- scenes associadas
- descrição canónica
- grau de literalidade vs abstração
- nota curta sobre como a entidade existe visualmente
- relevância visual

#### Critério mínimo de sucesso
- output existe
- entidades não físicas mas visualmente necessárias estão capturadas
- scenes e classificação presentes
- schema mínimo válido

---

## Leitura sistémica da decomposição

Esta divisão procura cobrir o universo do S3 em 4 eixos relativamente limpos:

1. humanos
2. espaços
3. coisas físicas
4. coisas simbólicas / eventivas / atmosféricas

Isto facilita:

- dispatch selectivo
- account-aware behaviour
- observabilidade
- retries mais simples
- compile posterior pelo supervisor/substrate

---

## O que continua fora dos operators

Mesmo com estes 4 operators fechados em v1, continuam fora da sua responsabilidade:

- dedupe global entre outputs
- merge entre overlaps
- resolução de colisões
- priorização final do sector
- compilação do `compiled_entities.json`
- handoff para o S4

Ou seja:

- os operators **identificam e estruturam**
- o supervisor/substrate **consolida**

---

## O que falta fechar a seguir

Depois desta v1, ainda falta fechar:

- output schema formal de cada operator
- monitorização pós-dispatch pelo supervisor
- retries selectivos
- compile/merge final do S3
- contract de handoff para o S4

---

## Estado desta definição

**Status:** v2 da operator layer do S3

Esta definição fecha:

- a separação operators vs compile/merge logic
- a preservação de uma taxonomy rica
- o mapa actual de 4 operators principais
- o papel do config por conta
- o common dispatch contract v1 do supervisor -> operator
- a definição v1 operacional dos 4 operators

Próximo passo natural: fechar a camada pós-dispatch do supervisor e/ou formalizar o output schema base dos operators para implementação inicial.
