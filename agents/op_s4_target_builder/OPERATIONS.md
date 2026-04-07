# OPERATIONS.md

## Sequencia

1. Parse activation message para: compiled_entities_path, sector_root, job_id, video_id, account_id, language.
2. Validar que compiled_entities_path existe no disco.
3. Executar helper:
   `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\target_builder.py" <compiled_entities_path> <sector_root> <job_id> <video_id> <account_id> <language>`
4. Validar que intake existe: `<sector_root>/intake/research_intake.json`
5. Validar que report existe: `<sector_root>/intake/target_builder_report.md`
6. Reportar resultado baseado em artifacts no disco.

## Regras

- Estado no disco > conversa.
- Falha explicita > sucesso ambiguo.
- Nao inventar outputs inexistentes.
- Nao considerar concluido apenas por resposta textual.
