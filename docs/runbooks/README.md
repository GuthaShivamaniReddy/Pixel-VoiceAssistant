# Runbooks

**Operational status:** Phase 8 security procedures exist as configuration and documentation. Pixel still has no named production on-call.

These runbooks must be exercised in staging before production.

| Runbook | Purpose |
|---|---|
| [security-incident.md](security-incident.md) | Detection, containment, kill switches, recovery |
| [secret-rotation.md](secret-rotation.md) | Provider, database, admin, CI secrets |
| [incident-minimum.md](incident-minimum.md) | Short checklist |
| [knowledge-refresh.md](knowledge-refresh.md) | Ingest and promote an index (future HTTP admin) |

When a runtime exists, each runbook must name an on-call owner (currently UNASSIGNED).
