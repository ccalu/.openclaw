# TOOLS.md

## research_worker.py
Executa web discovery real para um target. Brave Search como primario, Firecrawl como fallback.
```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\research_worker.py" <brief_path> <sector_root>
```
- Input: path do brief JSON, path do sector root
- Output: candidate_set.json no diretorio do target
- Exit code 0 = sucesso

## schema_validator.py
Valida schema de um artifact JSON contra o schema esperado.
```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <path> candidate_set
```
- Input: path do JSON, nome do schema (candidate_set)
- Output: stdout com resultado de validacao
- Exit code 0 = schema valido
