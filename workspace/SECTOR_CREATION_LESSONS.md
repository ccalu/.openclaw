# SECTOR_CREATION_LESSONS.md

## Propósito

Checklist operacional curta para criação e consolidação de novos sectores do Bloco 2, baseada nas lições reais absorvidas sobretudo em S3 e S4.

Não substitui docs de arquitectura do sector.
Serve para evitar erros repetidos de materialização, boundary design, runtime truth e documentação.

---

## 1. Congelar o boundary antes de materializar

Antes de criar actors, fechar explicitamente:
- input canónico
- output canónico
- artefactos persistidos no disco
- quem transforma o quê entre sectores
- o que é contrato vs implementação vs doc operacional

Perguntas obrigatórias:
- Qual é a fonte de verdade operacional deste sector?
- Qual é o artefacto central do sector?
- Onde acaba o sector anterior e onde começa este?
- Há tradução semântica no boundary ou só transformação de formato?

---

## 2. Não assumir que mais actors é melhor

Materializar actors tem custo estrutural.
Não agentizar o miolo por prestígio ou simetria visual.

### Sinais de over-materialization
- mais de metade dos actors acabam a servir só de casca para helpers
- o debugging real acontece quase todo em Python e não nos turns dos agents
- paths, artefactos e checkpoints ficam mais confiáveis no substrate do que nos actors
- o sector precisa de controlo forte de retries, validação, I/O, resume e ordem determinística
- o actor começa a “inventar” lógica em vez de apenas cumprir o contract

### Regra prática
Se o miolo precisa de:
- controlo forte de paths
- manipulação intensiva de artefactos
- checkpoint-resume
- validação de schema
- retries controlados
- comportamento determinístico

então considerar seriamente **helper-direct + substrate Python** como arquitectura principal dessa parte.

---

## 3. Distinguir actor, helper-direct e substrate de suporte

Sempre classificar explicitamente:
- **actor OpenClaw activo**
- **helper-direct activo**
- **support substrate**
- **legacy retained**
- **candidate for removal**

Sem esta distinção, a topologia do sector degrada rapidamente.

---

## 4. Runtime truth vive no disco, não na conversa

Um sector só está realmente provado quando houver evidência em runtime real:
- artefactos escritos
- checkpoints correctos
- schemas a passar
- status/completion consistentes
- resume funcional quando aplicável

Nunca usar resumo conversacional de agent como fonte de verdade operacional final.

---

## 5. Materialização só conta quando é real

Pasta local + docs + intenção não bastam.

Um actor só conta como materializado quando:
1. existe no OpenClaw
2. aparece em `openclaw agents list`
3. executa um turno real
4. produz output no shape correcto

---

## 6. Shortcuts tácticos não podem virar padrão por acidente

Exemplos típicos:
- keys hardcoded em Python
- dual-format fallback mantido demasiado tempo
- actor deprecated ainda presente mas tratado como se fosse activo
- provider improvisado por conveniência local

### Regra
Se algo for um desvio pragmático:
- documentar explicitamente como **táctico / temporário**
- escrever o risco
- escrever o caminho de migração
- impedir que isso seja copiado para o próximo sector sem revisão

---

## 7. Quando substituir um artefacto central, adaptar downstream rápido

Se o sector troca a sua fonte de verdade (ex.: `candidate_set` -> `asset_materialization_report`):
- coverage
- pack compiler
- sector report
- docs de contract
- troubleshooting

precisam ser alinhados cedo.

Senão o sistema começa a:
- funcionar no runtime
- mas mentir nos reports

E isso é uma forma perigosa de dívida.

---

## 8. Boundary translation merece peça própria

Se o sector anterior produz entidades cruas e o sector seguinte precisa de alvos operacionais, não colapsar isso numa conversão burra.

Criar explicitamente uma camada de tradução/consolidação quando necessário.

Exemplo genérico:
- sector A produz entidades semânticas
- sector B precisa de targets pesquisáveis / executáveis
- logo, o boundary precisa de:
  - dedup/consolidation
  - contextualização
  - searchability / viability classification
  - provenance

---

## 9. Usar removal gates em vez de apagar cedo

Antes de remover legado, exigir gates claros.

Gate mínimo recomendado:
1. novo core provado E2E em outro caso real além do piloto
2. nenhum import/runtime path aponta para legado
3. docs canónicos já foram actualizados e revistos

Até lá:
- marcar como deprecated
- arquivar histórico
- não apagar por impulso

---

## 10. Fechar cada sector em 4 camadas

Antes de usar um sector como template do próximo, verificar:

### A. Runtime
- pipeline provado
- artefactos correctos
- checkpoints/status correctos

### B. Canonical docs
- arquitectura actualizada
- contracts/schemas actualizados
- invocation/runtime flow actualizados

### C. Agent-local docs
- OPERATIONS/MISSION/CONTRACT alinhados com o real
- deprecated marcado como deprecated

### D. Meta-learning
- postmortem
- troubleshooting
- padrões reutilizáveis
- memória actualizada
- checklist melhorada

Se estas 4 camadas não estiverem fechadas, o sector ainda não virou bom template.

---

## Frase-regra

**Não optimizar para “ficou bonito como grafo de agents”. Optimizar para a arquitectura mais legível, auditável e robusta que realmente funcione.**
