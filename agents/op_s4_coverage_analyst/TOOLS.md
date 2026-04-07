# TOOLS.md

## coverage_analyst.py

Helper principal. Determina cobertura por target e por cena.

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\coverage_analyst.py" <intake_path> <sector_root>
```

- Le intake (targets + scene_index) e evaluated sets de cada target
- Produz `<sector_root>/compiled/coverage_report.json`
- Schema: `s4.coverage_report.v1`

## schema_validator.py

Validador de schema para artifacts S4.

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <artifact_path> <schema_type>
```

- Para coverage report usar schema_type: `coverage_report`
- Retorna exit code 0 se valido, non-zero se invalido
