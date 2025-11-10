# Facebook Content Integrity Pipeline — Starter (Option 5: Pipeline Pro)

Ce starter implémente un **pipeline scalable** basé sur FastAPI + SQLite, avec:
- **Ingestion**: URL → HTML → texte nettoyé (BeautifulSoup) OU input direct (titre/desc/transcript).
- **Analyse**: règles Remove/Reduce/Inform (heuristiques) + *hook* LLM optionnel.
- **Réécriture**: titres/desc anti-clickbait + cartouche INFORM.
- **Sorties**: JSON REST API, stockage SQLite (audit log).
- **UI**: mini page HTMX pour tester rapidement.

## ⚙️ Installation rapide
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```
Ouvre: http://127.0.0.1:8000

## 🧪 Endpoints
- `GET /health` → ping
- `POST /analyze` → analyse un post
- `POST /ingest` → récupère et nettoie le texte d'une URL
- `GET /history` → derniers audits (JSON)
- `GET /ui` → petite interface de test

## 📦 Exemple de payload
```json
{
  "platform": "facebook",
  "title": "Tu ne devineras JAMAIS ce secret…",
  "description": "Commente OUI si tu veux la suite!",
  "transcript": "",
  "links": ["https://exemple.com/article"]
}
```

## 🏗️ Étendre
- Remplace `analysis/llm.py` par tes appels LLM (OpenAI, etc.).
- Branche une extension Chrome (content script) pour appeler `/analyze`.
- Ajoute des règles/regex spécifiques à ton domaine.

Bonne construction! 🚀
