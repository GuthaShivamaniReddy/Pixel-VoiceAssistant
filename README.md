# Pixel — Cyber Florida AI Voice Assistant

**Current status: Phase 9 complete (product quality and frontend polish)**

Pixel answers organization-specific questions from an approved source registry with retrieval, grounding, citations, and abstention. It can offer approved Cyber Florida Open links via server-side tools. Local default providers may still be `mock` unless `OPENAI_API_KEY` is configured.

Do not treat this as a production assistant.

---

## What Pixel will be

Pixel is Cyber Florida’s planned voice and conversational interface: a trustworthy AI assistant that listens, understands, retrieves **approved** Cyber Florida information, reasons within defined boundaries, speaks naturally, and guides users to the correct next step.

It is **not** a generic chatbot with a microphone and **not** an offensive-security agent.

---

## Repository layout

```text
apps/web          Next.js conversation UX
apps/api          FastAPI health, sessions, turns, realtime voice
apps/worker       Ingestion worker (`pixel-worker ingest` indexes the fixture corpus)
packages/pixel    Orchestrator, knowledge/RAG, domain models, provider adapters
infra/            Docker Compose, Dockerfiles, Postgres init
evals/            Policy, safety, and knowledge evaluation datasets
docs/             Product, policy, architecture
```

---

## Prerequisites

- Node.js 20+
- Python 3.12+ (3.12 recommended; CI uses 3.12)
- Docker Desktop running (for Postgres/pgvector and optional full stack)

---

## Configure

```bash
copy .env.example .env
```

On macOS/Linux: `cp .env.example .env`

`.env.example` contains **local placeholders only**. Never put real API keys in git.

Environment templates:

| File | Use |
|---|---|
| `.env.example` | Local default |
| `.env.development.example` | Shared development-shaped values |
| `.env.staging.example` | Staging-shaped values (fake hosts) |
| `.env.production.example` | Production-shaped values (fake hosts, mocks off) |

---

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

npm install
```

---

## Start

Postgres + pgvector (required for `/ready` with a database):

```bash
docker compose -f infra/docker-compose.yml up db -d
```

API:

```bash
python -m uvicorn pixel_api.main:app --host 127.0.0.1 --port 8000
```

Or: `python -m pixel_api.main` / `pixel-api`

Web (another terminal):

```bash
npm run web:dev
```

Optional full stack:

```bash
docker compose -f infra/docker-compose.yml up --build
```

- Web: http://localhost:3000
- API health: http://127.0.0.1:8000/health
- API ready: http://127.0.0.1:8000/ready

Worker stub:

```bash
pixel-worker
```

---

## Quality checks

```bash
ruff format apps/api apps/worker packages/pixel
ruff format --check apps/api apps/worker packages/pixel
ruff check apps/api apps/worker packages/pixel
pyright
pytest

npm run web:format:check
npm run web:lint
npm run web:typecheck
npm run web:test
npm run web:e2e
npm run web:build
```

Dependency scans:

```bash
pip-audit
npm audit --audit-level=high
```

---

## Security notes

- Provider secrets stay on the server. Do not add `NEXT_PUBLIC_*` keys, tokens, or passwords.
- Admin routes return **403** until real authentication exists (`ADMIN_ENABLED` defaults false).
- CORS is an explicit origin list, not `*`.
- Production settings must not use mock LLM/STT/TTS providers.

See [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md) and [docs/security/](docs/security/). Conversation UX notes: [docs/conversation-ux.md](docs/conversation-ux.md).

---

## Documentation

Start at [docs/README.md](docs/README.md). Behavior contract: [docs/policies.md](docs/policies.md).

---

## Phase status

| Phase | Status |
|---|---|
| 0 Product discovery | Complete (docs) |
| 1 Identity and safety policy | Complete (docs) |
| 2 Engineering foundation | Complete |
| 3 Conversation UX prototype | Complete |
| 4 End-to-end voice loop | Complete — see [docs/voice.md](docs/voice.md) |
| 5 AI orchestrator | Complete — see [docs/orchestrator.md](docs/orchestrator.md) |
| 6 Knowledge / RAG | Complete — see [docs/knowledge.md](docs/knowledge.md) |
| 7 Tools and navigation | Complete — see [docs/tools.md](docs/tools.md) |
| 8 Security, privacy, abuse resistance | Complete — see [docs/security/](docs/security/) |
| 9 Product quality and frontend polish | Complete — see [docs/conversation-ux.md](docs/conversation-ux.md) |
| 10+ Observability through production | Not started |

---

## Source notes

Cyber Florida context is based on public [Cyber Florida](https://cyberflorida.org/) information. Hosting, SSO, and paid vendors are not chosen in this repository.
