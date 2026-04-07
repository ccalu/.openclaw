# CONTEXT.md

Ultimo operador do S4 (Asset Research sector). Produz os deliverables finais do sector.

Le intake (`s4_research_intake.json`), evaluated candidate sets, coverage report, e raw candidate sets. Compila tudo em `compiled/s4_research_pack.json` + `compiled/s4_sector_report.md`.

Consumido por:
- `sm_s4_asset_research` — usa pack e report para closure validation (sector completo vs gaps pendentes)
- `b2_director` — usa research pack para retomar pipeline apos S4
- S5 downstream — consome research pack como artefacto principal do S4
