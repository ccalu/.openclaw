# OPERATIONS.md

1. Ler dispatch do disco.
2. Confirmar que `operator_name = symbolic_event_extractor`.
3. Ler source package.
4. Extrair símbolos, eventos, fenómenos e elementos atmosféricos relevantes.
5. Normalizar o output final para o schema canónico `s3.symbolic_event.output.v1`.
6. O JSON final deve incluir obrigatoriamente:
   - `contract_version = s3.symbolic_event.output.v1`
   - `operator_name = symbolic_event_extractor`
   - `job_id`
   - `status = completed | failed`
   - `entities[]`
   - `generated_at`
7. Se quiseres preservar estruturas intermédias como `symbolic_events` ou `scene_coverage`, elas só podem existir como campos auxiliares adicionais; nunca substituem `entities[]`.
8. Registar scene_ids, grau de literalidade e nota de tradução visual em `entities[]`.
9. Escrever output final no path pedido.
10. Em caso de falha, registar falha explícita.
