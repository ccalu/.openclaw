# OPERATIONS.md

## Regras operacionais

1. Contexto limpo por activação.
2. Estado no disco > conversa.
3. Falha explícita > sucesso ambíguo.
4. Não inventar outputs inexistentes.
5. Não considerar um operator concluído apenas por resposta textual.

## Sequência base

1. Validar bootstrap.
2. Usar exactamente os paths declarados no bootstrap, sem reconstruí-los por heurística textual.
3. Escrever checkpoint de supervisor started.
4. Resolver activation plan.
5. Ler `operator_registry.md`.
6. Tratar o `operator_registry` como lista canónica e fechada dos operators desta fase.
7. Gerar payloads de dispatch compatíveis com `s3.operator_dispatch.v1`.
8. Se o activation plan marcar 4 operators activos, tentar os 4 — não cair silenciosamente para subset sem checkpoint explícito que justifique isso.
9. Invocar operators activos via `exec` com `openclaw agent --agent <operator_agent_id> --session-id <unique-run-operator-session> --message "..." --json --timeout 1800`.
10. Não fazer o trabalho semântico dos operators internamente como substituto do dispatch real.
11. Gerar um `session-id` único por run e por operator; não reutilizar a mesma sessão acumulada entre vídeos ou entre operators diferentes.
12. Usar timeout explícito de 1800 segundos nas chamadas aos operators; não depender do timeout implícito/default.
13. Não tentar ACP/sessions_spawn como caminho primário deste hop; se o launch real falhar, degradar/falhar explicitamente.
14. Monitorizar `status.json`, `checkpoint.json` e `output.json` por operator.
15. Validar outputs estruturais.
16. Não considerar outputs internos/paralelos (`locations`, `artifacts`, `atmosphere`, `era_context`, etc.) como substitutos dos outputs canónicos dos 4 operators.
17. Fazer retry selectivo quando permitido.
18. Compilar `compiled_entities.json`.
19. Gerar `s3_sector_report.md`.
20. Validar explicitamente que `compiled/compiled_entities.json` e `compiled/s3_sector_report.md` existem antes de fechar o sector.
21. Escrever checkpoint final do sector.
22. Espelhar obrigatoriamente o resultado macro em `b2_root/checkpoints/s3_completed.json` ou `b2_root/checkpoints/s3_failed.json`.

## Limites

- não és boundary Paperclip-facing
- não és o `b2_director`
- não deves delegar compile final para os operators
- não deves chamar operators fora do registry oficial
