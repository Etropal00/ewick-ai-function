from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .models import PostInput, Audit
from .db import init_db, get_session
from .ingestion import fetch_and_clean
from .analysis.rules import heuristics
from .analysis.rewrite import anti_clickbait_title, anti_clickbait_desc, inform_block
from sqlmodel import select
import json

app = FastAPI(title="FB Integrity Pipeline")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

class IngestReq(BaseModel):
    url: str

@app.post("/ingest")
def ingest(req: IngestReq):
    return fetch_and_clean(req.url)

@app.post("/analyze")
def analyze(inp: PostInput):
    try:
        h = heuristics(inp.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analyse échouée: {e}")

    fixes = {
        "title": anti_clickbait_title(inp.title),
        "description": anti_clickbait_desc(inp.description),
        "notes": []
    }
    actions = h["actions"]
    actions["inform_block"] = inform_block(actions["needs_inform"], inp.links)

    out = {
        "signals": h["signals"],
        "scores": h["scores"],
        "actions": actions,
        "fixes": fixes,
        "audit": {
            "policy_framework": "remove_reduce_inform",
            "model_version": "starter-v1"
        }
    }

    with get_session() as s:
        audit = Audit(
            platform=inp.platform,
            input_json=json.dumps(inp.model_dump(), ensure_ascii=False),
            output_json=json.dumps(out, ensure_ascii=False)
        )
        s.add(audit)
        s.commit()
    return out

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FB Integrity UI</title>
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>
  body { font-family: system-ui, sans-serif; max-width: 900px; margin: 30px auto; }
  .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin: 10px 0; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .btn { padding: 8px 12px; border-radius: 8px; border: 1px solid #333; background:#f7f7f7; cursor:pointer;}
  pre { white-space: pre-wrap; }
</style>
</head>
<body>
  <h1>Facebook Integrity — Analyse</h1>
  <div class="card">
    <div class="row">
      <label>Titre<br><input id="title" style="width:100%"></label>
      <label>Liens (séparés par virgule)<br><input id="links" style="width:100%"></label>
    </div>
    <label>Description<br><textarea id="desc" rows="4" style="width:100%"></textarea></label>
    <div class="row">
      <button class="btn" onclick="analyze()">Analyser</button>
      <a class="btn" href="/history" target="_blank">Voir l'historique (JSON)</a>
    </div>
  </div>
  <div id="result"></div>

<script>
async function analyze(){
  const title = document.getElementById('title').value;
  const description = document.getElementById('desc').value;
  const links = (document.getElementById('links').value || '').split(',').map(s=>s.trim()).filter(Boolean);
  const payload = { platform: "facebook", title, description, transcript: "", links };
  const res = await fetch('/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  if(!res.ok){
    const err = await res.json().catch(()=>({detail:'Erreur inconnue'}));
    document.getElementById('result').innerHTML = `<div class="card"><b>Erreur:</b> ${err.detail||res.status}</div>`;
    return;
  }
  const data = await res.json();
  document.getElementById('result').innerHTML = `<div class="card"><h3>Résultat</h3><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
}
</script>
</body>
</html>
"""
