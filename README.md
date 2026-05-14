# Ethiopia Job Portal

Production-oriented monorepo for a **job marketplace tailored to Ethiopia**: ETB salaries, **English + Amharic** UI, **Africa/Addis_Ababa (UTC+3)** semantics, mobile-first frontend, JWT auth with refresh tokens, PostgreSQL, Redis caching, CV parsing (PDF/DOCX) with TF–IDF matching, job alerts (email/SMS hooks), and payment stubs for **Chapa / Telebirr**.

## Architecture

| Layer | Stack |
|--------|--------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, **next-intl** (`en`, `am`) |
| Backend | FastAPI, SQLAlchemy 2, Pydantic v2, **scikit-learn** TF–IDF cosine similarity |
| Data | PostgreSQL, Redis (job list cache + rate limiting support) |
| Files | Local disk (dev) or S3 (env-driven) |
| Containers | Docker Compose: Postgres, Redis, API, Web |

```
├── backend/          # FastAPI app (`app/`), tests, Dockerfile
├── frontend/         # Next.js app, Dockerfile
├── packages/
│   └── shared-types/ # Optional shared TypeScript types (`JobOut`, etc.)
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml
```

## Quick start (Docker)

1. Copy environment file:

   ```bash
   cp .env.example .env
   ```

2. Adjust secrets in `.env` (JWT secrets, DB password, optional Google/SendGrid/SMS keys).

3. Start stack:

   ```bash
   docker compose up --build
   ```

4. **Seed** sample data (Ethiopian cities list, categories, employer + jobs, demo users):

   ```bash
   docker compose exec api python -m app.seed
   ```

5. Open **http://localhost:3000/en** (Next.js) and **http://localhost:8000/docs** (OpenAPI).

### Demo accounts (after seed)

| Role | Email | Password |
|------|--------|----------|
| Admin | `admin@ethiojobs.et` | `Admin12345!` |
| Employer | `employer@ethiojobs.et` | `Employer123!` |
| Seeker | `seeker@ethiojobs.et` | `Seeker123!` |

## Local development (without Docker)

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Set DATABASE_URL, REDIS_URL, JWT_* in .env or environment
uvicorn app.main:app --reload --port 8000
python -m app.seed
```

**Frontend**

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## Ethiopian-specific behavior (documented in code)

- **ETB**: salary fields are integers in Birr; frontend formats with `Intl.NumberFormat(..., { currency: "ETB" })`.
- **Locales**: `preferred_locale` on users (`en`, `am`, room for `om`, etc.); job posts support `title_am` / `description_am` for Amharic listings.
- **Timezone**: configure `TZ=Africa/Addis_Ababa` in deployment; optional Ethiopian calendar can be layered in the UI (Gregorian used by default).
- **SMS**: Africa’s Talking hooks in `app/services/notifications.py` (`+251…` normalization in job alerts).
- **Payments**: `POST /api/v1/payments/init` returns a **stub** checkout URL — replace with [Chapa](https://developer.chapa.co/) or Telebirr SDKs and a signed webhook to flip `is_premium` on `Job`.

## API overview (`/api/v1`)

| Method | Path | Description |
|--------|------|----------------|
| POST | `/auth/register` | Register seeker or employer |
| POST | `/auth/login` | Email or phone + password |
| POST | `/auth/google` | Verify Google `id_token` |
| POST | `/auth/refresh` | Rotate refresh token |
| GET | `/auth/me` | Current user |
| GET | `/jobs` | Public search (filters, Redis cache) |
| GET | `/jobs/{id}` | Job detail + view analytics |
| POST | `/jobs/{id}/apply` | Seeker one-click apply |
| GET/PATCH | `/seeker/profile` | Profile, skills, education, experience |
| POST | `/seeker/resume` | Upload PDF/DOCX (max 5MB) + parse |
| GET | `/seeker/applications` | Application status |
| POST/GET | `/seeker/job-alerts` | Saved search alerts |
| GET/PATCH | `/employer/company` | Company profile |
| POST/GET/PATCH | `/employer/jobs` | CRUD jobs |
| GET | `/employer/jobs/{id}/applicants` | Ranked applicants (TF–IDF batch) |
| PATCH | `/employer/applications/{id}` | Update status (shortlist/reject/hired) |
| POST | `/employer/messages` | Message candidate |
| GET | `/employer/jobs/{id}/analytics` | Views, applications, conversion |
| GET/PATCH | `/admin/users`, `/admin/jobs` | Admin oversight |
| POST | `/payments/init` | Premium placement stub |
| POST | `/payments/chapa/webhook` | Webhook stub (verify signature in prod) |

Full interactive docs: `/docs` when the API is running.

## CV parsing and matching

- **Parsing**: `pypdf` + `python-docx` extract text; heuristics for skills/sections; optional `CV_PARSER_MODE=spacy` (requires `spacy` + `en_core_web_sm`); optional `AFFINDA_API_KEY` stub hook.
- **Matching**: `sklearn.feature_extraction.text.TfidfVectorizer` + cosine similarity (`app/services/matching.py`). For **10k+ resumes**, precompute a **job-level vector**, store sparse vectors or Redis cache keys (`jobvec:{id}` pattern in code comments), and batch-transform candidates per request.

## Security

- JWT access + refresh (hashed refresh tokens in DB).
- **slowapi** rate limiting (default per-IP).
- Upload size + MIME/extension checks; optional **ClamAV** via `CLAMAV_SOCKET` + `python-clamd`.
- HTTPS, reverse proxy hardening, and secret rotation are deployment concerns (see below).

## Testing

```bash
cd backend
pytest tests/ -v
```

Tests default to **in-memory SQLite** via `tests/conftest.py` so CI does not require Postgres.

## Deployment (AWS EC2 / EthioCloud / VPS)

1. Build and push images or `git pull` on the server.
2. Run `docker compose` (or Swarm/Kubernetes) with managed PostgreSQL and Redis.
3. Put **Traefik** or **Caddy** in front for TLS (Let’s Encrypt).
4. Set `STORAGE_BACKEND=s3` and AWS credentials for resumes.
5. Run **Alembic** migrations for production schema evolution (template uses `create_all` on startup for simplicity—replace with migrations before real production traffic).
6. Add a **worker** (Celery/RQ) for alert fan-out and heavy CV batch reindexing.

## Scaling checklist

- [ ] Separate read replicas for job search.
- [ ] Redis for session/rate limit + job vector cache.
- [ ] Object storage CDN for static assets.
- [ ] Background workers for email/SMS and Chapa webhooks.

## License

Use and modify for your product; attribution appreciated.
