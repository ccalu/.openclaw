# S3 — Runtime Layout / Agent Topology

## Objectivo

Este documento define como o S3 (Visual Planning) existe de forma concreta dentro do runtime OpenClaw.

O foco aqui é fechar:

- nomes exactos dos agents
- topologia do sector
- directórios permanentes dos agents
- fronteira entre workspace principal e workspaces locais dos agents
- localização dos contracts e schemas
- layout dos artefactos de execução por vídeo/job
- regras operacionais importantes do runtime

O objectivo desta definição é permitir passar da arquitectura conceptual para a criação real dos agents do S3 com risco estrutural baixo.

---

## Topologia de agents do S3

A topologia v1 do sector S3 passa a ser composta por 5 agents:

### Supervisor
- `sm_s3_visual_planning`

### Operators
- `op_s3_human_subject_extractor`
- `op_s3_environment_location_extractor`
- `op_s3_object_artifact_extractor`
- `op_s3_symbolic_event_extractor`

---

## Convenção de naming

### Prefixos
- `sm_` = supervisor / sector manager
- `op_` = operator

### Namespace do sector
Todos os agents do S3 incluem o namespace `s3` no nome para:

- evitar colisão com futuros agents de S4/S5/S6
- facilitar debugging
- facilitar registry e lookup
- tornar inequívoca a pertença ao sector

### Regra prática
Neste momento, é preferível nomes longos mas claros a nomes curtos mas ambíguos.

---

## Directórios permanentes dos agents

Os agents permanentes devem viver em:

```text
.openclaw/agents/
```

### Layout v1

```text
.openclaw/agents/
  sm_s3_visual_planning/
  op_s3_human_subject_extractor/
  op_s3_environment_location_extractor/
  op_s3_object_artifact_extractor/
  op_s3_symbolic_event_extractor/
```

Este layout assume a convenção mais simples e previsível:

- 1 agent = 1 directório
- 1 workspace local por agent

---

## Fronteira entre workspace principal e workspaces locais

Esta separação é crítica.

---

## Workspace principal do Tobias

Local:

```text
.openclaw/workspace/S3/
```

Este directório deve ser o **source of truth sistémico do sector S3**.

Aqui vivem os documentos que descrevem o S3 como sistema, não como agent individual.

### Devem viver aqui
- `inputs.md`
- `architecture.md`
- `workflow_bootstrap.md`
- `supervisor.md`
- `operators.md`
- `runtime_layout.md`
- `contracts/`
- `schemas/`
- futuros docs transversais como `post_dispatch.md`, se necessário

### Função desta camada
Documentar:

- arquitectura do sector
- topologia de agents
- contracts partilhados
- fluxos entre camadas
- decisões sistémicas
- artefactos do sector
- regras de runtime que afectam múltiplos agents

---

## Workspaces locais dos agents

Local:

```text
.openclaw/agents/<agent_name>/
```

Cada workspace local deve conter apenas o necessário para aquele agent operar com clareza.

A função do workspace local é fornecer:

- identidade local
- missão local
- contract local
- regras operacionais locais
- critérios de sucesso/falha daquele agent

### Regra importante
O workspace local **não deve** virar cópia da documentação completa do S3.

O agent precisa de contexto suficiente para operar, mas a verdade sistémica continua centralizada em `.openclaw/workspace/S3/`.

---

## Estrutura mínima recomendada por agent

### Supervisor

```text
.openclaw/agents/sm_s3_visual_planning/
  IDENTITY.md
  MISSION.md
  CONTEXT.md
  CONTRACT.md
  OPERATIONS.md
```

#### Papel dos ficheiros

- `IDENTITY.md` → quem é o supervisor e onde se posiciona na hierarquia
- `MISSION.md` → missão operacional do supervisor
- `CONTEXT.md` → contexto local de execução do S3 para o supervisor
- `CONTRACT.md` → contract de entrada/saída do supervisor
- `OPERATIONS.md` → regras práticas de dispatch, monitorização, validação, retry, compile, handoff

---

### Operators

Exemplo:

```text
.openclaw/agents/op_s3_human_subject_extractor/
  IDENTITY.md
  MISSION.md
  CONTRACT.md
  OUTPUT_SCHEMA.md
```

A mesma estrutura base aplica-se aos outros 3 operators.

#### Papel dos ficheiros

- `IDENTITY.md` → quem é o operator e qual o seu papel no S3
- `MISSION.md` → missão local, cobertura e limites
- `CONTRACT.md` → o que recebe, o que lê, o que escreve, como falha
- `OUTPUT_SCHEMA.md` → semântica e estrutura do output esperado

---

## Contracts centrais vs contracts locais

---

## Contracts centrais do sector

Os contracts partilhados do sector devem viver em:

```text
.openclaw/workspace/S3/contracts/
```

### Estrutura inicial recomendada

```text
S3/contracts/
  supervisor_bootstrap_contract.md
  operator_dispatch_contract.md
  operator_registry.md
```

### Função

Estes docs são a referência canónica para:

- contract de arranque do supervisor
- contract de dispatch supervisor -> operator
- registry de mapping entre `operator_name` e `agent_id`

Se uma interface afecta mais de um agent, o contract deve viver aqui.

---

## Contracts locais dos agents

Cada agent também terá um `CONTRACT.md` local.

Mas esse ficheiro local não deve reinventar os contracts centrais.

A função dele é:

- traduzir o contract central para a perspectiva daquele agent
- resumir o que aquele agent tem de consumir e produzir
- tornar a operação do agent auto-compreensível sem espalhar verdade sistémica

### Regra prática
- **verdade partilhada canónica** -> `S3/contracts/`
- **interpretação operacional local** -> `.openclaw/agents/<agent>/CONTRACT.md`

---

## Schemas centrais

Os schemas formais devem viver em:

```text
.openclaw/workspace/S3/schemas/
```

### Estrutura inicial recomendada

```text
S3/schemas/
  human_subject_output.schema.json
  environment_location_output.schema.json
  object_artifact_output.schema.json
  symbolic_event_output.schema.json
  compiled_entities.schema.json
```

### Regra

O schema canónico deve ficar centralizado.

O `OUTPUT_SCHEMA.md` local de cada operator pode:

- explicar os campos
- resumir o shape esperado
- apontar para o schema canónico no directório `schemas/`

---

## Operator registry

O supervisor precisa de um registry explícito e simples para resolver invocações.

Local recomendado:

```text
.openclaw/workspace/S3/contracts/operator_registry.md
```

### Conteúdo conceptual

```json
{
  "human_subject_extractor": "op_s3_human_subject_extractor",
  "environment_location_extractor": "op_s3_environment_location_extractor",
  "object_artifact_extractor": "op_s3_object_artifact_extractor",
  "symbolic_event_extractor": "op_s3_symbolic_event_extractor"
}
```

### Papel operacional

O supervisor:

1. resolve o activation plan
2. escolhe os operators activos
3. consulta o registry
4. gera o dispatch payload
5. invoca o `agent_id` correspondente
6. valida o output no `output_path`

---

## Artefactos de execução por vídeo/job

Os workspaces dos agents são infra permanente.

Os artefactos da execução de cada vídeo devem viver no `run_root` daquele job.

### Layout v1 recomendado

```text
{run_root}/b2_s3_visual_planning/
  inputs/
    s3_source_package.json
  dispatch/
    human_subject_extractor_job.json
    environment_location_extractor_job.json
    object_artifact_extractor_job.json
    symbolic_event_extractor_job.json
  operators/
    human_subject_extractor/
      output.json
      checkpoint.json
      status.json
      log.md
    environment_location_extractor/
      output.json
      checkpoint.json
      status.json
      log.md
    object_artifact_extractor/
      output.json
      checkpoint.json
      status.json
      log.md
    symbolic_event_extractor/
      output.json
      checkpoint.json
      status.json
      log.md
  compiled/
    compiled_entities.json
  checkpoints/
    s3_bootstrap_ready.json
    s3_supervisor_started.json
    operator_activation_plan.json
  logs/
```

Este layout separa claramente:

- input-base do sector
- jobs de dispatch
- outputs por operator
- artefacto compilado final
- checkpoints do sector
- logs gerais

---

## Regra crítica de isolamento de contexto

Esta é uma regra operacional central do S3 e deve ser tratada como **não-negociável**.

### Regra

**Sempre que o supervisor invocar um operator, a execução desse operator deve começar com contexto/conversa limpos.**

O mesmo princípio vale para o próprio supervisor quando for activado para um novo vídeo/job.

### O que isto significa na prática

- o supervisor não deve herdar conversa acumulada de vídeos anteriores
- cada operator não deve acumular histórico conversacional entre jobs diferentes
- cada invocação deve operar como execução fresca, orientada pelo contract actual e pelos artefactos do job corrente

### Porque isto é importante

Sem isolamento de contexto, há risco elevado de:

- degradação progressiva da qualidade dos outputs
- vazamento de contexto entre vídeos
- confusão entre entidades de jobs diferentes
- carry-over de instruções velhas
- comportamento menos determinístico e menos auditável

### Princípio operacional derivado

O sistema deve preferir **invocações fresh / clean-context por job** em vez de reusar conversas longas e acumulativas.

O job corrente deve ser definido pelo:

- dispatch payload actual
- source package actual
- output path actual
- account rules snapshot actual

E não por memória conversacional residual.

### Implicação de implementação

Na criação prática dos agents e no mecanismo de invocação do supervisor, deve ser garantido um modo de execução que preserve este isolamento entre chamadas.

Se houver mais de uma forma de invocar agents no runtime, deve-se preferir a forma que melhor garanta:

- contexto limpo por execução
- menor carry-over conversacional
- maior previsibilidade do output

---

## Fronteira entre docs centrais e docs locais

### Docs centrais do S3 respondem a:

- como o sector funciona
- qual a arquitectura do sector
- quais agents existem
- como eles se relacionam
- quais contracts são partilhados
- quais são os artefactos do job
- quais são as regras sistémicas do runtime

### Docs locais dos agents respondem a:

- quem sou eu
- qual a minha missão
- o que recebo
- o que produzo
- o que não devo fazer
- como devo comportar-me operacionalmente

### Regra anti-caos

Se uma decisão afecta:

- mais de um agent
- a topologia do sector
- a interface entre camadas
- contratos partilhados
- comportamento de runtime transversal

então essa decisão deve viver no workspace principal do S3, não apenas num workspace local de agent.

---

## Estrutura final v1 consolidada

### Workspace principal

```text
.openclaw/workspace/S3/
  inputs.md
  architecture.md
  workflow_bootstrap.md
  supervisor.md
  operators.md
  runtime_layout.md
  contracts/
    supervisor_bootstrap_contract.md
    operator_dispatch_contract.md
    operator_registry.md
  schemas/
    human_subject_output.schema.json
    environment_location_output.schema.json
    object_artifact_output.schema.json
    symbolic_event_output.schema.json
    compiled_entities.schema.json
```

### Agents

```text
.openclaw/agents/
  sm_s3_visual_planning/
    IDENTITY.md
    MISSION.md
    CONTEXT.md
    CONTRACT.md
    OPERATIONS.md

  op_s3_human_subject_extractor/
    IDENTITY.md
    MISSION.md
    CONTRACT.md
    OUTPUT_SCHEMA.md

  op_s3_environment_location_extractor/
    IDENTITY.md
    MISSION.md
    CONTRACT.md
    OUTPUT_SCHEMA.md

  op_s3_object_artifact_extractor/
    IDENTITY.md
    MISSION.md
    CONTRACT.md
    OUTPUT_SCHEMA.md

  op_s3_symbolic_event_extractor/
    IDENTITY.md
    MISSION.md
    CONTRACT.md
    OUTPUT_SCHEMA.md
```

---

## Estado desta definição

**Status:** runtime layout / agent topology v1 do S3

Esta definição fecha:

- os 5 agents do sector
- os nomes exactos
- os directórios permanentes dos agents
- a fronteira entre workspace principal e workspaces locais
- a localização dos contracts e schemas
- o layout dos artefactos de execução por job
- a regra crítica de isolamento de contexto entre invocações

Próximo passo natural: definir o fluxo pós-finalização dos operators (monitorização, validação, retry, compile e handoff) antes da criação efectiva dos directórios e ficheiros dos agents.
