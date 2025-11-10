from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import select
import json

from .models import PostInput, Audit
from .db import init_db, get_session
from .ingestion import fetch_and_clean
from .analysis.rules import heuristics
from .analysis.rewrite import anti_clickbait_title, anti_clickbait_desc, inform_block

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
    # Bloc try/except pour erreurs propres
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
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>FB Integrity — Audit</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" />
<style>
  .container { max-width: 980px; margin: 2rem auto; }
  pre { white-space: pre-wrap; }
  .grid { grid-gap: 1rem; }
  .score { font-weight: 700; }
  .badge { display:inline-block; padding:.25rem .5rem; border-radius:.5rem; background:#e9ecef; }
  .ok { background:#d1fae5; }
  .warn { background:#fef3c7; }
  .danger { background:#fee2e2; }
</style>
</head>
<body>
<main class="container">
  <hgroup>
    <h1>FB Integrity — Audit</h1>
    <p>Évalue et corrige ton post avant publication. Simple et efficace.</p>
  </hgroup>

  <form onsubmit="analyze();return false;">
    <div class="grid">
      <label>Titre
        <input id="title" required placeholder="Titre de ton post" />
      </label>
      <label>Liens (séparés par virgules)
        <input id="links" placeholder="https://exemple.com, https://..." />
      </label>
    </div>
    <label>Description
      <textarea id="desc" rows="3" placeholder="Texte du post"></textarea>
    </label>
    <div class="grid">
      <button type="submit">Analyser</button>
      <a role="button" href="/history" target="_blank">Historique (JSON)</a>
    </div>
  </form>

  <article id="panel" style="display:none">
    <h3>Résumé</h3>
    <p id="overall"></p>
    <ul id="scores"></ul>

    <h3>Propositions</h3>
    <p><strong>Titre :</strong> <span id="fixTitle"></span></p>
    <p><strong>Description :</strong> <span id="fixDesc"></span></p>
    <p><strong>Contexte / INFORM :</strong><br><code id="inform"></code></p>

    <details>
      <summary>Détails JSON</summary>
      <pre id="json"></pre>
    </details>
  </article>
</main>

<script>
function badge(level, text){
  const cls = level === 'ok' ? 'badge ok' : level === 'warn' ? 'badge warn' : 'badge danger';
  return `<span class="${cls}">${text}</span>`;
}
function statusFromScores(remove, reduce){
  if (remove >= 0.5) return {level:'danger', label:'Risque de retrait (REMOVE élevé)'};
  if (reduce >= 0.5) return {level:'warn', label:'Risque de baisse de portée (REDUCE élevé)'};
  return {level:'ok', label:'OK (faible risque)'};
}
async function analyze(){
  const title = document.getElementById('title').value.trim();
  const description = document.getElementById('desc').value.trim();
  const links = (document.getElementById('links').value||'').split(',').map(s=>s.trim()).filter(Boolean);

  let res;
  try {
    res = await fetch('/analyze', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ platform:'facebook', title, description, transcript:'', links })
    });
  } catch(e){
    alert("Erreur réseau: " + e.message);
    return;
  }
  let data;
  try { data = await res.json(); } catch(e){ alert("Réponse invalide"); return; }

  if(!res.ok){
    alert((data && data.detail) ? data.detail : "Erreur d'analyse");
    return;
  }

  const rr = (data.scores?.risk_remove ?? 0);
  const rd = (data.scores?.risk_reduce ?? 0);
  const overall = statusFromScores(rr, rd);

  document.getElementById('panel').style.display = 'block';
  document.getElementById('overall').innerHTML = badge(overall.level, overall.label);
  document.getElementById('scores').innerHTML = `
    <li>Risque <b>REMOVE</b> : ${(rr*100).toFixed(0)}%</li>
    <li>Risque <b>REDUCE</b> : ${(rd*100).toFixed(0)}%</li>
    <li>INFORM requis : ${data.actions?.needs_inform ? 'Oui' : 'Non'}</li>
  `;
  document.getElementById('fixTitle').textContent = data.fixes?.title || '';
  document.getElementById('fixDesc').textContent = data.fixes?.description || '';
  document.getElementById('inform').textContent = data.actions?.inform_block || '';
  document.getElementById('json').textContent = JSON.stringify(data, null, 2);
}
</script>
</body>
</html>
"""
