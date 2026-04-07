import json
from pathlib import Path
from datetime import datetime, timezone
base = Path(r"C:\Users\User-OEM\.openclaw\workspace\content_factory_block2")
run = base / "runtime_realcheck" / "run_009"
(run / "upstream").mkdir(parents=True, exist_ok=True)
screenplay = {
  "video_context": {"title": "Supervisor Exec Run 009"},
  "script_overview": {"summary": "Fresh activation proof for exec + openclaw agent"},
  "scenes": [
    {"scene_id": "scene_001", "title": "Opening", "summary": "Luís XIV walks through Versailles as courtiers watch."},
    {"scene_id": "scene_002", "title": "Ceremony", "summary": "Madame de Maintenon accompanies the king in a private ceremony."},
    {"scene_id": "scene_003", "title": "Aftermath", "summary": "Nobles debate the future of France after the king dies."}
  ]
}
script_fetched = {
  "event": "01_script_fetched",
  "video_name": "a_queda_do_rei_sol",
  "title": "A Queda do Rei Sol",
  "description": "Resumo histórico sobre o fim do reinado de Luís XIV e a decadência da corte.",
  "account_id": "006",
  "language": "pt-BR",
  "source_row": 61,
  "fetched_at": datetime.now(timezone.utc).isoformat()
}
b2_bootstrap = {
  "kind": "b2_start",
  "contract_version": "b2.bootstrap.v1",
  "job_id": "realrun_supervisor_exec_009",
  "run_root": str(run),
  "b2_root": str(run / "b2"),
  "account_id": "006",
  "language": "pt-BR",
  "inputs": {"screenplay_analysis_path": str(run / "upstream" / "screenplay_analysis.json")},
  "mode": "s3_only"
}
(run / "upstream" / "screenplay_analysis.json").write_text(json.dumps(screenplay, ensure_ascii=False, indent=2), encoding="utf-8")
(run / "upstream" / "01_script_fetched.json").write_text(json.dumps(script_fetched, ensure_ascii=False, indent=2), encoding="utf-8")
(run / "b2_bootstrap.json").write_text(json.dumps(b2_bootstrap, ensure_ascii=False, indent=2), encoding="utf-8")
