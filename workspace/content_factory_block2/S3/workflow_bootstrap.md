# S3 — Workflow Bootstrap Before Supervisor Activation

## Objectivo

Este documento detalha o que o workflow paperclip-facing do S3 deverá fazer **antes** de activar o supervisor `sm_s3_visual_planning`.

Este workflow é, por enquanto, referido conceptualmente como:

- `w3_visual_planning.py`

O nome final ainda não está fechado.

---

## Papel do workflow

O workflow não é o cérebro semântico do sector.

O seu papel é actuar como:

- launcher
- bootstrapper
- adapter
- boundary layer entre Paperclip e OpenClaw

Ele prepara o terreno para o arranque canónico do S3.

---

## O que o workflow não deve fazer

O workflow não deve:

- identificar entidades visuais
- substituir o supervisor semântico
- simular operadores internos do S3
- compilar directamente os outputs semânticos do sector
- concentrar a inteligência do S3 dentro do próprio `.py`

---

## O que o workflow deve fazer

Antes de activar o supervisor, o workflow deve:

1. receber o payload do Paperclip
2. validar precondições upstream
3. criar a estrutura mínima do sector
4. montar o `s3_source_package.json`
5. escrever checkpoint de bootstrap
6. activar o supervisor com uma mensagem canónica de arranque
7. observar sucesso/falha do arranque

---

## Payload mínimo esperado do Paperclip

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

### Campos mínimos esperados

- `job_id`
- `video_name`
- `account_id`
- `language`
- `run_root`
- `inputs.screenplay_analysis_path`
- `inputs.script_fetched_checkpoint_path`

---

## Fase 1 — validar precondições

O workflow deve verificar, antes de qualquer invocação OpenClaw:

- `screenplay_analysis.json` existe
- `01_script_fetched.json` existe
- ambos os ficheiros abrem como JSON válido
- `total_scenes > 0`
- existe contexto mínimo do vídeo
- `run_root` existe
- o job está num estado suficiente para iniciar o S3

### Se falhar

Se qualquer uma destas condições falhar:

- o supervisor **não** é activado
- o workflow devolve falha limpa ao Paperclip
- o erro é classificado como falha de boundary/upstream, não do runtime interno do S3

---

## Fase 2 — criar estrutura mínima do sector

Depois das precondições, o workflow deve criar a estrutura-base do S3 dentro do `run_root`.

Exemplo:

```text
{run_root}/b2_s3_visual_planning/
  inputs/
  identifiers/
  compiled/
  checkpoints/
  logs/
```

### Papel desta estrutura

- tornar o arranque previsível
- separar artefactos do sector dos artefactos globais do vídeo
- permitir recovery e observabilidade
- evitar que o supervisor tenha de improvisar paths e pastas no momento do arranque

---

## Fase 3 — montar `s3_source_package.json`

O workflow deve ler os artefactos upstream e gerar o pacote-base do sector em:

```text
{run_root}/b2_s3_visual_planning/inputs/s3_source_package.json
```

Este ficheiro segue o contrato definido em `inputs.md`.

### Fonte esperada dos dados

- `screenplay_analysis.json`
- `01_script_fetched.json`

### Objectivo deste artefacto

Transformar o legado bruto do CFV3 num input-base canónico do S3.

Assim, o supervisor não precisa arrancar dependente directamente do shape original dos artefactos do V3.

---

## Fase 4 — escrever checkpoint de bootstrap

Antes de chamar o supervisor, o workflow deve escrever um checkpoint de bootstrap.

Exemplos conceptuais:

- `s3_bootstrap_ready.json`
- `s3_step0_workflow_bootstrap.json`

### Conteúdo mínimo esperado

- payload recebido do Paperclip
- artefactos upstream validados
- paths gerados pelo bootstrap
- timestamp de conclusão da fase

---

## Fase 5 — activar o supervisor

O workflow deve então activar o `sm_s3_visual_planning` com uma mensagem estruturada de arranque.

O supervisor não deve ser chamado com um prompt improvisado nem com artefactos brutos do V3 como interface primária.

### Bootstrap message contract (conceitual)

```json
{
  "kind": "s3_start",
  "job_id": "job_006_pt_guinle_001",
  "run_root": "...",
  "sector_root": ".../b2_s3_visual_planning",
  "source_package_path": ".../b2_s3_visual_planning/inputs/s3_source_package.json",
  "checkpoints_dir": ".../b2_s3_visual_planning/checkpoints",
  "identifiers_dir": ".../b2_s3_visual_planning/identifiers",
  "compiled_dir": ".../b2_s3_visual_planning/compiled",
  "logs_dir": ".../b2_s3_visual_planning/logs"
}
```

### Princípio

O workflow passa ao supervisor:

- contexto suficiente para arrancar
- paths canónicos do sector
- o artefacto-base do S3 já preparado

---

## O que ainda não está definido aqui

Este documento pára no momento da activação do supervisor.

Ainda não cobre:

- o comportamento interno do `sm_s3_visual_planning`
- activação de identificadores
- retries internos
- compilação semântica
- outputs finais do sector

Esses pontos pertencem à fase seguinte do desenho do S3.

---

## Regra resumida

### Formulação simples

**Paperclip invoca o workflow do S3.**
**O workflow prepara o sector.**
**O workflow activa o supervisor.**
**Só depois começa o runtime interno do S3.**

---

## Estado desta definição

**Status:** v1 do bootstrap workflow do S3

Este documento serve como base para futura implementação do `.py` paperclip-facing que dará arranque ao sector.
