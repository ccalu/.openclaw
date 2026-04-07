# OPERATIONS.md

## Sequencia de execucao

1. Parse activation message para obter: candidate_set_path, brief_path, sector_root, target_id
2. Ler candidate_set.json do candidate_set_path (`exec cat`)
3. Ler target_research_brief.json do brief_path (`exec cat`)
4. Avaliar TODOS os candidates em um unico pass. Para cada candidate:
   - Considerar do candidate_set: source_url, page_title, source_domain, preliminary_classification, rationale, confidence
   - Considerar do brief: canonical_label, target_type, research_modes, search_goals, research_needs
   - Determinar final_classification independentemente (NAO copiar preliminary_classification):
     - factual_evidence: historicamente fundamentado, documentariamente credivel
     - visual_reference: visualmente util para representacao mas nao necessariamente factual
     - stylistic_inspiration: valor de mood/estilo/composicao
     - reject: nao relevante ou nao suficientemente util
   - Escrever target_fitness_note: quao bem este candidate serve este target?
   - Escrever downstream_usefulness_note: quao util para S5/S6 downstream?
   - Escrever asset_usability_note: qualidade/usabilidade do ficheiro local/referencia
   - Decidir is_best_candidate: true apenas para os candidates mais fortes
5. Montar evaluated_candidate_set.json completo com todos os campos required
6. Escrever ficheiro em `<sector_root>/targets/<target_id>/<target_id>_evaluated_set.json`
7. Validar: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <output_path> evaluated_candidate_set`
8. Reportar resultado

## Regras

- UMA execucao por candidate set, nao por candidate individual
- final_classification deve ser julgamento semantico independente
- best_candidate_ids deve referenciar evaluated_candidates com is_best_candidate=true
- evaluator_notes e warnings devem ser sempre arrays (podem ser vazios)
- NAO inventar candidates que nao existem no input set
- Incerteza deve ser surfaced em notes/warnings, nao escondida
