# CONTEXT.md

## Posicao no S4

Quarto operador do S4 (Asset Research sector).

## Fluxo

- Recebe candidate_set + brief do worker upstream
- Produz evaluated_candidate_set com classificacao semantica canonica
- Output consumido por coverage_analyst e pack_compiler downstream

## Autoridade

Autoridade canonica de classificacao semantica para o sector.
A classificacao final deste actor e a verdade que downstream consome.

## Semantica

Output e overlay sobre candidate_set, nao replacement.
Downstream faz join por candidate_id entre raw e evaluated layers.
