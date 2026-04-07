# TOOLS.md

## pack_compiler.py

Helper principal. Compila todos os artefactos S4 no research pack e sector report.

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\pack_compiler.py" <intake_path> <sector_root> <job_id> <video_id> <account_id> <language>
```

- Le intake, evaluated sets, coverage report, raw candidate sets
- Produz `<sector_root>/compiled/s4_research_pack.json` (schema: `s4.research_pack.v1`)
- Produz `<sector_root>/compiled/s4_sector_report.md`
- Valida pack internamente via schema_validator antes de escrever

## schema_validator.py

Validador de schema para artifacts S4.

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <artifact_path> <schema_type>
```

- Para research pack usar schema_type: `research_pack`
- Retorna exit code 0 se valido, non-zero se invalido
