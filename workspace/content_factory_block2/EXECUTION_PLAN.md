# EXECUTION_PLAN.md — Content Factory Block 2

## Objectivo deste documento

Este documento é o plano-mãe de execução do **Content Factory Block 2**.

O seu objectivo não é apenas resumir arquitectura. O seu objectivo é servir como **plano operacional de implementação**, suficientemente claro, completo e accionável para que:

- Tobias consiga implementar o sistema com baixa ambiguidade
- subagentes possam ser activados para ajudar em partes da execução sem desalinhar a arquitectura
- a equipa tenha a maior probabilidade possível de fazer o **primeiro teste do B2** exactamente como planeado
- a integração com o Paperclip e com o agent do lado Paperclip (**Perseus**) seja feita de forma compatível com o desenho já aprovado

Este documento deve funcionar como a referência principal de execução para a fase actual do B2.

---

## Objectivo da fase actual

A fase actual não é “construir o Bloco 2 inteiro em produção final”.

A fase actual é:

> construir a primeira versão executável e testável do Bloco 2 com foco inicial em **S3 only**, validando a integração real entre Paperclip e OpenClaw.

### Formulação exacta do objectivo

Validar que o sistema consegue executar, de ponta a ponta, a seguinte cadeia:

```text
Paperclip
  -> Perseus
    -> W3 / boundary do B2
      -> b2_director
        -> sm_s3_visual_planning
          -> S3 operators
            -> compiled_entities.json
```

### Resultado desejado desta fase

Provar que o B2 pode ser activado do lado Paperclip, entrar no OpenClaw, executar o S3 completo com agents reais, produzir os artefactos esperados, encerrar o sector correctamente e dar sinais compatíveis com o runtime macro do B2.

---

## Escopo exacto do primeiro teste

O primeiro teste do B2 deve ser **deliberadamente limitado**.

### O que entra no primeiro teste

- integração Paperclip -> Perseus -> boundary B2 -> OpenClaw
- activação do `b2_director`
- activação do `sm_s3_visual_planning`
- execução dos 4 operators do S3
- outputs por operator persistidos no disco
- validação e compile do S3
- produção de `compiled_entities.json`
- produção de `s3_sector_report.md`
- checkpoint final de S3
- progressão do B2 até reconhecer que o S3 foi concluído

### O que não precisa entrar ainda no primeiro teste

- implementação real do S4
- implementação real do S5
- implementação real do S6
- retry macro sofisticado no `b2_director`
- recovery avançado multi-sector
- optimizações de runtime
- observabilidade refinada de produção

### Simplificação recomendada para o primeiro teste

O B2 v1 pode operar num **test mode focado em S3**, onde o director considera o bloco suficientemente provado assim que:

- S3 executa com sucesso
- output canónico do S3 foi produzido
- o estado do bloco ficou coerente

Isto pode significar uma de duas abordagens:

1. **B2 test mode = stop after S3**
2. ou **B2 normal mode, mas com S4/S5/S6 ainda não implementados e explicitamente não activados**

A decisão exacta de implementação pode ser tomada depois, mas o princípio é:

> o primeiro teste existe para provar o encadeamento e o runtime real do B2 com S3, não para resolver já o bloco inteiro.

---

## Decisões arquitecturais já fechadas

As seguintes decisões devem ser tratadas como fechadas para esta fase.

---

### 1. O Bloco 2 é uma unidade paperclip-facing única

O Paperclip não deve orquestrar S3, S4, S5 e S6 sector a sector.

O Paperclip deve ver o B2 como uma unidade única.

---

### 2. O interior do B2 é orquestrado pelo OpenClaw

A progressão interna S3 -> S4 -> S5 -> S6 deve ser coordenada no OpenClaw.

---

### 3. Existe uma boundary layer do B2

O Paperclip conversa com uma boundary surface do B2, representada nesta fase por algo como:

- `w3_block2.py`

Esta peça faz bootstrap, observa eventos macro do bloco e reactiva o director quando necessário.

---

### 4. O `b2_director` é o control plane interno do bloco

O `b2_director` lê estado persistido do B2, interpreta eventos macro, decide o próximo sector e activa o supervisor sectorial apropriado.

---

### 5. O runtime do B2 é orientado a artefactos + reentradas discretas

O sistema não depende de conversas contínuas entre agents.

O estado vive em artefactos persistidos.

Os agents fazem turnos discretos de decisão/controlo.

---

### 6. O S3 é o primeiro sector a ser implementado

O primeiro sector real do B2 a ser implementado e testado é o **S3 — Visual Planning**.

---

### 7. O S3 já tem uma decomposição macro fechada

O S3 opera com:

- 1 supervisor sectorial
- 4 operators principais
- compile/merge no supervisor/substrate

---

### 8. O S3 tem 4 operators principais

- `op_s3_human_subject_extractor`
- `op_s3_environment_location_extractor`
- `op_s3_object_artifact_extractor`
- `op_s3_symbolic_event_extractor`

---

### 9. Contexto limpo por invocação é obrigatório

Esta é uma regra estrutural crítica.

Sempre que o supervisor invocar um operator, e sempre que o B2 Director ou supervisor forem activados para novo job/evento, a execução deve começar com contexto limpo.

O sistema não deve depender de carry-over conversacional entre vídeos/jobs.

---

### 10. Todos os agents desta fase devem usar GPT-5.4 mini via OpenAI OAuth

Esta é a configuração-alvo para:

- `b2_director`
- `sm_s3_visual_planning`
- todos os operators do S3
- outros agents auxiliares desta fase, quando aplicável

---

## Arquitectura-alvo da fase actual

### Fluxo macro

```text
Paperclip
  -> Perseus
    -> W3 / boundary B2
      -> b2_director
        -> sm_s3_visual_planning
          -> op_s3_human_subject_extractor
          -> op_s3_environment_location_extractor
          -> op_s3_object_artifact_extractor
          -> op_s3_symbolic_event_extractor
```

### Artefacto final esperado do S3

- `compiled_entities.json`
- `s3_sector_report.md`

### Estado de bloco esperado no teste inicial

- o B2 deve conseguir reconhecer que o S3 concluiu com sucesso
- o runtime do B2 deve ficar coerente e observável

---

## Inventário do que precisa ser criado

Esta secção enumera, sem ambiguidade, o que precisa realmente ser criado para a fase actual.

---

## A. Agents OpenClaw

### 1. Director do bloco
- `b2_director`

### 2. Supervisor do S3
- `sm_s3_visual_planning`

### 3. Operators do S3
- `op_s3_human_subject_extractor`
- `op_s3_environment_location_extractor`
- `op_s3_object_artifact_extractor`
- `op_s3_symbolic_event_extractor`

---

## B. Workspaces locais dos agents

Precisam ser criados os workspaces locais, com os ficheiros apropriados, para:

- `b2_director`
- `sm_s3_visual_planning`
- os 4 operators do S3

---

## C. Docs centrais do bloco e do sector

Já existe base documental considerável, mas ainda precisam ser criados e/ou refinados docs centrais como:

### B2
- `B2_runtime_control_flow.md` ✅
- `B2_director.md` ✅
- eventualmente contracts/layout complementares do B2

### S3
- `inputs.md` ✅
- `architecture.md` ✅
- `workflow_bootstrap.md` ✅
- `supervisor.md` ✅
- `operators.md` ✅
- `runtime_layout.md` ✅
- `post_dispatch.md` ✅

### Ainda por criar/refinar
- contracts centrais do S3
- schemas formais do S3
- docs de operation local do supervisor e operators

---

## D. Contracts centrais a criar

### B2
- contract de bootstrap do B2
- contract de reentrada do `b2_director`
- contract boundary B2 <-> Paperclip/Perseus

### S3
- `supervisor_bootstrap_contract`
- `operator_dispatch_contract`
- `operator_registry`
- contract de output compilado do S3

---

## E. Schemas / artefactos formais a criar

### S3 operator outputs
- `human_subject_output.schema.json`
- `environment_location_output.schema.json`
- `object_artifact_output.schema.json`
- `symbolic_event_output.schema.json`

### S3 compiled output
- `compiled_entities.schema.json`

### B2 state/output
- schema macro de `b2_state.json` (pode começar documental e virar JSON schema depois)
- schema macro de `b2_completed.json` / `b2_failed.json` se necessário

---

## F. Helpers / substrate / “skills” Python necessários

Nem tudo deve ficar “no prompt”.

Para aumentar previsibilidade, certas partes devem ser apoiadas por substrate mecânico.

### Mínimo recomendado para esta fase

#### S3
- helper de validação de output de operator
- helper de leitura/normalização dos outputs dos 4 operators
- helper de compile do `compiled_entities.json`
- helper de geração base do `s3_sector_report.md`

#### B2
- helper leve de leitura/escrita de `b2_state.json`
- helper leve de avaliação de eventos/checkpoints macro do bloco (se necessário)

### Regra

A implementação pode começar simples, mas deve tentar evitar que:

- schema validation fique puramente conversacional
- compile do S3 seja totalmente artesanal
- estado do B2 dependa de interpretação vaga

---

## G. Integração Paperclip

### Peça do lado Paperclip
- **Perseus**

### Papel esperado de Perseus
- activar e monitorar o B2 do lado Paperclip
- conversar com a boundary do B2
- não conhecer a topologia interna do B2 em detalhe fino

### Peças a alinhar do lado Paperclip
- contract de activação do B2
- contract de monitorização/status
- contract de retorno final
- comportamento no primeiro teste S3-only

---

## Sequência recomendada de implementação

Esta é a ordem recomendada para maximizar a probabilidade de sucesso no primeiro teste.

---

## Fase 1 — Consolidar a base documental e de execução

### Objectivo
Evitar começar implementação real sem plano operacional claro.

### Tarefas
- consolidar este `EXECUTION_PLAN.md`
- garantir que docs do B2 e S3 estão organizados em `content_factory_block2/`
- listar explicitamente o que falta criar
- alinhar naming final das peças principais

### Status actual
Em progresso / muito avançado.

---

## Fase 2 — Fechar contracts centrais mínimos

### Objectivo
Criar as interfaces canónicas que vão evitar drift entre agents e implementation helpers.

### Tarefas
- criar `S3/contracts/operator_dispatch_contract.md`
- criar `S3/contracts/operator_registry.md`
- criar `S3/contracts/supervisor_bootstrap_contract.md`
- criar contracts centrais mínimos do B2, se necessário

### Resultado esperado
Os agents deixam de depender apenas de docs narrativos e passam a ter interfaces explícitas.

---

## Fase 3 — Fechar schemas mínimos

### Objectivo
Definir shape mínimo dos outputs e permitir validação menos ambígua.

### Tarefas
- criar os 4 schemas de output dos operators do S3
- criar schema mínimo de `compiled_entities.json`
- opcionalmente formalizar o state/output do B2

### Resultado esperado
O supervisor e os helpers passam a ter alvos concretos de validação.

---

## Fase 4 — Criar workspaces reais dos agents OpenClaw

### Objectivo
Materializar os agents como entidades reais do runtime.

### Tarefas
- criar `sm_s3_visual_planning`
- criar os 4 operators do S3
- revisar/ajustar `b2_director` já criado
- configurar todos com GPT-5.4 mini via OpenAI OAuth

### Importante
Os workspaces locais devem manter apenas contexto operacional local. A verdade sistémica continua no workspace principal do bloco.

---

## Fase 5 — Implementar substrate/helpers mínimos

### Objectivo
Remover fragilidade desnecessária do fluxo v1.

### Tarefas
- criar validator mínimo de output de operator
- criar compile helper do S3
- criar gerador base do `s3_sector_report.md`
- criar helper leve de estado do B2, se necessário

### Regra
Não overengineer. Mas também não deixar tudo no improviso do prompt.

---

## Fase 6 — Ligar `b2_director` ao S3

### Objectivo
Fazer o director conseguir activar o S3 e reconhecer a sua conclusão.

### Tarefas
- definir activation flow real entre `b2_director` e `sm_s3_visual_planning`
- definir checkpoint `s3_completed.json` / `s3_failed.json`
- definir modo de teste do B2 com foco em S3-only
- garantir que `b2_state.json` evolui coerentemente

### Resultado esperado
O B2 já consegue percorrer a primeira etapa real do bloco.

---

## Fase 7 — Definir a peça do Paperclip (`Perseus`) e a boundary do B2

### Objectivo
Fechar a integração real do lado Paperclip.

### Tarefas
- definir o papel exacto de Perseus
- definir como Perseus activa o B2
- definir como Perseus monitora o B2
- definir como `w3_block2.py` se posiciona nessa interface
- decidir como o primeiro teste S3-only será tratado do lado Paperclip

### Resultado esperado
O Paperclip consegue disparar o B2 e interpretar correctamente o seu estado externo.

---

## Fase 8 — Executar o primeiro teste B2 v1 (S3-only)

### Objectivo
Fazer o primeiro teste real ponta-a-ponta.

### O teste deve provar
- Paperclip consegue iniciar o B2
- Perseus consegue acompanhar a execução macro
- o B2 entra no OpenClaw correctamente
- `b2_director` activa o S3
- S3 executa com agents reais
- S3 gera outputs por operator
- S3 compila `compiled_entities.json`
- S3 gera `s3_sector_report.md`
- o estado final do teste fica coerente e auditável

---

## Fase 9 — Corrigir fricções e só depois expandir

### Objectivo
Aprender com o primeiro teste antes de alargar escopo.

### Só depois disto
- avançar para S4
- introduzir retries mais sofisticados
- optimizar observabilidade
- refinamentos de produção

---

## Definição de “done” do primeiro teste

O primeiro teste é considerado bem-sucedido se, num job realista:

1. o Paperclip consegue iniciar o B2
2. Perseus activa/acompanha o B2 correctamente
3. o `b2_director` inicia o S3 sem ambiguidade
4. o `sm_s3_visual_planning` activa os 4 operators
5. os 4 operators escrevem outputs válidos ou explicitamente tratáveis
6. o supervisor compila `compiled_entities.json`
7. o supervisor gera `s3_sector_report.md`
8. checkpoints e estado do sector ficam correctos
9. o estado do B2 fica coerente com a conclusão do S3
10. tudo isto roda com GPT-5.4 mini via OpenAI OAuth

### Sinal importante de sucesso
O teste deve conseguir ser compreendido por artefactos no disco e pelo estado persistido, sem depender de conversa longa residual entre agents.

---

## Simplificações v1 explicitamente permitidas

Para aumentar a chance de sucesso no primeiro teste, as seguintes simplificações são permitidas e desejáveis.

### 1. Sem retry macro no `b2_director`
Se um sector falhar terminalmente nesta fase, o director pode simplesmente falhar o bloco.

### 2. Validação estrutural mínima no director
O director só precisa validar:
- existência do artefacto esperado
- validade estrutural mínima

Não precisa fazer validação semântica profunda do output sectorial.

### 3. S3 como único sector real do primeiro teste
Não tentar resolver S4/S5/S6 antes de provar que o S3 integra bem.

### 4. Logs leves mas suficientes
Preferir logs/checkpoints claros a overengineering de observabilidade.

### 5. Compile do S3 com helper simples
Não precisa ser a versão final perfeita, mas deve ser previsível e auditável.

---

## Riscos principais desta fase

### Risco 1 — Criar agents antes de fechar interfaces mínimas
Mitigação:
- contracts centrais e schemas mínimos antes da expansão total

### Risco 2 — Deixar lógica mecânica demais no prompt
Mitigação:
- helpers de validação/compile/estado

### Risco 3 — Misturar responsabilidades entre director, supervisor e operator
Mitigação:
- respeitar limites já fechados

### Risco 4 — O Paperclip acabar a conhecer demais o interior do B2
Mitigação:
- manter Perseus e a boundary do B2 como interface macro

### Risco 5 — Carry-over de contexto degradar outputs
Mitigação:
- contexto limpo por activação como regra imutável

---

## Regras operacionais obrigatórias para implementação

### 1. Context isolation por activação
Cada activação de:
- `b2_director`
- supervisor sectorial
- operator

...deve operar com contexto limpo e depender dos artefactos do job actual.

### 2. Estado no disco > memória conversacional
O estado do sistema deve ser recuperável por ficheiros persistidos.

### 3. Falha explícita > sucesso ambíguo
Se uma condição crítica não for satisfeita, falhar limpo é melhor do que avançar de forma duvidosa.

### 4. Não overengineer o primeiro teste
O primeiro teste existe para validar o encadeamento e o runtime real, não para resolver toda a produção visual final.

### 5. Todos os agents desta fase com o mesmo baseline de modelo
Usar GPT-5.4 mini via OpenAI OAuth em todos os agents desta fase, salvo mudança explícita posterior.

---

## Delegação para subagentes

Este documento também existe para permitir delegação segura.

### Subtarefas potencialmente delegáveis

- criação de contracts centrais
- criação de schemas mínimos
- criação de workspaces locais de agents
- criação de helpers Python simples
- revisão de consistência entre docs centrais e workspaces locais

### O que subagentes não devem mudar livremente

Sem nova aprovação explícita, subagentes não devem alterar:

- a decisão de tratar o B2 como unidade paperclip-facing
- o papel do `b2_director`
- a prioridade de S3-only no primeiro teste
- a regra de contexto limpo
- o modelo-base GPT-5.4 mini via OAuth
- a fronteira entre director / supervisor / operator

---

## Estratégia recomendada de execução para Tobias

Para maximizar a chance de sucesso, Tobias deve trabalhar nesta ordem:

1. consolidar interfaces mínimas
2. materializar agents do S3 e director
3. materializar helpers mínimos
4. alinhar a interface de Perseus com a boundary do B2
5. executar primeiro teste narrow
6. só depois expandir escopo

### Regra de ouro

> preferir um B2 v1 estreito, claro e funcional
> a um B2 amplo, elegante no papel e instável no primeiro teste

---

## Estado actual do plano

**Status:** plano-mãe de execução do Content Factory Block 2 — v1

Este documento fecha:

- o objectivo exacto da fase actual
- o escopo do primeiro teste
- as decisões arquitecturais já tomadas
- o inventário do que precisa ser criado
- a ordem recomendada de implementação
- a definição de sucesso do primeiro teste
- as simplificações e riscos da fase actual
- as regras operacionais obrigatórias para Tobias e subagentes

Próximos passos naturais imediatos:

1. criar/refinar contracts centrais mínimos
2. criar/refinar schemas mínimos
3. criar oficialmente os agents do S3
4. discutir/definir Perseus e a interface concreta do lado Paperclip
5. replicar explicitamente o padrão validado de integração sectorial para S5, incluindo `s5_requested.json`, `s5_completed.json`, `s5_failed.json` e o contract macro de handoff para S6
