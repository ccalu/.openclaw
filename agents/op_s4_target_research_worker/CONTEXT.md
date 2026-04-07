# CONTEXT.md

## Posicao no S4
- Terceiro operador do S4 (apos target_builder e web_investigator)
- Executa web discovery real para um target especifico
- Produz candidate_set consumido pelo evaluator downstream

## Fluxo
1. target_builder cria target intake com metadata estruturada
2. web_investigator produz research brief com search goals
3. **research_worker executa discovery real** (este actor)
4. candidate_evaluator avalia e classifica os candidates

## Stack de discovery
- **Brave Search** como fonte primaria (API free tier)
- **Firecrawl** como fallback (scrape/search CLI)
- Helper Python executa ambos — o LLM nao faz search direto

## Design: helper-backed
O LLM nao performa web searches. Ele:
1. Le o dispatch
2. Chama o helper via exec
3. Valida outputs no disco
4. Reporta resultado
