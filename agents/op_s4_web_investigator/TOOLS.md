# TOOLS.md

## schema_validator.py
Validador de schema para briefs de S4.
```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <brief_path> target_research_brief
```
Retorna pass/fail + detalhes de campos em falta ou invalidos.

## File I/O

### Read files
```
exec cat <path>
```
Usar para ler research_intake.json e research_batch_manifest.json.

### Write files
```
exec python -c "import json, pathlib; p=pathlib.Path(r'<path>'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(<dict>, indent=2, ensure_ascii=False), encoding='utf-8')"
```
Usar para criar brief JSON files e directories de target.
