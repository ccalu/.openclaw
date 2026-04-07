# S3 — Architecture

## Objectivo

Este documento descreve a arquitectura do S3 (Visual Planning) dentro do novo Bloco 2, com foco especial na relação entre:

- **Paperclip** como orquestrador global
- **mini-orquestradores / workflows paperclip-facing**
- **OpenClaw** como runtime interno da equipa do sector

O objectivo é deixar explícito que, no novo sistema, já não existe um único orquestrador Python monolítico equivalente ao do CFV3 original. Em vez disso, o pipeline passa a ser repartido em várias unidades menores, invocáveis de forma independente pelo Paperclip.

---

## Contexto arquitectural

No CFV3 original, um orquestrador Python central controlava o pipeline inteiro do vídeo:

- inicialização do job
- screenplay
- TTS
- alinhamento
- visual
- assembly/render
- checkpoints globais

Esse modelo fazia sentido num sistema único e homogéneo, onde quase tudo era executado dentro da mesma stack Python.

No novo sistema, isso deixa de ser verdade.

Agora existem:

- múltiplos providers
- equipas OpenClaw
- blocos Python isolados
- integração com Paperclip
- sectores que podem ter runtime e natureza diferentes

Por isso, o antigo modelo de **um cérebro Python global que sabe tudo** deixa de ser o desenho correcto.

---

## Nova filosofia

### Antes

Um único orquestrador Python grande empurrava todo o pipeline do início ao fim.

### Agora

O pipeline é dividido em **mini-orquestradores / workflows paperclip-facing**.

Cada workflow:

- é invocável de forma independente pelo Paperclip
- controla apenas uma fatia delimitada do pipeline
- faz bootstrap local dessa etapa
- chama a camada interna correcta de execução
- devolve ao Paperclip um estado claro de sucesso/falha

---

## Papel do Paperclip

O Paperclip passa a ser o **orquestrador global do fluxo**.

Isso significa que ele decide:

- quando um bloco/sector começa
- quando o próximo pode ser invocado
- qual o payload do job
- como monitorar progresso e estado
- como encadear W1, W2, W3, W4, etc.

O Paperclip **não deve conhecer nem controlar directamente a topologia interna do S3**.

Ele não deve:

- invocar identificadores individualmente
- saber quantos operadores existem no S3
- gerir retries internos do sector
- depender da estrutura interna dos workspaces do OpenClaw

---

## Papel dos mini-orquestradores / workflows

Os workflows paperclip-facing são a camada de fronteira entre:

- a orquestração global do Paperclip
- e o runtime interno de cada bloco/sector

No caso do S3, o workflow paperclip-facing do sector deve:

1. receber o payload do Paperclip
2. validar os artefactos upstream necessários
3. preparar a estrutura de directórios do sector
4. montar o input-base do S3
5. chamar o supervisor OpenClaw do sector
6. aguardar a conclusão do sector
7. devolver ao Paperclip o estado final desse trecho

---

## Princípio fundamental do S3

O Paperclip **não invoca os operadores do S3**.

O Paperclip também **não deve, idealmente, invocar directamente a topologia interna do sector**.

Em vez disso, a sequência arquitectural correcta é:

```text
Paperclip
  -> workflow / mini-orquestrador paperclip-facing do S3
    -> sm_s3_visual_planning
      -> operadores internos do S3
```

---

## Porque esta separação é importante

Esta separação evita misturar responsabilidades que pertencem a camadas diferentes.

### Paperclip
Responsável por:
- orquestração global
- estado global do pipeline
- encadeamento entre workflows

### Workflow paperclip-facing do S3
Responsável por:
- tradução do job do Paperclip para o contexto do sector
- bootstrap local do S3
- validação de inputs
- normalização de output do sector para o ecossistema Paperclip

### `sm_s3_visual_planning`
Responsável por:
- lógica interna do sector
- resolução do activation plan
- dispatch dos operadores
- retries internos
- compilação dos resultados
- handoff interno do sector para downstream

### Operadores do S3
Responsáveis por:
- análise semântica delimitada por família de entidades visuais
- extração/estruturação do material semântico necessário para o sector
- escrita do output canónico no disco

---

## O que o workflow do S3 representa

O workflow paperclip-facing do S3 **não é o cérebro do sector**.

Ele é uma camada fina de:

- entrada
- adaptação
- bootstrap
- boundary control

O cérebro do sector continua a ser o supervisor OpenClaw do S3.

---

## Exemplo conceptual

Ainda sem nome definitivo, o sector poderá ter um entrypoint paperclip-facing como:

- `w3_s3_visual_planning.py`
- `wf_s3_visual_planning.py`
- `run_s3_visual_planning.py`

O nome exacto ainda não está fechado.

O importante é a função dessa peça:

- receber o job do Paperclip
- preparar o S3
- chamar `sm_s3_visual_planning`
- devolver estado estruturado

---

## Relação com os outros workflows do sistema

A mesma lógica tende a aplicar-se ao resto do pipeline novo.

Exemplo conceptual:

```text
workflows/
  w1_screenplay.py
  w2_tts_audio.py
  w3_visual.py
  w4_assembly.py
```

Nem todos estes workflows estão fechados ainda.

Mas a filosofia já está clara:

- cada workflow representa uma unidade paperclip-facing
- cada workflow controla apenas um trecho do pipeline
- Paperclip encadeia workflows
- cada workflow chama internamente o runtime correcto (Python, OpenClaw, etc.)

---

## Consequência prática para o S3

O S3 deve ser desenhado assumindo que:

- ele será iniciado por um workflow externo ao sector
- esse workflow preparará o contexto mínimo de arranque
- o supervisor do S3 não precisa ser a primeira interface exposta ao Paperclip
- a topologia interna do S3 deve ficar escondida atrás dessa boundary layer

---

## Regra arquitectural resumida

### Regra

**Paperclip invoca workflows.**  
**Workflows invocam equipas.**  
**Equipas invocam operadores.**

Esta é, por agora, a formulação arquitectural correcta para o S3.

---

## Workflow bootstrap before supervisor activation

O arranque do S3 deve ser separado em duas camadas:

1. **workflow paperclip-facing (`w3_visual_planning.py`)**
2. **supervisor interno do sector (`sm_s3_visual_planning`)**

Nesta primeira camada, o foco não é ainda o que o supervisor faz internamente, mas sim tudo o que precisa acontecer **antes** da sua activação.

### Papel do `w3_visual_planning.py`

Este workflow não é o cérebro semântico do S3.

Ele actua como:

- launcher
- bootstrapper
- adapter
- boundary layer entre Paperclip e OpenClaw

### O que o workflow deve fazer

Antes de activar o supervisor, o workflow deve:

1. receber o payload do Paperclip
2. validar as precondições upstream
3. criar a estrutura mínima de directórios do sector
4. montar o `s3_source_package.json`
5. escrever um checkpoint de bootstrap
6. invocar o supervisor com um bootstrap message contract canónico

### Payload mínimo recebido do Paperclip

Exemplo conceptual:

```json
{
  "job_id": "job_006_pt_guinle_001",
  "video_name": "a_historia_tragica_do_palacio_mais_decadente_do_ri",
  "account_id": "006",
  "language": "pt",
  "run_root": "C:/.../video_dir",
  "inputs": {
    "screenplay_analysis_path": ".../screenplay_analysis.json",
    "script_fetched_checkpoint_path": ".../checkpoints/01_script_fetched.json"
  }
}
```

### Fases do workflow antes do supervisor

#### Fase 1 — validar precondições

Verificar se:

- `screenplay_analysis.json` existe
- `01_script_fetched.json` existe
- os JSONs abrem sem erro
- `total_scenes > 0`
- existe contexto mínimo do vídeo
- `run_root` existe e é utilizável

Se esta fase falhar, o supervisor não deve ser activado.

#### Fase 2 — criar estrutura do sector

Criar a estrutura mínima dentro de:

```text
{run_root}/b2_s3_visual_planning/
  inputs/
  operators/
  compiled/
  checkpoints/
  logs/
  dispatch/
```

#### Fase 3 — montar `s3_source_package.json`

O workflow lê os artefactos upstream e gera o input-base do S3 em:

```text
{run_root}/b2_s3_visual_planning/inputs/s3_source_package.json
```

Esse ficheiro segue a estrutura documentada em `inputs.md`.

#### Fase 4 — escrever checkpoint de bootstrap

Antes de chamar o supervisor, o workflow escreve um checkpoint de arranque, por exemplo:

- `s3_bootstrap_ready.json`
- ou `s3_step0_workflow_bootstrap.json`

Este checkpoint regista:

- payload recebido
- artefactos validados
- paths gerados
- timestamp do bootstrap

### Bootstrap message contract do supervisor

Depois do bootstrap, o workflow deve activar o `sm_s3_visual_planning` com uma mensagem estruturada, não com um prompt improvisado.

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

### Fronteira desta definição

Tudo o que está acima pertence à **boundary layer do S3**.

Ainda não está definido aqui:

- o detalhe do comportamento individual de cada operator
- como o supervisor monitoriza os operators em execução
- como valida outputs
- como compila o resultado final do sector

Esses temas devem ser tratados separadamente.

---

## Operator architecture inside S3

O S3 passa a assumir explicitamente uma separação entre duas camadas internas:

### Camada A — extraction / normalization operators

Esta camada contém os operators que fazem **análise semântica delimitada** sobre o `s3_source_package.json` e produzem artefactos canónicos no disco.

A responsabilidade destes operators é:

- extrair entidades visualmente relevantes
- estruturar essas entidades segundo a sua família semântica
- respeitar o `entity_focus` e as regras da conta
- escrever output utilizável por downstream

Estes operators **não devem** ser responsáveis por:

- compilar o resultado final do sector
- fundir outputs entre famílias
- fazer dedupe global inter-operator
- decidir handoff para o S4

### Camada B — compile / merge logic

Esta camada pertence preferencialmente ao **supervisor + substrate**, não aos operators.

A sua responsabilidade é:

- agregação dos outputs dos operators
- dedupe global
- validação cruzada
- compilação do artefacto final do S3
- preparação do handoff para o sector seguinte

Esta separação existe para evitar que os operators acumulem responsabilidades de pipeline e para manter a lógica mecânica centralizada numa camada mais controlável.

---

## Taxonomy rica, operator layer estável

O S3 deve preservar uma **taxonomy rica de entidades visuais**. O sistema não deve ser empobrecido só para reduzir o número de operators.

Famílias semânticas relevantes incluem, entre outras:

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

No entanto, esta riqueza semântica **não implica** criar um operator diferente para cada microcategoria.

A decisão estrutural actual é preservar uma taxonomy ampla, mas operá-la através de um conjunto menor de operators com fronteiras cognitivas estáveis.

---

## Mapa actual dos operators do S3

A operator layer actual do S3 passa a ser composta por 4 operators principais:

1. `human_subject_extractor`
2. `environment_location_extractor`
3. `object_artifact_extractor`
4. `symbolic_event_extractor`

### 1. `human_subject_extractor`
Cobre principalmente:
- characters
- human figures
- groups
- factions
- crowds

### 2. `environment_location_extractor`
Cobre principalmente:
- locations
- places
- environments
- settings
- arquitectura espacial
- contextos físicos de cena

### 3. `object_artifact_extractor`
Cobre principalmente:
- objects
- props
- vehicles
- machines
- animals / creatures
- documents
- maps
- letters
- interfaces
- historical artifacts
- cultural items

### 4. `symbolic_event_extractor`
Cobre principalmente:
- symbols
- motifs
- abstract visual concepts
- natural phenomena
- disasters
- event-visual entities
- elementos que pedem tradução visual não estritamente literal

Este mapa ainda será refinado operator por operator, mas a decomposição macro está fechada nesta forma.

---

## Papel do config por conta

O config por conta passa a ter um papel importante dentro do S3.

A ideia não é usar o config da conta para decidir se um operator “existe” ou não, mas sim para modular:

- `entity_focus`
- famílias prioritárias
- nível de precisão exigido
- sensibilidade à especificidade histórica/geográfica
- thresholds de salience
- coverage expectations
- viés de extracção compatível com o nicho/canal

Exemplos conceptuais:

- uma conta pode exigir máxima precisão em figuras históricas, palácios, edifícios específicos e localizações exactas
- outra conta pode priorizar armamentos, tanques, navios, mapas e facções
- outra pode depender mais de artefactos antigos, simbologia, reconstrução plausível e contextos menos literais

Isto significa que o comportamento do S3 deve ser **account-aware**, mas sem tornar a topologia de operators dependente de cada conta.

---

## Dispatch contract como infra do sector

A relação entre supervisor e operators não deve depender de prompts ad hoc.

O S3 passa a assumir um modelo em que cada operator é invocado com:

1. um **common dispatch envelope**
2. um **operator-specific payload**

O common dispatch envelope carrega, entre outras coisas:

- identidade da execução
- contexto do vídeo/conta
- `entity_focus`
- `source_package_path`
- scope de análise
- snapshot das regras da conta
- `output_path`
- paths de checkpoint/status/log
- execution policy

O operator-specific payload carrega o detalhe particular do contract de cada operator.

O detalhe completo desta camada fica centralizado em `operators.md`.

---

## Estado desta definição

**Status:** base arquitectural do S3 actualizada após fecho inicial da operator layer

Esta definição fecha estruturalmente:

- a separação Paperclip -> workflow -> supervisor -> operators
- a separação entre analysis operators e compile/merge logic
- a existência de 4 operators principais no S3
- o papel do config por conta como modulador do `entity_focus`
- a necessidade de um dispatch contract estável entre supervisor e operators

Ainda falta fechar:

- contract exacto de cada operator
- output schema de cada operator
- monitorização pós-dispatch
- retries selectivos
- compilação final do sector
- handoff para S4
