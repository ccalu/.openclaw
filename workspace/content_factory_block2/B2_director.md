# B2 Director

## Objectivo

Este documento define o `b2_director` como peça real do runtime do Bloco 2.

O foco aqui é fechar, em nível v1:

- papel exacto do `b2_director`
- missão operacional
- limites de responsabilidade
- relação com Paperclip / boundary workflow / supervisores sectoriais
- contract de entrada e saída em nível suficiente para criação do workspace do agent
- shape macro do estado persistido do bloco

O objectivo desta definição é permitir criar o agent `b2_director` com uma base estrutural forte, sem ainda cair em detalhe implementacional excessivo.

---

## O que é o `b2_director`

O `b2_director` é o director interno do Bloco 2 dentro do runtime OpenClaw.

Ele é o agent responsável por **orquestrar a progressão do Bloco 2** através dos sectores:

- S3
- S4
- S5
- S6

O `b2_director` é, portanto, o **control plane do bloco**.

---

## O que o `b2_director` não é

É importante evitar sobreposição de papéis.

O `b2_director` não é:

- o boundary com o Paperclip
- um supervisor sectorial
- um operator
- um executor contínuo “sempre acordado”
- uma camada de semântica interna dos sectores

A sua função não é executar trabalho sectorial directamente, mas sim coordenar a progressão correcta do bloco.

---

## Missão central

A missão do `b2_director` é:

> ler o estado actual do Bloco 2, interpretar o evento mais recente, decidir o próximo passo correcto do bloco, activar o supervisor sectorial apropriado, persistir o novo estado do bloco e garantir que o B2 progride correctamente até completion ou failure.

---

## Pergunta operacional central

A pergunta que o `b2_director` resolve é:

> Dado o estado actual do Bloco 2, qual é o próximo passo correcto do bloco?

Esta é a sua pergunta de controlo.

---

## Responsabilidades do `b2_director`

O `b2_director` deve ser responsável por:

- ler bootstrap e estado persistido do bloco
- interpretar checkpoints sectoriais
- decidir qual sector deve correr agora
- activar o supervisor do sector apropriado
- actualizar `b2_state.json`
- escrever checkpoints do bloco
- decidir retry / progressão / falha de bloco em nível macro
- decidir quando o bloco pode ser considerado concluído
- persistir o fecho do bloco

---

## Limites de responsabilidade

O `b2_director` não deve:

- executar semântica interna de S3/S4/S5/S6
- chamar operators sectoriais directamente
- monitorizar operators directamente
- compilar outputs sectoriais internamente
- substituir o supervisor do sector
- substituir o boundary workflow com o Paperclip
- depender de conversa longa acumulada entre turns

---

## Relação com os outros actores

### Paperclip

O Paperclip não conversa directamente com o interior do B2.

Fala apenas com a boundary do bloco.

---

### `w3_block2.py`

É a peça que activa e reactiva o `b2_director`.

O workflow observa checkpoints macro do bloco e chama o director quando surge um evento relevante.

---

### Supervisores sectoriais

Os supervisores sectoriais são subordinados operacionais do `b2_director`.

O director decide quando cada supervisor entra.

Exemplos esperados:

- `sm_s3_visual_planning`
- `sm_s4_asset_research`
- `sm_s5_scene_kit_design`
- `sm_s6_visual_spec_assembly`

---

### Perseus

No lado Paperclip, o agent responsável por activar e monitorar o Bloco 2 foi nomeado como **Perseus**.

A separação conceptual recomendada é:

- **Perseus** -> actor Paperclip-facing
- **`b2_director`** -> actor OpenClaw-facing interno do B2

Isto mantém as camadas claras e reduz ambiguidade entre runtime externo e runtime interno.

---

## Modelo de funcionamento

O `b2_director` funciona por **reentradas discretas orientadas a eventos/checkpoints**.

Ele não deve ser modelado como agent em conversa contínua e acumulativa.

### Em cada activação, o director deve:

1. ler `b2_state.json`
2. ler o artefacto que motivou a activação actual
3. interpretar o estado do bloco
4. decidir o próximo passo
5. escrever o novo estado do bloco
6. activar o supervisor seguinte, ou fechar o bloco
7. terminar

---

## Inputs do `b2_director`

Os inputs do director dividem-se em 3 camadas.

---

### 1. Bootstrap input

No arranque do bloco, o director deve receber informação suficiente para assumir controlo inicial do B2.

Exemplo conceptual:

```json
{
  "kind": "b2_start",
  "job_id": "job_006_pt_001",
  "run_root": "C:/...",
  "b2_root": "C:/.../b2",
  "account_id": "006",
  "language": "pt-BR",
  "inputs": {
    "screenplay_analysis_path": "...",
    "audio_timestamps_path": "...",
    "other_upstream_artifacts": "..."
  }
}
```

---

### 2. Resume input

Nas reentradas, o director deve ser activado com um input curto, centrado no evento que motivou o novo turno.

Exemplo conceptual:

```json
{
  "kind": "b2_resume",
  "run_root": "...",
  "b2_root": ".../b2",
  "reason": "s3_completed",
  "trigger_artifact": ".../checkpoints/s3_completed.json"
}
```

---

### 3. Estado persistido do bloco

A principal fonte de verdade do director não é a conversa, mas sim o estado persistido e os artefactos do bloco.

Exemplos:

- `b2_state.json`
- checkpoints do bloco
- checkpoints sectoriais
- outputs canónicos dos sectores

---

## Outputs do `b2_director`

O director não produz sozinho o artefacto final do B2, mas produz os artefactos de controlo que tornam o bloco executável e recuperável.

### Outputs principais

- `b2_state.json` actualizado
- checkpoints de progressão do bloco
- activação do supervisor sectorial apropriado
- `b2_completed.json` ou `b2_failed.json`

### Outputs auxiliares possíveis

- report de decisão do bloco
- log do director
- rationale curta da transição de estado

---

## Estados do bloco que o director precisa entender

O conjunto de estados deve ser pequeno, claro e orientado à progressão do bloco.

### Estados macro recomendados v1

- `bootstrapped`
- `running_s3`
- `running_s4`
- `running_s5`
- `running_s6`
- `completed`
- `failed`

Mais tarde pode surgir um estado como `degraded_completed`, se for necessário.

---

## Eventos que o director precisa interpretar

O director deve interpretar pelo menos estes eventos:

- `bootstrap_ready`
- `s3_completed`
- `s3_failed`
- `s4_completed`
- `s4_failed`
- `s5_completed`
- `s5_failed`
- `s6_completed`
- `s6_failed`

---

## Decisões típicas do director

### Caso 1 — bootstrap pronto

Evento:
- `bootstrap_ready`

Decisão:
- activar S3

---

### Caso 2 — S3 concluído

Evento:
- `s3_completed`

Decisão:
- ler `s3_completed.json` como source of truth do handoff sectorial
- validar `compiled_entities_path` e `sector_report_path` declarados nesse checkpoint
- actualizar estado do bloco
- activar S4 (fora do modo `s3_only`) ou fechar o bloco (em `s3_only`)

---

### Caso 3 — S4 falhou

Evento:
- `s4_failed`

Decisão:
- avaliar se faz sentido retry sectorial
- ou marcar falha de bloco

---

### Caso 4 — S5 concluído

Evento:
- `s5_completed`

Decisão:
- ler `s5_completed.json` como source of truth do handoff sectorial
- validar `video_direction_frame_path`, `scene_kit_specs_dir`, `scene_kit_pack_path` e `sector_report_path` declarados nesse checkpoint
- confirmar `ready_for_s6 == true`
- confirmar completude macro declarada (`scene_kit_specs_generated == scene_count_total` e `scene_kit_specs_valid == scene_count_total`)
- actualizar estado do bloco
- activar S6

---

### Caso 5 — S6 concluído

Evento:
- `s6_completed`

Decisão:
- validar output final do B2
- escrever `b2_completed.json`
- fechar o bloco

---

## Shape macro recomendado do `b2_state.json`

Deve existir um estado persistido central do bloco em:

```text
{run_root}/b2/state/b2_state.json
```

### Shape conceptual v1

```json
{
  "block": "b2",
  "status": "running",
  "current_stage": "s3",
  "completed_stages": [],
  "failed_stages": [],
  "next_stage": "s4",
  "last_event": "s3_requested",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

### Exemplo após progressão

```json
{
  "block": "b2",
  "status": "running",
  "current_stage": "s4",
  "completed_stages": ["s3"],
  "failed_stages": [],
  "next_stage": "s5",
  "last_event": "s3_completed",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

Este estado é a peça central para:

- recovery
- reentrada limpa
- rastreabilidade do bloco
- decisão de progressão do director

---

## Workspace local recomendado do `b2_director`

O workspace do agent deve viver em:

```text
.openclaw/agents/b2_director/
```

### Estrutura inicial recomendada

```text
.openclaw/agents/b2_director/
  IDENTITY.md
  MISSION.md
  CONTEXT.md
  CONTRACT.md
  OPERATIONS.md
```

### Papel dos ficheiros

#### `IDENTITY.md`
Quem é o director, posição hierárquica e papel no B2.

#### `MISSION.md`
Missão operacional do director.

#### `CONTEXT.md`
Contexto do Bloco 2, relação com sectores e boundary workflow.

#### `CONTRACT.md`
Bootstrap contract, resume contract, artefactos lidos e artefactos escritos.

#### `OPERATIONS.md`
Regras práticas de interpretação de estados/eventos, activação de sectores, progressão, falha e completion.

---

## Fronteira entre doc central e workspace do agent

### Docs centrais do bloco devem responder a:

- arquitectura do B2
- runtime control flow do bloco
- relação com Paperclip / Perseus
- topologia dos sectores do bloco
- contratos estruturais do bloco

### Workspace local do `b2_director` deve responder a:

- quem é o director
- o que recebe
- o que decide
- o que escreve
- o que nunca deve fazer

### Regra prática

A verdade sistémica do bloco deve permanecer em:

```text
.openclaw/workspace/content_factory_block2/
```

O workspace do agent deve conter apenas a camada operacional local do director.

---

## Naming recomendado

A separação de naming recomendada é:

- **Perseus** -> actor do lado Paperclip
- **`b2_director`** -> actor do lado OpenClaw

Esta distinção ajuda a manter as camadas claras em documentação, implementação e debugging.

---

## Resumo executivo

O `b2_director` é:

- o director interno do Bloco 2 no OpenClaw
- o control plane do bloco
- orientado a estado persistido e checkpoints
- activado por reentradas discretas

Ele deve:

- ler o estado do bloco
- decidir o próximo sector
- activar o supervisor apropriado através da boundary/checkpoint model acordada
- actualizar estado e checkpoints
- validar paths declarados pelos checkpoints sectoriais
- fechar o bloco quando apropriado

Ele não deve:

- fazer o trabalho interno dos sectores
- chamar operators directamente
- substituir o boundary workflow
- depender de contexto conversacional acumulado entre turns

---

## Estado desta definição

**Status:** v1 do `b2_director`

Esta definição fecha:

- o papel exacto do `b2_director`
- a missão e os limites de responsabilidade
- a relação com Paperclip, `w3_block2.py`, supervisores sectoriais e Perseus
- os contracts de entrada/saída em nível suficiente para criar o workspace do agent
- a shape macro do estado persistido do bloco

Próximos passos naturais:

1. planear os ficheiros do workspace local do `b2_director`
2. criar o agent `b2_director`
3. depois discutir a peça do Paperclip (`Perseus`) responsável por activar e monitorar o B2
