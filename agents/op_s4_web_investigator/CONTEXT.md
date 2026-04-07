# CONTEXT.md

## Position in S4

Segundo operador do sector S4 (Asset Research).

Pipeline S4:
1. `op_s4_target_builder` — gera research_intake.json a partir de entities de S3
2. **`op_s4_web_investigator`** — gera target_research_brief.json por target (este operador)
3. `op_s4_target_research_worker` — executa discovery usando os briefs
4. `op_s4_candidate_evaluator` — avalia candidates encontrados
5. `op_s4_coverage_analyst` — analisa coverage do batch
6. `op_s4_pack_compiler` — compila pack final

## Data Flow

```
research_intake.json + research_batch_manifest.json
        |
        v
  op_s4_web_investigator (este operador)
        |
        v
  targets/<target_id>/<target_id>_brief.json  (um por target)
        |
        v
  op_s4_target_research_worker (consome briefs downstream)
```

## Key Relationships

- Recebe dispatch de `sm_s4_asset_research` (supervisor)
- Briefs sao consumidos por `op_s4_target_research_worker`
- Nao spawna nem dispatcha workers — o supervisor faz isso
- `op_s4_candidate_evaluator` pode ler briefs para entender intent durante qualification
