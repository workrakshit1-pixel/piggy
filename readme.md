# Piggy — AI Expense Assistant (FastAPI + SQLite)

Piggy is a small assistant that tracks expenses. Use natural commands via `/api/assistant` or the REST endpoints.

## Features
- Add / Delete / List expenses
- Natural language assistant endpoint (simple local parser)
- Optional OpenAI integration for more human replies (disabled by default)
- Built with FastAPI + SQLAlchemy + SQLite (or any DB via `DATABASE_URL`)

## Install

```bash
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
