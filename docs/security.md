# Security Model & Threat Analysis for B2BValue

## Threat Model
- **Actors:** Internal agents, system users, external API integrations
- **Assets:** Business context, workflow history, semantic knowledge, relationship graph
- **Threats:**
  - Unauthorized access to sensitive memory tiers
  - Tampering with workflow history or context
  - Injection of malicious or malformed data
  - Data leakage via logs or error messages

## RBAC Matrix
| Role   | Working | Episodic | Semantic | Graph |
|--------|---------|----------|----------|-------|
| admin  | RWX     | RWX      | RWX      | RWX   |
| agent  | R       |          | R        |       |
| system | RWX     | RWX      | RWX      | RWX   |

- **R**: Read, **W**: Write, **X**: Delete

## Controls
- All memory access is mediated by `MemoryManager` and subject to role-based access control.
- Default: agents get read-only access to working/semantic, admin/system get full access everywhere.
- All entity writes are validated for type, required fields, and sensitivity.
- All external (untrusted) JSON is schema-validated before use.
- Audit logs are written for all memory mutations and access attempts.

## Recommendations
- Periodically audit logs for suspicious access patterns.
- Rotate admin/system credentials regularly.
- Review and update access control policies as new agents are added.

---
See also: `local-coding-rules.md` and `docs/entity_schemas.md`.
