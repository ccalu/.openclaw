# Useful external references

## 1) OpenClaw Skills docs
- URL: https://docs.openclaw.ai/tools/skills
- Why useful:
  - confirms skills are AgentSkills-compatible
  - confirms workspace vs shared skill loading model
  - supports the idea of creating B1-specific local skills like `scene-bible-schema` and `preproduction-validation`

## 2) OpenClaw skills docs mirror on GitHub
- URL: https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md
- Why useful:
  - similar content, easier to reference when docs site changes
  - reinforces skill precedence and per-agent workspace model

## 3) OpenClaw `skill-creator` example
- URL: https://github.com/openclaw/openclaw/blob/main/skills/skill-creator/SKILL.md
- Why useful:
  - useful example of how a strong SKILL.md is written
  - important for authoring internal B1 skills with minimal token waste and clear trigger conditions

## 4) Practical structured output / JSON schema reminder
- URL: https://blog.promptlayer.com/how-json-schema-works-for-structured-outputs-and-tool-integration/
- Why useful:
  - not OpenClaw-specific, but reinforces a key B1 point: use strict structured outputs for `scene_bible.json`
  - relevant because B1’s real product is a stable contract artifact, not freeform text

## Notes on external research quality
- The OpenClaw docs are the strongest external source used.
- The structured-output article is only a supporting reference, not a source of project truth.
- I did not use external sources to redefine the local architecture; I only used them to validate practical implementation choices around skills and structured artifacts.
