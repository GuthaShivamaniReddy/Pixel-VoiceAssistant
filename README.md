# Pixel — Cyber Florida AI Voice Assistant

**Current status: Planning (Phase 0–1 documentation)**

Pixel is not a running assistant. This repository holds the project specification, Phase 0 constraints, and a target architecture. There is no voice input, speech-to-text, AI conversation, RAG, text-to-speech, tests, or production build.

Do not treat documentation as a working product.

---

## What Pixel will be

Pixel is Cyber Florida’s planned voice and conversational interface: a trustworthy AI assistant that listens, understands, retrieves **approved** Cyber Florida information, reasons within defined boundaries, speaks naturally, and guides users to the correct next step.

Specialization:

- Cyber Florida information, programs, training, workforce resources, research, and events
- Cybersecurity education and awareness
- Phishing / scam awareness
- Defensive cybersecurity guidance

It is **not** a generic chatbot with a microphone and **not** an offensive-security agent.

Target experience (future):

Voice input → Speech-to-Text → AI reasoning → RAG / tools → Grounded response → Text-to-Speech → conversation  

Text is a full fallback.

---

## What exists today (verified)

| Item | Status |
|---|---|
| Application code (`apps/`, packages) | **None** |
| Database, APIs, providers | **None** |
| Tests, CI, containers | **None** |
| Secrets / API keys in repo | **None found** |
| Project guide PDF | Present |
| Phase 0 product + policy + architecture docs | Present under `docs/` |

Gap analysis: [docs/GAP_ANALYSIS.md](docs/GAP_ANALYSIS.md).

---

## Documentation

Start here: [docs/README.md](docs/README.md).

Required core set:

| Document | Contents |
|---|---|
| [docs/product.md](docs/product.md) | Vision, users, MVP, ownership, sources, retention |
| [docs/policies.md](docs/policies.md) | Behavior contract v1.1.0 |
| [docs/conversation-examples.md](docs/conversation-examples.md) | 102 example dialogues |
| [docs/architecture.md](docs/architecture.md) | Target architecture (unimplemented) |
| [docs/risk-register.md](docs/risk-register.md) | Risks, assumptions, spec conflicts |
| [docs/decisions/](docs/decisions/) | ADRs |
| [docs/runbooks/](docs/runbooks/) | Operational templates |
| [docs/testing/](docs/testing/) | Test strategy |
| [docs/security/](docs/security/) | Threat model |
| [docs/evaluations/](docs/evaluations/) | Eval placeholders |

---

## Planned stack (not installed)

Recorded in `docs/architecture.md` and `docs/decisions/`:

- **Web:** Next.js, React, TypeScript
- **API:** Python FastAPI
- **Data:** PostgreSQL + pgvector
- **Voice transport (MVP):** WebSocket + push-to-talk (WebRTC later if measured)
- **Providers:** adapters for LLM, STT, TTS, embeddings, vector store
- **Local default:** mock providers; no committed secrets

---

## Local development

Not applicable. There is no application to install or run.

**Never commit API keys.**

---

## Development rules

- Follow [docs/ROADMAP.md](docs/ROADMAP.md). Do not skip foundation, security, or evaluation for a demo.
- Retrieved knowledge is untrusted and must not override [docs/policies.md](docs/policies.md).
- Do not claim a feature works unless it is implemented and tested.
- Do not automatically start the next phase after finishing one.

---

## Phase status

| Phase | Name | Status |
|---|---|---|
| 0 | Product discovery and constraints | **Complete (docs)** |
| 1 | Identity, conversation policy, and safety rules | **Complete (docs)** |
| 2+ | Engineering foundation through production | **Not started** |

---

## Source notes

Cyber Florida context is based on public Cyber Florida at USF information. Stack and security recommendations still require Cyber Florida / USF technology, security, procurement, accessibility, and privacy validation before production.

- [Cyber Florida](https://cyberflorida.org/)
