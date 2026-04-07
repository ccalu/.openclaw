# CONTEXT.md

Quinto operador do S4 (Asset Research sector).

Le intake (`s4_research_intake.json`) e evaluated candidate sets produzidos pelo `op_s4_candidate_evaluator`, e produz `compiled/coverage_report.json` com estados de cobertura por target e por cena.

Consumido por:
- `op_s4_pack_compiler` — usa coverage states para estruturar target e scene summaries no pack final
- `sm_s4_asset_research` — usa coverage report para decisoes de closure (sector completo vs gaps pendentes)
