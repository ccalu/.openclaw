# OPERATIONS.md

1. Ler dispatch do disco.
2. Confirmar que `operator_name = environment_location_extractor`.
3. Ler source package.
4. Extrair lugares, settings e ambientes com relevância visual.
5. Normalizar o output final para o schema canónico `s3.environment_location.output.v1`.
6. O JSON final deve incluir obrigatoriamente:
   - `contract_version = s3.environment_location.output.v1`
   - `operator_name = environment_location_extractor`
   - `job_id`
   - `status = completed | failed`
   - `entities[]`
   - `generated_at`
7. Se quiseres preservar estruturas intermédias como `locations`, `environments`, `settings` ou `scene_coverage`, elas só podem existir como campos auxiliares adicionais; nunca substituem `entities[]`.
8. Escrever output final no path pedido.
9. Em caso de falha, registar falha explícita.
