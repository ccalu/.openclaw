# S3 — Post-Dispatch Flow

## Objectivo

Este documento descreve o que acontece no S3 depois que o supervisor despacha os operators.

O foco é fechar a fase pós-dispatch do sector, incluindo:

- monitorização da execução dos operators
- validação dos outputs
- retry selectivo
- compilação do artefacto final do sector
- geração do relatório final do S3
- fecho do sector e preparação de handoff para downstream

Este documento complementa `supervisor.md`, mas mantém esta fase separada para evitar sobrecarga excessiva no documento do supervisor.

---

## Princípio geral

O S3 **não termina** quando os operators respondem ou quando parecem ter acabado.

O S3 só deve ser considerado concluído quando:

1. os outputs dos operators foram observados e validados
2. os retries necessários foram resolvidos
3. o artefacto compilado final foi produzido
4. o relatório final do sector foi produzido
5. o estado final do sector foi persistido
6. o sector ficou pronto para consumo downstream

---

## Responsabilidade do supervisor nesta fase

O supervisor continua a ser o dono do control plane do sector.

No entanto, esta fase concentra bastante responsabilidade. Por isso, é importante distinguir:

### O que permanece no supervisor

O supervisor deve continuar responsável por:

- decidir se um operator realmente concluiu com sucesso
- decidir se falha pede retry selectivo
- decidir se o sector pode fechar com degradação controlada ou não
- decidir se o compile final está suficientemente bom para downstream
- assumir e persistir o estado final do sector

### O que deve ser apoiado por substrate / helpers / skills mecânicas

Certos trabalhos não devem depender apenas de julgamento conversacional do supervisor.

Devem ser apoiados por substrate mecânico sempre que possível, especialmente:

- leitura padronizada dos artefactos dos operators
- validação de schema
- recolha de statuses
- agregação de outputs
- dedupe/normalização básica
- geração da base do artefacto compilado
- geração da base do relatório final do sector

### Regra prática

O supervisor continua dono da decisão.

Mas não deve ser forçado a fazer toda a mecânica de forma manual/conversacional se houver forma mais determinística de suportar essa fase.

---

## Fase 1 — Monitorização dos operators

Depois do dispatch, o supervisor entra numa fase de observação da execução.

### O que deve monitorizar por operator

Para cada operator activo, o supervisor deve observar:

- existência de `status.json`
- existência de `checkpoint.json`
- existência de `output.json`
- sinais de progresso útil
- sinais de falha explícita
- timeout excedido

### Estados operacionais úteis

Cada operator deve acabar mapeado num destes estados operacionais:

- `pending`
- `running`
- `completed`
- `failed`
- `timed_out`
- `invalid_output`

### Regra

O supervisor deve monitorizar principalmente por artefactos persistidos no disco, não por respostas textuais soltas do agent.

---

## Fase 2 — Validação dos outputs dos operators

Quando um operator aparenta ter terminado, o supervisor valida o resultado.

### Validação mínima por operator

1. o `output_path` esperado existe
2. o ficheiro abre sem erro
3. o schema mínimo esperado está presente
4. o conteúdo é coerente com o `operator_name`
5. existe output útil ou uma falha explícita bem formada

### Observação importante

Output vazio não deve ser tratado automaticamente como sucesso.

É necessário distinguir entre:

- output vazio mas legítimo
- output vazio por falha silenciosa
- output malformado
- output da família errada

---

## Fase 3 — Retry selectivo

Se um operator falhar, o supervisor não deve, por defeito, reiniciar o sector inteiro.

### Regra base

O retry deve ser preferencialmente **selectivo por operator**.

### Exemplos

- `human_subject_extractor` falha -> retry apenas deste operator
- `object_artifact_extractor` produz schema inválido -> retry apenas deste operator

### Casos típicos em que retry é permitido

- timeout
- output não escrito
- JSON inválido
- schema inválido
- falha explícita recuperável

### Casos em que retry do operator pode não ser o caminho certo

Se a falha for estrutural upstream, o problema pode estar em:

- `source_package` quebrado
- dispatch payload malformado
- paths inválidos
- config inconsistente

Nesses casos, o problema já não é apenas do operator. Pode ser falha do supervisor, do bootstrap ou do sector.

### Política v1 recomendada

- 1 execução inicial
- 1 retry selectivo por operator, quando a falha for recuperável
- se falhar novamente, marcar operator como falhado
- o supervisor decide então se o sector fecha degradado ou falha completamente

---

## Fase 4 — Compile / merge do sector

Quando os operators válidos terminam, o S3 entra na fase de compilação.

Esta fase deve ser tratada como responsabilidade conjunta de supervisor + substrate mecânico.

### Objectivo do compile

Produzir o artefacto canónico final do S3 para downstream:

```text
{sector_root}/compiled/compiled_entities.json
```

### Subfases do compile

#### 4.1 Colecta dos outputs válidos

Ler os outputs válidos dos operators:

- `human_subject_extractor/output.json`
- `environment_location_extractor/output.json`
- `object_artifact_extractor/output.json`
- `symbolic_event_extractor/output.json`

#### 4.2 Normalização inicial

Padronizar estrutura suficiente para permitir merge inter-output.

#### 4.3 Dedupe / overlap resolution

Resolver overlap entre outputs, incluindo casos como:

- entidade descrita em mais de um operator
- objecto com dimensão simbólica
- grupo humano associado a evento colectivo
- lugar vs artefacto contextual

#### 4.4 Priorização / weighting

Aplicar:

- `entity_focus`
- regras da conta
- thresholds de relevância
- recorrência entre scenes
- especificidade

#### 4.5 Geração do artefacto compilado final

Escrever o `compiled_entities.json` final em `compiled/`.

---

## Fase 5 — Relatório final do sector

Além do artefacto machine-facing, o S3 deve produzir um relatório humano-legível.

### Artefacto recomendado

```text
{sector_root}/compiled/s3_sector_report.md
```

### Função do relatório

Este relatório existe para:

- auditoria humana
- debugging
- revisão rápida do resultado do sector
- facilitar alinhamento entre Tobias, Lucca, Claude Code e runtime downstream

### Regra recomendada

O relatório final não deve depender apenas de escrita manual do supervisor.

A melhor divisão é:

- substrate/helper gera uma base estruturada
- supervisor revê, completa e assume o fecho

---

## Pacote final de output do S3

A fase final do S3 deve produzir pelo menos 2 artefactos principais.

### 1. Machine-facing

```text
compiled/compiled_entities.json
```

Este é o output operacional canónico do S3.

É este ficheiro que downstream deve consumir.

### 2. Human-facing

```text
compiled/s3_sector_report.md
```

Este é o relatório final do sector, voltado a humanos e debugging.

---

## Shape macro recomendado do `compiled_entities.json`

A estrutura exacta ainda pode evoluir, mas a shape macro v1 recomendada é:

```json
{
  "sector": "s3_visual_planning",
  "contract_version": "s3.compiled_entities.v1",
  "job_id": "job_006_pt_guinle_001",
  "video_id": "video_abc123",
  "account_id": "006",
  "language": "pt-BR",
  "status": "completed",
  "entity_focus": {
    "priority_mode": "strict_precision",
    "coverage_mode": "balanced"
  },
  "sources": {
    "source_package_path": ".../inputs/s3_source_package.json"
  },
  "operators": {
    "human_subject_extractor": {
      "status": "completed",
      "output_path": ".../operators/human_subject_extractor/output.json"
    },
    "environment_location_extractor": {
      "status": "completed",
      "output_path": ".../operators/environment_location_extractor/output.json"
    },
    "object_artifact_extractor": {
      "status": "completed",
      "output_path": ".../operators/object_artifact_extractor/output.json"
    },
    "symbolic_event_extractor": {
      "status": "completed",
      "output_path": ".../operators/symbolic_event_extractor/output.json"
    }
  },
  "compiled_entities": {
    "human_subjects": [],
    "environment_locations": [],
    "object_artifacts": [],
    "symbolic_events": []
  },
  "compile_notes": [],
  "warnings": [],
  "generated_at": "ISO_TIMESTAMP"
}
```

### Função desta shape

Ela dá ao downstream:

- identidade do sector/job
- referência às fontes usadas
- estado dos operators
- blocos compilados por família macro
- warnings e notas de compile

---

## Shape macro recomendado do `s3_sector_report.md`

Estrutura conceptual recomendada:

```md
# S3 Sector Report

## Job
- job_id: ...
- video_id: ...
- account_id: ...
- language: ...

## Final Status
- status: completed
- compile_mode: full / degraded
- generated_at: ...

## Operators
- human_subject_extractor: completed
- environment_location_extractor: completed
- object_artifact_extractor: completed
- symbolic_event_extractor: failed_once_then_retried_successfully

## Entity Summary
### Human Subjects
- X entities compiled
- principais: ...

### Environment / Locations
- X entities compiled
- principais: ...

### Object / Artifacts
- X entities compiled
- principais: ...

### Symbolic / Events
- X entities compiled
- principais: ...

## Warnings
- ...

## Notes for Downstream
- ...
```

### Função desta shape

Ela dá aos humanos:

- resumo rápido do sector
- visão do estado dos operators
- visão compacta do que foi compilado
- warnings relevantes
- notas úteis para o próximo sector

---

## Fase 6 — Fecho do sector

Depois do compile e do relatório, o supervisor decide o estado final do sector.

### Caso A — sucesso limpo

Condições:

- outputs mínimos necessários válidos
- compile executado com sucesso
- `compiled_entities.json` válido
- `s3_sector_report.md` gerado

Resultado:

- sector marcado como completo
- checkpoint final escrito
- sector pronto para handoff downstream

### Caso B — sucesso degradado / parcial

Condições:

- algum operator falhou
- mas compile ainda é utilizável
- downstream ainda consegue consumir o output com warnings explícitos

Resultado:

- sector pode fechar com degradação controlada
- relatório final precisa salientar o modo degradado
- warnings precisam ser persistidos explicitamente

### Caso C — falha do sector

Condições:

- faltam outputs críticos
- compile não é confiável
- `compiled_entities.json` não pode ser produzido com qualidade mínima

Resultado:

- sector falha
- checkpoint de falha final escrito
- sem handoff downstream

---

## Artefactos recomendados no pós-dispatch

### Por operator

Dentro de:

```text
operators/<operator_name>/
```

Artefactos recomendados:

- `status.json`
- `checkpoint.json`
- `output.json`
- `log.md`

### No nível do sector

Dentro de:

```text
checkpoints/
```

Artefactos recomendados:

- `operator_monitoring_snapshot.json`
- `operator_validation_report.json`
- `operator_retry_report.json`
- `s3_compile_started.json`
- `s3_compile_completed.json`
- `s3_sector_completed.json` ou `s3_sector_failed.json`

---

## Handoff para downstream

Se o sector fechar com sucesso utilizável, o supervisor deve deixar o S3 pronto para consumo downstream.

### Regra arquitectural

O supervisor não precisa necessariamente de chamar o S4 directamente, caso essa responsabilidade fique com Paperclip/workflow.

Mas precisa deixar o sector:

- validado
- compilado
- claramente encerrado
- com output canónico persistido
- com relatório final persistido
- com estado final inequívoco

---

## Resumo executivo

Depois que os operators terminam, o supervisor deve:

1. monitorizar os operators por artefactos persistidos
2. validar os outputs produzidos
3. fazer retry selectivo quando a falha for recuperável
4. compilar `compiled_entities.json`
5. gerar `s3_sector_report.md`
6. decidir e persistir o estado final do sector
7. preparar o sector para handoff downstream

---

## Estado desta definição

**Status:** v1 do post-dispatch flow do S3

Esta definição fecha:

- o comportamento do supervisor depois do dispatch
- a divisão supervisor vs substrate/helper na fase final
- a lógica de monitorização, validação e retry selectivo
- a consolidação do output final do S3
- o pacote final de output (`compiled_entities.json` + `s3_sector_report.md`)
- os estados finais possíveis do sector

Próximo passo natural: criação efectiva dos directórios, contracts e workspaces dos 5 agents do S3.
