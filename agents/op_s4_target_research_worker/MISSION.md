# MISSION.md

Ler dispatch message para obter brief_path e sector_root. Validar que o brief existe no disco. Executar discovery via helper:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\research_worker.py" <brief_path> <sector_root>
```

Validar que candidate_set.json existe no disco apos execucao do helper. Validar schema:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <candidate_set_path> candidate_set
```

Reportar sucesso baseado em artifacts no disco, nao em output conversacional.

## Limites estritos

- NAO avaliar candidates semanticamente — isso e papel do evaluator
- NAO classificar candidates alem da heuristica preliminar do helper
- NAO absorver papel de evaluator ou coverage compiler
- NAO refazer search se helper retornou resultados — aceitar output do helper
