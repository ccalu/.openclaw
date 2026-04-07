# Transition Plan — From Dry Run to Real Agent Run

## Objectivo

Este documento fecha a transição entre:
- dry run estrutural simulado
- primeiro run narrow com agents reais

---

## O que já está provado

Já está provado mecanicamente:
- bootstrap do B2
- geração do bootstrap do S3
- geração de dispatch payloads
- validação de outputs
- compile do S3
- geração do report
- espelho `s3_completed.json`
- fecho `b2_completed.json`

---

## O que falta trocar pela execução real dos agents

### 1. Director real
Substituir o bootstrap manual por um turno real do `b2_director`.

### 2. Supervisor real
Substituir a simulação do supervisor por um turno real do `sm_s3_visual_planning`.

### 3. Operators reais
Substituir os fake outputs por turns reais dos 4 operators.

---

## Sequência narrow recomendada

### Fase A
Usar os helpers mecânicos já criados para reduzir incerteza.

### Fase B
Fazer o supervisor real preparar dispatches e apenas validar a capacidade de ler/bootstrapar o sector.

### Fase C
Executar um operator real isolado primeiro.

### Fase D
Executar os 4 operators reais.

### Fase E
Fechar compile/report/checkpoint com supervisor real.

### Fase F
Fechar reentrada e completion com director real.

---

## Regra estratégica

Não tentar ir de simulação total para full real run em um salto só.

A transição correcta é:
- director real
- supervisor real
- um operator real
- depois os 4
- depois completion real do bloco
