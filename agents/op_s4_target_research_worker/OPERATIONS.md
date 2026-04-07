# OPERATIONS.md

## Sequencia de execucao

1. **Parse dispatch** — extrair brief_path e sector_root da mensagem de ativacao
2. **Validar brief** — verificar que o arquivo em brief_path existe no disco
3. **Executar helper** —
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\research_worker.py" <brief_path> <sector_root>
   ```
4. **Verificar output** — confirmar que candidate_set.json foi criado no diretorio do target
5. **Validar schema** —
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <candidate_set_path> candidate_set
   ```
6. **Reportar** — numero de candidates encontrados, schema valido, file path do artifact

## Regras

- Retrieval provenance deve ser via helper real (Brave/Firecrawl), nao imaginacao LLM
- Zero candidates e aceitavel — reportar com warning
- Nao tentar melhorar/refazer search se helper retornou resultados — aceitar output do helper
- Nao reclassificar candidates — isso e trabalho do evaluator
- Se helper falhar (exit code != 0), reportar erro com stderr
- Se brief nao existir no disco, reportar erro imediatamente sem executar helper
