# MISSION.md

Ler dispatch message para obter intake_path e sector_root. Validar que o intake existe no disco. Executar coverage analysis via helper:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\coverage_analyst.py" <intake_path> <sector_root>
```

Validar que coverage_report.json existe no disco apos execucao do helper em `<sector_root>/compiled/coverage_report.json`. Validar schema:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <coverage_report_path> coverage_report
```

Reportar sucesso baseado em artifacts no disco, nao em output conversacional.

## Limites estritos

- NAO reclassificar candidates — evaluated sets sao verdade
- NAO refazer evaluation de candidates individuais
- NAO fazer discovery de novos candidates
- NAO compilar pack — isso e papel do pack_compiler
- NAO interpretar ou alterar output do helper — aceitar resultado
