# CONTEXT.md

## S4 — Asset Research

S4 e o sector de Asset Research do Block 2 (B2) do Content Factory.

### Posicao no pipeline
- Upstream: S3 (Visual Planning) — recebe `compiled_entities.json` como input principal
- Downstream: S5 (Visual Direction) — consome `s4_research_pack.json`

### Objectivo
Produzir um research pack com:
- visual references (imagens de referencia para composicoes)
- factual evidence (evidencia factual para contexto historico/narrativo)
- stylistic inspiration (inspiracao estilistica para direccao visual)

### Operators do S4
1. `op_s4_target_builder` — normaliza entities em research targets
2. `op_s4_web_investigator` — planeia discovery e gera briefs por target
3. `op_s4_target_research_worker` — executa web research (Brave/Firecrawl)
4. `op_s4_candidate_evaluator` — avalia e classifica candidatos
5. `op_s4_coverage_analyst` — analisa cobertura target-level e scene-level
6. `op_s4_pack_compiler` — compila pack final + sector report

### Artefactos finais
- `s4_research_pack.json` — pack estruturado para downstream
- `s4_sector_report.md` — relatorio human-readable do sector
