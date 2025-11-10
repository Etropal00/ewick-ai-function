@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  echo [*] Creation venv...
  "%LocalAppData%\Python\pythoncore-3.12-64\python.exe" -m venv .venv || (echo [X] Python 3.12 introuvable & pause & exit /b 1)
)
call .\.venv\Scripts\activate

echo [*] Upgrade pip + install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [*] Launching on http://127.0.0.1:8000
python -m uvicorn app.api:app --reload
