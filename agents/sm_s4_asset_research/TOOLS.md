# TOOLS.md

## Helper tools disponiveis

Todos os helpers estao em:
`C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\`

Invocacao: `exec python "<helper_path>" <args>`

### dirs.py
Cria a estrutura de directorias do S4 (intake, targets, compiled, checkpoints, dispatch, logs, runtime).

### target_builder.py
Constroi research intake a partir das compiled entities do S3.

### batch_manifest_builder.py
Gera batch manifest a partir do intake (define batches, ordering, parallelism cap).

### web_investigator.py
Constroi target research briefs com search goals e storage paths.

### research_worker.py
Executa web research via Brave Search + Firecrawl para um target. Produz candidate_set.

### candidate_evaluator.py
Avalia candidatos contra o brief. Produz evaluated_candidate_set com classificacoes finais.

### coverage_analyst.py
Analise heuristica de cobertura — target-level e scene-level. Produz coverage_report.

### pack_compiler.py
Compila final pack (`s4_research_pack.json`) + sector report (`s4_sector_report.md`).

### schema_validator.py
Valida artefactos contra JSON schemas definidos. Retorna pass/fail + erros.

### checkpoint_writer.py
Escreve checkpoints de status, completion e failure. Inclui B2 mirror.

### bootstrap_loader.py
Carrega e valida o bootstrap do supervisor. Retorna campos parsed ou erro.
