# Sapna Saathi

Sapna Saathi is a local hackathon demo. Scholarship records and eligibility rules are illustrative sample data. No government service is connected.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite server proxies `/api` to `http://127.0.0.1:8000`. Build the production frontend with `npm run build` from `frontend`.

## Backend

In another terminal, from the repository root:

```powershell
py -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
python -m pip install -r backend/requirements.txt
python -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The API stores demo profile and checklist progress in `backend/sapna_saathi.db` (created automatically and ignored by Git). `SAPNA_SAATHI_DB` can set a different SQLite file path. No authentication is implemented; this local demo stores only the profile fields used by the existing app. Do not enter identity numbers or bank account numbers.

## API

- `GET /api/health`
- `GET /api/opportunities`
- `POST /api/eligibility/check` with `{ "profile": { ... } }`
- `GET` / `PUT /api/profile/{student_id}`
- `GET` / `PUT /api/documents/{student_id}`

The frontend keeps its browser-local demo data and displays a fallback notice on the results page when the API is unavailable. Eligibility is determined by explicit deterministic demo rules in Python, not an AI model. Verify any real scholarship requirements with its official provider.
