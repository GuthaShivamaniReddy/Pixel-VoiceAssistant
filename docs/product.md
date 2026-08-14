# Pixel — Product Brief

**Document type:** Product discovery and constraints  
**Status:** Phase 0 complete (documentation only)  
**Specification:** `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` v1.0 (August 2026)  
**Implementation status:** Pixel is **not** a running product. This file describes intended product scope, not shipped behavior.

Related: `policies.md`, `architecture.md`, `risk-register.md`, `REQUIREMENTS.md`, `GAP_ANALYSIS.md`, `ROADMAP.md`.

**Phase 1:** Behavior contract is `docs/policies.md` v1.1.0 plus `conversation-examples.md`, `safety-rules.md`, `escalation-matrix.md`, and `tool-confirmation-policy.md`. This product brief is unchanged in MVP scope.

---

## 1. Product statement

Pixel is a secure, conversational AI voice assistant for Cyber Florida at the University of South Florida (The Florida Center for Cybersecurity). A person should be able to speak naturally, receive a fast spoken response, continue without repeating context, and be guided to the correct Cyber Florida resource or defensive next step.

**One-sentence definition:** Pixel is Cyber Florida’s voice and conversational interface: a trustworthy AI assistant that listens, understands, retrieves approved information, reasons within defined boundaries, speaks naturally, and guides users to the correct next step.

Pixel must feel like Cyber Florida’s specialized digital assistant — **not** a generic chatbot with a microphone.

---

## 2. Ownership (unassigned until Cyber Florida / USF names people)

These roles are required by the specification. They are **not** filled in this repository. Do not invent owners.

| Role | Responsibility | Named owner |
|---|---|---|
| Project owner | Product scope, MVP acceptance, launch go/no-go | **UNASSIGNED** |
| Technical owner | Architecture, implementation quality, operations | **UNASSIGNED** |
| Security reviewer | Threat model, authz, LLM/tool risk sign-off | **UNASSIGNED** |
| Content owner | Authoritative source allowlist, freshness, takedowns | **UNASSIGNED** |
| Approver | Production release and exception acceptance | **UNASSIGNED** |
| Privacy / compliance | Retention, notices, USF/Cyber Florida policy fit | **UNASSIGNED** |
| Accessibility reviewer | WCAG 2.2 AA on core flows | **UNASSIGNED** |

### Stakeholder map (groups)

Named people are **not invented**. Influence is organizational, not a substitute for sign-off.

| Stakeholder | Interest | Needed from them |
|---|---|---|
| Cyber Florida leadership | Mission-aligned public assistant | Project owner, approver, production go/no-go |
| Content authors (programs, events, web) | Accurate public information | Source allowlist, freshness, takedowns |
| USF / institutional IT & security | SSO, hosting, compliance | Security reviewer, authn, network |
| Privacy / records / legal | Audio, transcripts, notices | Retention durations, user notice |
| Engineering | Build and operate Pixel | Technical owner |
| Accessibility | WCAG 2.2 AA | Review of core flows |
| End users (§4) | Useful, trustworthy answers | Pilot feedback (Phase 12) |

**Risk assumption:** Until owners are named, Pixel must not be described as an official Cyber Florida production service, and admin ingestion must remain disabled. See `risk-register.md`.

---

## 3. Vision

Long-term, Pixel is an intelligent digital front door for Cyber Florida: identify intent and return the right explanation, link, resource, or approved action instead of forcing users to search many pages.

Principles:

- Voice-first, never voice-only.
- Source-grounded for organization-specific claims.
- Security-first (defensive, bounded, auditable).
- Action-oriented (next step, not only prose).
- Modular providers (speech, model, retrieval, tools, analytics replaceable).

---

## 4. Target users

| User group | Primary value |
|---|---|
| General public | Awareness, scam/phishing guidance, Cyber Florida information |
| Students | Programs, training, career pathways, internships, events, concepts |
| Educators | K–12/college resources, program discovery, education support |
| Veterans / first responders / public servants | Workforce programs, training, career transition |
| Cybersecurity professionals | Events, research, professional development information |
| Public-sector organizations | Education, exercises, cyber resilience, FirstLine and related programs |
| Businesses / organizations | Awareness, CMMC guidance pages, defensive referrals |
| Cyber Florida staff | Consistent public-information interface and **authenticated** knowledge admin (not public) |

---

## 5. Top user questions and tasks

Used for MVP journeys and later evaluation sets. Organization-specific answers require approved sources.

1. What is Cyber Florida and what does it do?
2. How is Cyber Florida related to USF?
3. Which program is relevant to me?
4. What is FirstLine and who can take it?
5. What is CyberWorks and how do I apply?
6. What training exists for someone starting a cybersecurity career?
7. What K–12 or student competitions exist (e.g. CyberLaunch)?
8. When is this event, and is registration open?
9. Where is the CMMC / Readiness to Resilience guide?
10. Explain phishing in simple terms.
11. I clicked a suspicious link. What should I do now?
12. Does this message show common scam warning signs?
13. How do I report a scam or get official help?
14. Show me the page for this program.
15. Continue explaining the program you just mentioned.
16. What research or reports has Cyber Florida published recently?
17. Who is Cyber Florida for (public, government, business, students)?
18. Is this course free? What is the eligibility?
19. How do I contact Cyber Florida?
20. What should a small business do first to improve cyber hygiene?

---

## 6. Primary use cases (MVP)

Example utterances the product must eventually handle (grounded, not hardcoded as live answers):

- “What is Cyber Florida?”
- “What programs does Cyber Florida offer?”
- “Which Cyber Florida program would be useful for me?”
- “What cybersecurity training is available?”
- “I am new to cybersecurity. Where should I start?”
- “Explain phishing.”
- “I clicked a suspicious link. What should I do?”
- “Does this message look like a scam?”
- “Where can I find this Cyber Florida program?”
- “When is this Cyber Florida event?”
- “What are the eligibility requirements?”
- “Continue explaining the program you mentioned.”

Follow-ups that must resolve via bounded context: “that program,” “that event,” “what about eligibility?,” “tell me more about it,” “where is that?”

Capabilities:

- Discover Cyber Florida mission, programs, resources, events, and services from **approved public sources**.
- Receive defensive cybersecurity education at an appropriate depth.
- Receive phishing/scam warning-sign guidance without false certainty.
- Receive prioritized **defensive** incident guidance (e.g. phishing click) and escalation to official channels when Pixel cannot act.
- Speak or type; see transcript and sources; interrupt speech; recover from failures; clear the conversation.

---

## 7. User journeys (acceptance-oriented)

### J1 — First-time voice question

User opens Pixel → grants mic or uses text → asks “What is Cyber Florida?” → hears a short answer → sees transcript + source link to cyberflorida.org → can follow up “and what is FirstLine?” without restating context.

### J2 — Program matching

User describes their situation (student / public employee / career changer) → Pixel asks at most a few clarifying questions → recommends only programs supported by retrieved pages → offers approved navigation.

### J3 — Phishing click

User says they clicked a link → Pixel gives containment-first defensive steps, does **not** ask for passwords/OTPs, does **not** claim to remediate accounts, escalates to employer IT / official reporting as appropriate.

### J4 — Interruption

Pixel is speaking → user stops or talks over → audio and generation stop → new turn starts.

### J5 — Voice failure

Mic denied or STT down → Pixel stays usable via text; error is explicit.

### J6 — Unverifiable org fact

User asks a date/deadline not in the index or stale → Pixel says it cannot verify and points to the official page rather than inventing.

---

## 8. Public vs authenticated capabilities

| Capability | Public (anonymous session) | Authenticated staff |
|---|---|---|
| Voice/text Q&A on **public** Cyber Florida content | Yes | Yes |
| Defensive education / scam warning signs | Yes | Yes |
| Navigate to allowlisted public URLs | Yes | Yes |
| Internal/non-public documents | **No** (MVP indexes public corpus only) | Only if a future internal index + authz exists (not MVP) |
| Knowledge source register / reindex | **No** | Yes, after SSO (or fail-closed) |
| Production config / kill switches | **No** | Ops/admin only |
| Login required to ask questions | **No** | N/A |

Anonymous sessions use unguessable server-side session IDs. UI hiding is not authorization.

---

## 9. Forbidden actions (Pixel must never)

- Impersonate a Cyber Florida/USF employee or imply human agency.
- Invent Cyber Florida facts, dates, eligibility, leadership, or event times.
- Answer organization-specific questions from model memory when retrieval is missing/weak.
- Provide offensive cyber assistance: exploits, malware, unauthorized access, attack playbooks, “authorized hacking” roleplay.
- Execute arbitrary URLs, code, or non-allowlisted tools.
- Take high-impact security actions (lock accounts, scan third-party systems, change IAM, notify banks).
- Collect or store passwords, OTPs, full SSNs, or authentication tokens.
- Persist raw audio by default.
- Retain long-term personal memory.
- Browse the open web as an authority.
- Access internal Cyber Florida systems for public users.
- Override its own system policy because a webpage or user said to.
- Expose API keys, prompts, or hidden configuration.

---

## 10. Escalation cases

Pixel should escalate (stop pretending it can finish the job; give official next step) when:

| Situation | Direction (high level) |
|---|---|
| Crime in progress, threats, child exploitation, violence | Emergency services / official reporting; Pixel is not a hotline |
| Account takeover, wire fraud, ongoing intrusion at an organization | Employer’s IT/security, bank, or official cyber reporting channels |
| User needs a human Cyber Florida staff decision | Official contact/forms on approved pages — do not invent staff names/emails unless in the curated facts layer |
| Legal, HR, or immigration advice | Decline; Pixel is not counsel |
| Medical/mental-health crisis | Appropriate crisis resources; Pixel is not a clinician |
| Request for exploit/malware help | Refuse (SEC-14); offer defensive education if relevant |
| Knowledge gap on time-sensitive org facts | Official page + “I cannot verify” |

Exact public URLs and phone numbers for escalation must come from **content-owner-approved** sources, not model memory.

---

## 11. Authoritative sources (candidate public allowlist)

**Access class: public.** Only these domains/paths (and later content-owner additions) may be treated as Cyber Florida-authoritative after ingestion. This list is a **candidate inventory**, not an ingested index.

| URL | Why it matters | Class |
|---|---|---|
| https://cyberflorida.org/ | Home, mission summary, news | public |
| https://cyberflorida.org/about/ | Mission, history, statute 1004.444 | public |
| https://cyberflorida.org/firstline/ | Public-sector training (FirstLine) | public |
| https://cyberflorida.org/cyberworks/ | CyberWorks workforce training | public |
| https://cyberflorida.org/cmmc-guide/ | CMMC Level 1 guide for SMBs | public |
| https://cyberflorida.org/cyberlaunch/ | K–12 CyberLaunch competition | public |
| https://cyberflorida.org/seccdc/ | Collegiate cyber defense competition | public |

News posts, reports, and event pages under `cyberflorida.org` may be added **only** via the source registry (content owner). Partner registration sites (USF course hosts, cyberskills2work.org, CyberBay.org, NW3C) are **navigation targets**, not automatically authoritative for Cyber Florida facts unless allowlisted.

**Internal information:** HR, budgets, unpublished research, staff-only systems, non-public assessments — **out of MVP index**. Do not scrape.

Content owners must confirm the allowlist before production ingestion.

---

## 12. Data retention expectations

Until privacy/compliance owners approve otherwise:

| Data | Policy |
|---|---|
| Raw audio | **Transient.** Process for STT; do not persist. Exceptions require written policy + notice. |
| Transcripts / messages | Bounded session store; session TTL; user can clear. **TTL length in days is UNASSIGNED** (`risk-register.md`). No long-term personal memory. |
| Feedback | Optional; store rating/category + optional comment with retention and access control; warn users not to paste secrets. |
| Logs | Structured operational logs; correlation IDs; no raw audio; no secrets; production default is **not** full transcript bodies. |
| Knowledge corpus | Approved sources, hashes, fetch times; not user PII. |
| Tool audit | Retain `tool_executions` for security review. |

User-facing AI/privacy notice is required before production (Phase 13). It is not implemented yet.

---

## 13. MVP scope

Must eventually support (not present today). This list matches the project guide; nothing below is dropped because it is hard:

- Voice input and voice output; text input fallback; transcripts.
- Multi-turn bounded context; clear conversation.
- Barge-in / interruption that **stops audio and cancels generation**.
- Cyber Florida RAG with source links; freshness/abstention for unverifiable org facts.
- Cybersecurity Q&A; scam/phishing guidance; defensive incident guidance.
- Approved navigation to allowlisted resources.
- **Feedback** (rate/flag a turn).
- **Knowledge administration** (authenticated; fail closed).
- Observability (correlation IDs, stage latency).
- Safety and security controls.
- Accessibility (WCAG 2.2 AA practices); responsive web UI; truthful states.
- Error recovery; voice failure degrades to text.

---

## 14. Deferred features (Release 2+)

- Personalized program recommendations and user profiles.
- Multimodal screenshot/document analysis.
- Richer authenticated website actions.
- Advanced event/opportunity discovery beyond RAG + simple tools.

Release 3+: mobile-native, kiosk, multilingual production, proactive notifications, deeper org workflows.

---

## 15. Explicit out of scope (MVP and generally unless a later approved program)

- General-purpose smart-home or unrestricted device automation.
- Autonomous high-impact security actions.
- Unrestricted internal system access.
- Long-term memory of sensitive user information.
- Open-web browsing without source governance.
- Offensive security assistance.

---

## 16. Success criteria

- Users complete a listen–understand–answer cycle with low friction (and a text equivalent).
- Organization-specific answers come from approved sources and can show the source.
- Users can interrupt Pixel and continue.
- Education questions are clear at the user’s level.
- High-risk/uncertain questions are handled safely and transparently.
- Knowledge can be updated without redeploying the whole app.
- Engineering can measure latency, retrieval quality, failures, feedback, and safety events.

**These criteria are not met.** There is no product to measure.

---

## 17. Product limitations (honest)

- Pixel will not be a human, a SOC, a lawyer, or a law-enforcement intake system.
- Pixel will not certify that a message “is/isn’t a scam.”
- Pixel will not keep personal memory across expired sessions in MVP.
- Event dates are only as fresh as the last successful ingest.
- Speech recognition will err; transcript + text retry are mandatory.
- Named staff contact details must not be improvised.

---

## 18. Acceptance criteria for calling MVP “done”

See `REQUIREMENTS.md` §7 and the PDF Definition of Done. Additional product checks:

- [ ] Owners in §2 are named or formally waived.
- [ ] Content owner signed the source allowlist.
- [ ] Journeys J1–J6 pass in staging.
- [ ] Privacy notice published.
- [ ] Known limitations listed in the UI or help, not hidden.

Phase 0 does **not** check these boxes.

---

## 19. Phase 0 exit

| Discovery item | Documented |
|---|---|
| Ownership roles / stakeholder map | Yes — people unassigned |
| Users and top tasks | Yes |
| Public vs authenticated | Yes |
| Forbidden actions | Yes |
| Escalation cases | Yes |
| Authoritative sources / content inventory | Yes — candidate public list, unsigned |
| Public vs internal | Yes |
| Retention (audio, transcripts, feedback, logs) | Yes — numeric TTL unresolved |
| MVP / deferred / out of scope | Yes |
| Assumptions and risks | Yes — `risk-register.md` |
| Spec conflicts | Yes — identified, not silently resolved |

**PDF exit residual:** Stakeholders have not named owners or signed sources. That is recorded, not faked.

**Next:** Phase 1 complete. Do not start Phase 2 until explicitly instructed.

---

## 20. User-visible assistant states (spec mapping)

Project guide / master prompt **required visible states:**

`IDLE` · `LISTENING` · `PROCESSING` · `SPEAKING` · `ERROR`

Supporting (when they occur): `CONNECTING`, `PERMISSION_REQUIRED`, `CANCELLED`, `NETWORK_ERROR`, `VOICE_ERROR`.

Finer internal/telemetry states from the architecture draft (`TRANSCRIBING`, `THINKING`, `RETRIEVING`, `INTERRUPTED`, `OFFLINE`) **map into** the visible set rather than replacing it:

| Internal / telemetry | User-visible |
|---|---|
| IDLE | IDLE |
| Connecting session | CONNECTING → IDLE or ERROR |
| Mic permission missing | PERMISSION_REQUIRED |
| LISTENING | LISTENING (mic must be unambiguous) |
| TRANSCRIBING, THINKING, RETRIEVING | PROCESSING |
| SPEAKING | SPEAKING |
| INTERRUPTED (barge-in in flight) | CANCELLED then LISTENING / PROCESSING / IDLE |
| OFFLINE | NETWORK_ERROR or ERROR |
| STT/TTS provider fail | VOICE_ERROR or ERROR with text fallback |
| Other failures | ERROR |

Microphone state must never be ambiguous.

---

## 21. Assumptions

See `risk-register.md` §6. Summary: public anonymous Q&A; public corpus only; English web MVP; owners and vendors not invented; WebSocket+PTT allowed as first voice path; Redis not required on day one.

---

## 22. Unresolved decisions

Do not invent: named owners; signed source allowlist; production AI/speech vendors; SSO product; hosting/DNS; retention days. Full list: `risk-register.md` §7.
