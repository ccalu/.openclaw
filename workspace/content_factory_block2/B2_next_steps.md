# B2 — Next Implementation Steps After Runtime Wiring

## Estado
A ligação conceptual mínima `b2_director -> S3 -> reentrada -> b2_completed/b2_failed` já ficou fechada documentalmente.

## Próximo passo exacto
Implementar a camada mecânica mínima que falta para o primeiro dry run estrutural:

1. helper leve de estado do B2
   - criar/escrever `b2_state.json`
   - criar checkpoints macro do bloco

2. gerador de bootstrap do S3 a partir do B2
   - criar `s3_source_package.json`
   - criar payload `s3.supervisor_bootstrap.v1`

3. contrato operacional do supervisor para espelhar checkpoints no `b2_root`
   - `s3_completed.json`
   - `s3_failed.json`

4. script de dry run estrutural
   - simular bootstrap do B2
   - simular outputs mínimos do S3
   - provar compile + report + fecho do bloco

## Regra
Não abrir S4/S5/S6 antes deste loop mínimo estar provado.
