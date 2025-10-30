# Resume Screener API

FastAPI-based backend to upload resumes (PDF/DOCX/TXT), extract key fields, and store data in PostgreSQL. Includes JWT auth.

## Local Setup

1. Create and activate a virtualenv (optional), then install dependencies:

```bash
pip install -r requirements.txt
```

- Optional (for spaCy NER): Installing spaCy on Windows with Python 3.13 may require build tools. For best compatibility, use Python 3.12 and then:
```bash
pip install spacy==3.7.5
python -m spacy download en_core_web_sm
```

2. Start PostgreSQL locally and create a database `resume_screener`. Default connection string (psycopg v3):

```
postgresql+psycopg://postgres:postgres@localhost:5432/resume_screener
```

Override via environment variable `DATABASE_URL`.

3. Run the API:

```bash
uvicorn app.main:app --reload
```

4. Seed an HR user and obtain a JWT token:

- Seed: `POST /auth/seed_hr`
- Login: `POST /auth/login` with form fields `username=hr@example.com`, `password=password`.

5. Upload a resume:

`POST /upload_resume` with Bearer token. Use form-data `file` as the upload.

## Notes

- If spaCy is not installed, the app falls back to heuristic extraction (regex/keyword) for name and skills.
- PDF parsing uses `pdfplumber`.

## Project Layout

- `app/main.py` – app factory and router registration
- `app/routes/` – API routes (auth, resumes)
- `app/models/` – database setup and ORM entities
- `app/utils/` – parsing and NLP helpers

## Next Steps

- Add endpoints for job description storage and results scoring
- Add docker and docker-compose for local Postgres + API 