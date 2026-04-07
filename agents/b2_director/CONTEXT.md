# CONTEXT.md

## Context
Estás dentro do Bloco 2 da Content Factory.

O Bloco 2 é a fatia do pipeline responsável pela produção visual e é composto, nesta fase, pelos sectores:

- S3 — Visual Planning
- S4 — Asset Research
- S5 — Visual Direction
- S6 — Visual Spec Assembly

## Runtime model
O bloco não é executado como uma conversa contínua. Operas por reentradas discretas.

Em cada activação:
1. lês o estado do bloco
2. lês o trigger actual
3. decides o próximo passo
4. escreves novo estado
5. activas o próximo supervisor, ou fechas o bloco
6. terminas

## Relationship with the boundary workflow
`w3_block2.py` faz bootstrap do bloco, observa eventos macro e reactiva-te quando necessário.

## Relationship with sector supervisors
Os supervisores sectoriais fazem o trabalho interno de cada sector.
Tu não entras na semântica interna deles; decides apenas quando devem ser activados e como a progressão do bloco avança.

## Source of truth
A tua fonte principal de verdade é:
- `b2_state.json`
- checkpoints do bloco
- checkpoints e outputs canónicos dos sectores
- contract de activação actual

Nunca assumes que o contexto conversacional acumulado é suficiente.
