# CONTRACT.md

## Input
- Dispatch message com: brief_path, sector_root
- Helper le o brief e executa Brave Search + Firecrawl fallback

## Output
- `targets/<target_id>/<target_id>_candidate_set.json` conformando a `s4.candidate_set.v1`

## Candidate fields
Cada candidate contem:
- source_url: URL real da fonte
- page_title: titulo da pagina
- source_domain: dominio extraido
- preliminary_classification: heuristica do helper (factual_evidence, visual_reference, stylistic_inspiration)
- confidence: 0-1
- licensing_note: hint de licenciamento (public_domain_or_cc, rights_reserved, free_license, unknown)
- acquisition_mode: reference_only (default)
- local_asset_path: pode ser null
- preview_path: pode ser null
- capture_path: pode ser null

## Success criteria
- candidate_set.json existe no disco
- Schema valida via schema_validator.py

## Edge cases
- Zero candidates e valido (com warning) — nao e falha
- Helper retorna resultados parciais — aceitar, nao refazer

## Boundary
- Discovery only — sem avaliacao semantica de candidates
