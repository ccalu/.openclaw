# MISSION.md

Ler dispatch message para obter intake_path, sector_root, job_id, video_id, account_id, language. Executar compilacao via helper:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\pack_compiler.py" <intake_path> <sector_root> <job_id> <video_id> <account_id> <language>
```

Validar que `s4_research_pack.json` existe no disco em `<sector_root>/compiled/s4_research_pack.json`. Validar que `s4_sector_report.md` existe no disco em `<sector_root>/compiled/s4_sector_report.md`. Validar schema:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <sector_root>/compiled/s4_research_pack.json research_pack
```

Reportar sucesso baseado em artifacts no disco, nao em output conversacional.

## Limites estritos

- NAO esconder unresolved gaps — gaps sao verdade do sector
- NAO summarizar loosely — pack deve ser fiel aos inputs
- NAO reclassificar candidates — evaluated sets sao verdade
- NAO refazer coverage analysis — coverage report e input, nao output
- NAO interpretar ou alterar output do helper — aceitar resultado
