# B2 — Runtime Control Flow

## Objectivo

Este documento descreve o modelo de runtime e controlo do Bloco 2 dentro da arquitectura Paperclip + OpenClaw.

O foco é tornar tangível e operacional a seguinte pergunta:

> como o Bloco 2 funciona na prática sem depender de um agent “mágico” em conversa contínua?

Este documento fecha especialmente:

- quem activa quem
- quem espera o quê
- quem observa o quê
- que artefactos disparam reentrada
- como o Paperclip conversa com o B2 sem precisar entender o interior sectorial

---

## Decisão arquitectural central

O Bloco 2 deve ser tratado como **uma unidade paperclip-facing única**, enquanto a orquestração interna de S3 -> S4 -> S5 -> S6 fica a cargo do OpenClaw.

### Formulação da decisão

- **Paperclip orquestra o Bloco 2 como unidade**
- **OpenClaw orquestra internamente os sectores do Bloco 2**
- a observabilidade interna do bloco é preservada por **artefactos, checkpoints e estado persistido**, e não por micro-orquestração sector a sector dentro do Paperclip

---

## Princípio de runtime

O Bloco 2 não deve ser pensado como uma conversa contínua entre agents.

O modelo correcto é o de uma **state machine orientada a artefactos e reentradas discretas**.

### Isto significa

- o estado real do bloco vive em ficheiros persistidos
- os agents fazem turnos discretos de controlo
- cada turno:
  - lê o estado actual
  - decide o próximo passo
  - escreve novo estado
  - despacha o actor seguinte
  - termina

### Isto evita

- depender de memória conversacional longa
- agents “em standby mental” entre etapas
- carry-over de contexto desnecessário
- dificuldade de recovery após falha/interrupção

---

## Actores do fluxo

### 1. Paperclip

O Paperclip vê o Bloco 2 como uma unidade única.

Responsabilidades:

- iniciar o entrypoint do B2
- esperar o resultado final do bloco
- consumir o output final do bloco
- não gerir a sequência interna S3 -> S4 -> S5 -> S6

O Paperclip não deve conhecer a topologia interna fina do B2.

---

### 2. `w3_block2.py` — boundary workflow / adapter

Esta peça é a ponte entre Paperclip e o interior OpenClaw do Bloco 2.

Responsabilidades:

- bootstrap inicial do bloco
- criação da estrutura mínima de runtime do B2
- activação inicial do `b2_director`
- reactivação do `b2_director` quando ocorrer evento relevante
- observação dos artefactos macro do bloco
- devolução do estado final do B2 ao Paperclip

### Importante

O `w3_block2.py` não deve tomar decisões semânticas internas do B2.

Ele actua como:

- launcher
- boundary adapter
- watcher do bloco
- bridge com o Paperclip

---

### 3. `b2_director` — OpenClaw

O `b2_director` é o cérebro de controlo interno do Bloco 2.

Responsabilidades:

- ler o estado actual do bloco
- interpretar o evento que disparou a activação actual
- decidir qual sector deve correr agora
- activar o supervisor sectorial apropriado
- actualizar o estado persistido do bloco
- decidir quando o bloco terminou ou falhou

### Importante

O `b2_director` não precisa ficar vivo continuamente.

Ele funciona por **reactivações discretas orientadas a eventos/checkpoints**.

---

### 4. Supervisores sectoriais

Exemplos:

- `sm_s3_visual_planning`
- `sm_s4_asset_research`
- `sm_s5_scene_kit_design`
- `sm_s6_visual_spec_assembly`

Responsabilidades:

- gerir o sector internamente
- chamar operators
- monitorizar e validar outputs internos do sector
- produzir output canónico do sector
- escrever checkpoint sectorial de sucesso/falha

---

### 5. Operators sectoriais

São os executores especializados de cada sector.

No caso do S3, por exemplo, os operators tratam das famílias semânticas específicas do Visual Planning.

---

## Fluxo macro de activação

```text
Paperclip
  -> w3_block2.py
    -> b2_director
      -> supervisor sectorial (S3 / S4 / S5 / S6)
        -> operators do sector
```

Este fluxo não ocorre dentro de um único turno contínuo.

A progressão do bloco acontece por reentradas discretas do `b2_director`.

---

## Quem activa quem

### Activação inicial

1. **Paperclip activa `w3_block2.py`**
2. `w3_block2.py` prepara o bootstrap do bloco
3. `w3_block2.py` activa o `b2_director`
4. `b2_director` decide o primeiro sector a correr
5. `b2_director` activa o supervisor desse sector

### Reactivações posteriores

6. o supervisor sectorial termina o seu trabalho e escreve checkpoint de sector concluído/falhado
7. `w3_block2.py` detecta esse evento relevante
8. `w3_block2.py` reactiva o `b2_director`
9. `b2_director` decide o próximo passo do bloco

E assim sucessivamente até ao fecho do B2.

---

## Quem espera o quê

### Paperclip espera

- apenas o **resultado final do Bloco 2**
- não espera individualmente S3, S4, S5 ou S6
- não precisa saber a ordem ou a lógica interna exacta dos sectores

---

### `w3_block2.py` espera

- eventos/checkpoints macro do bloco
- especialmente sinais de conclusão ou falha sectorial
- o momento em que deve reactivar o `b2_director`
- o momento em que o bloco completou ou falhou

O `w3_block2.py` não espera outputs internos de operator nem semântica fina dos sectores.

---

### `b2_director` espera

Idealmente, o `b2_director` **não espera em modo vivo/contínuo**.

O director é activado, toma uma decisão, persiste estado e termina.

A “espera” do director existe sob a forma de:

- `b2_state.json`
- checkpoints do bloco
- checkpoints sectoriais
- artefactos de triggering que indicam nova condição do sistema

---

### Supervisor sectorial espera

É ao nível do supervisor sectorial que acontece a espera mais “real” do runtime interno.

Cada supervisor espera:

- outputs dos operators do seu sector
- checkpoints internos do sector
- critérios de validação do sector
- compile interno do sector

---

## Quem observa o quê

### Paperclip observa

- apenas o estado externo do `w3_block2.py`
- sucesso/falha final do B2
- artefacto final consumível do B2

---

### `w3_block2.py` observa

- `b2_state.json`
- checkpoints do bloco
- checkpoints sectoriais concluídos/falhados
- `b2_completed.json`
- `b2_failed.json`

### Exemplo conceptual de checkpoints observados

```text
{run_root}/b2/checkpoints/
  b2_bootstrap_ready.json
  s3_requested.json
  s3_completed.json
  s4_requested.json
  s4_completed.json
  s5_requested.json
  s5_completed.json
  s6_requested.json
  s6_completed.json
  b2_completed.json
```

---

### `b2_director` observa

- `b2_state.json`
- artefacto que disparou a activação actual
- checkpoint do sector anterior
- output canónico do sector anterior, quando necessário para validação/decisão

#### Exemplos

- se o director vê `s3_completed.json` + output válido do S3 -> decide activar S4
- se o director vê `s4_completed.json` + handoff macro válido do S4 -> decide activar S5
- se o director vê `s5_completed.json` + handoff macro válido do S5 -> decide activar S6
- se o director vê `s4_failed.json` -> decide retry sectorial, degradação ou falha do bloco

---

### Supervisor sectorial observa

- artefactos internos do sector
- outputs/checkpoints/status dos operators
- outputs compilados do próprio sector

No caso do S3, por exemplo, o supervisor observa:

- `dispatch/`
- `operators/<operator>/status.json`
- `operators/<operator>/checkpoint.json`
- `operators/<operator>/output.json`

---

## Artefactos que disparam reentrada do `b2_director`

Esta é a peça central do modelo.

O `b2_director` deve ser reactivado quando surge um checkpoint decisivo de sector.

### Artefactos principais de reentrada

- `s3_completed.json`
- `s3_failed.json`
- `s4_completed.json`
- `s4_failed.json`
- `s5_completed.json`
- `s5_failed.json`
- `s6_completed.json`
- `s6_failed.json`

### Regra

Sempre que um sector entra num estado decisivo, isso gera condição para nova activação do `b2_director`.

---

## Papel real do `w3_block2.py`

O `w3_block2.py` funciona como **boundary watcher + adapter**.

### Responsabilidade prática

1. inicia o bloco
2. detecta eventos relevantes do bloco
3. reactiva o `b2_director`
4. devolve o resultado final ao Paperclip

### O que ele não deve fazer

- decidir a lógica interna do B2
- assumir papel de supervisor sectorial
- gerir semântica de retry interno de cada sector
- substituir o director nas decisões do bloco

---

## Como o `b2_director` funciona em cada turno

Cada activação do director deve ser curta, determinística e orientada a decisão.

### Input conceptual da activação

```json
{
  "kind": "b2_resume",
  "run_root": "...",
  "b2_root": ".../b2",
  "reason": "s3_completed",
  "trigger_artifact": ".../checkpoints/s3_completed.json"
}
```

### O que o director faz em cada activação

1. lê `b2_state.json`
2. lê o artefacto que disparou a reentrada
3. valida o estado do sector anterior
4. decide o próximo passo
5. escreve novo `b2_state.json`
6. escreve checkpoint correspondente
7. activa o supervisor seguinte, ou fecha o bloco

### O que o director não faz

- não entra em loop longo
- não monitoriza operators directamente
- não substitui o trabalho interno do supervisor sectorial
- não depende de memória conversacional longa entre turns

---

## Como o Paperclip conversa com o B2 sem entender o interior inteiro

O Paperclip deve conversar apenas com a **boundary surface** do Bloco 2.

### O que o Paperclip precisa conhecer

#### Input macro do B2
Exemplo:

- `job_id`
- `run_root`
- `account_id`
- `language`
- artefactos upstream necessários para iniciar o bloco

#### Output macro do B2
Exemplo:

- artefacto final do bloco (ex.: `video_spec.json`)
- report final do bloco
- status final do B2
- checkpoint `b2_completed.json`

#### Status macro do B2
Exemplo:

- `running`
- `completed`
- `failed`

### O que o Paperclip não precisa conhecer

- quais supervisors existem
- quais operators existem
- como S3 compila entidades
- como S4 faz retry
- como S5 lida com regeneração
- como S6 fecha o spec

Tudo isso permanece encapsulado no interior do B2.

---

## Boundary contract ideal entre Paperclip e B2

### Exemplo conceptual de input do bloco

```json
{
  "kind": "start_b2",
  "job_id": "...",
  "run_root": "...",
  "account_id": "...",
  "language": "...",
  "inputs": {
    "screenplay_analysis_path": "...",
    "audio_timestamps_path": "...",
    "other_upstream_artifacts": "..."
  }
}
```

### Exemplo conceptual de output final do bloco

```json
{
  "status": "completed",
  "block": "b2",
  "output": {
    "video_spec_path": ".../b2/final/video_spec.json",
    "b2_report_path": ".../b2/final/b2_report.md"
  }
}
```

---

## Estado persistido do B2

Deve existir um ficheiro central de estado do bloco:

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

Este ficheiro é a peça central para recovery e reentrada limpa do director.

---

## Exemplo de fluxo completo

### Início do bloco

1. Paperclip chama `w3_block2.py`
2. `w3_block2.py` cria bootstrap do bloco
3. `w3_block2.py` escreve `b2_bootstrap_ready.json`
4. `w3_block2.py` escreve `b2_state.json`
5. `w3_block2.py` activa `b2_director`

### Turno 1 do director

6. `b2_director` lê o estado do bloco
7. decide iniciar S3
8. escreve `s3_requested.json`
9. activa `sm_s3_visual_planning`
10. termina

### Fecho do S3

11. `sm_s3_visual_planning` conclui o S3
12. escreve `s3_completed.json`
13. persiste output canónico do S3

### Reentrada 1

14. `w3_block2.py` detecta `s3_completed.json`
15. reactiva `b2_director` com `reason = s3_completed`

### Turno 2 do director

16. `b2_director` valida o S3
17. decide iniciar S4
18. escreve `s4_requested.json`
19. activa supervisor do S4
20. termina

### Progressão do bloco

O mesmo padrão repete-se para S4, S5 e S6.

### Fecho do bloco

21. `b2_director` valida S6
22. escreve `b2_completed.json`
23. persiste output final do B2
24. termina
25. `w3_block2.py` detecta `b2_completed.json`
26. devolve sucesso ao Paperclip

---

## Padrão de integração sectorial S4 -> S5 -> S6

O padrão de integração do S5 deve seguir explicitamente o mesmo shape macro já validado para os sectores anteriores:

1. o sector anterior conclui e escreve checkpoint macro (`s4_completed.json`)
2. a boundary reactiva `b2_director`
3. o director valida o handoff macro do sector anterior
4. o director escreve `s5_requested.json`
5. a boundary detecta esse request e lança `sm_s5_scene_kit_design`
6. o supervisor do S5 corre o runtime interno do sector
7. o S5 escreve `s5_completed.json` ou `s5_failed.json`
8. a boundary reactiva `b2_director`
9. o director valida o handoff macro do S5 e decide se abre S6

No caso do S5, o handoff macro deve ser validado por paths declarados no checkpoint sectorial, e não por descoberta implícita de ficheiros na pasta do sector.

---

## Resumo operacional consolidado

### Quem activa quem

- Paperclip -> `w3_block2.py`
- `w3_block2.py` -> `b2_director`
- `b2_director` -> supervisor do sector apropriado
- supervisor do sector -> operators do sector

### Quem espera o quê

- Paperclip espera o B2 completo
- `w3_block2.py` espera eventos/checkpoints do bloco
- `b2_director` não espera “vivo”; é reactivado
- supervisor sectorial espera outputs e compile do seu sector

### Quem observa o quê

- Paperclip observa apenas o estado macro do B2
- `w3_block2.py` observa checkpoints do bloco
- `b2_director` observa `b2_state.json` + checkpoints sectoriais
- supervisor sectorial observa artefactos internos do sector

### Que artefactos disparam reentrada

- `s3_completed.json` / `s3_failed.json`
- `s4_completed.json` / `s4_failed.json`
- `s5_completed.json` / `s5_failed.json`
- `s6_completed.json` / `s6_failed.json`

### Como o Paperclip conversa com o B2

- através de uma boundary surface única
- com input macro do bloco
- com output macro do bloco
- sem conhecer a mecânica interna sectorial

---

## Estado desta definição

**Status:** validado em E2E narrow real para `S3-only`

Esta definição já não é apenas conceptual. O padrão foi provado em runtime real para:

- boundary Paperclip-side a observar checkpoints no disco
- `b2_director` em bootstrap activo
- `b2_director` em resume `s3_completed -> b2_completed`
- `sm_s3_visual_planning` a gerir o sector S3
- operator layer real do S3
- `s3_completed.json` como gatilho de reentrada
- `b2_completed.json` como fecho do bloco em `mode = s3_only`

Esta definição fecha:

- o modelo de runtime do B2 como state machine orientada a artefactos
- o papel do `w3_block2.py` como boundary watcher/adapter
- o papel do `b2_director` como cérebro de controlo interno do bloco
- o mecanismo de reentrada por checkpoints sectoriais
- a relação entre Paperclip e o B2 sem exposição da topologia interna

Próximos passos naturais:

1. consolidar a documentação replicável para S4/S5/S6
2. endurecer fresh-session hygiene e cleanup policy para runs sucessivos
3. usar este padrão como baseline de abertura dos próximos sectores
