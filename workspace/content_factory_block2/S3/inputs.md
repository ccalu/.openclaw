# S3 — Inputs

## Objectivo

Este documento define a proposta inicial e simplificada de input para o Setor 3 (S3 — Visual Planning) do novo Bloco 2.

Nesta primeira fase, o S3 não depende de `scene_bible.json` novo nem de contratos mais complexos. O sector parte apenas dos artefactos reais já existentes hoje no Content Factory V3, especialmente:

- `screenplay_analysis.json`
- `01_script_fetched.json`

A ideia é que o supervisor do S3 normalize estes artefactos e gere um pacote-base único que possa ser entregue aos operadores do sector.

---

## Princípio desta versão

Para não complicar demasiado o arranque do S3, todos os operadores podem receber o mesmo input-base simplificado, com:

- contexto geral do vídeo
- visão resumida da escala do script
- lista completa das cenas já divididas

Isto dá aos identificadores visão global suficiente do vídeo sem depender ainda de um `scene_bible` novo.

---

## Estrutura proposta do input-base

```json
{
  "video_context": {
    "video_name": "...",
    "title": "...",
    "description": "...",
    "account_id": "006",
    "language": "pt"
  },
  "script_overview": {
    "full_word_count": 3599,
    "total_scenes": 91,
    "source_row": 61
  },
  "scenes": [
    {
      "scene_number": 1,
      "text": "..."
    }
  ]
}
```

---

## Significado de cada bloco

### `video_context`

Contexto geral do vídeo.

Campos actuais:

- `video_name` — slug/nome operacional do vídeo
- `title` — título do vídeo
- `description` — descrição do vídeo
- `account_id` — conta/canal de origem
- `language` — idioma do vídeo

Este bloco ajuda os operadores a entender o enquadramento global do conteúdo.

---

### `script_overview`

Resumo estrutural do conteúdo.

Campos actuais:

- `full_word_count` — total de palavras do script original
- `total_scenes` — número total de cenas no `screenplay_analysis.json`
- `source_row` — linha de origem no Google Sheets, quando existir

Este bloco dá noção da escala do vídeo sem obrigar os operadores a lerem metadata bruta do V3.

---

### `scenes`

Lista completa das cenas já divididas pelo Bloco 1.

Nesta proposta simplificada, cada cena contém apenas:

- `scene_number`
- `text`

Isto permite que os identificadores do S3:

- vejam o vídeo inteiro como sequência de cenas
- raciocinem com contexto global
- devolvam resultados ancorados por cena

---

## Decisão actual

Nesta fase inicial:

- não usar ainda `scene_bible.json` novo como dependência do S3
- não complicar o input com campos adicionais por cena
- não criar variações diferentes de input por operador no primeiro momento
- usar um único pacote-base simples para todos os identificadores

Mais tarde, se necessário, o supervisor do S3 poderá derivar views especializadas para cada operador. Mas isso não faz parte desta primeira definição.

---

## Fonte esperada dos dados

O supervisor do S3 deve montar este input-base a partir de artefactos já existentes no CFV3:

- `checkpoints/01_script_fetched.json`
- `screenplay_analysis.json`

Mapeamento esperado:

- `video_context.title` ← `01_script_fetched.json.data.title`
- `video_context.description` ← `01_script_fetched.json.data.description`
- `video_context.video_name` ← `01_script_fetched.json.video_name` ou equivalente do job
- `video_context.account_id` ← contexto do job/pipeline
- `video_context.language` ← `screenplay_analysis.json.language` ou contexto do job
- `script_overview.full_word_count` ← `01_script_fetched.json.data.words`
- `script_overview.total_scenes` ← `screenplay_analysis.json.total_scenes`
- `script_overview.source_row` ← `01_script_fetched.json.data.row_number`
- `scenes[]` ← `screenplay_analysis.json.scenes[]`

---

## Estado desta definição

**Status:** v1 simplificada

Esta é a primeira proposta operacional do input do S3 e serve como base para começar a estruturar o sector no OpenClaw sem overengineering prematuro.
