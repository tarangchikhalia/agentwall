# AgentWall roadmap

Date: 2026-10-14
Current status: Foundation scaffold; policy engine and audit first

## Stage 1: standalone policy and audit service, v0.1

Milestones advance on evidence, not elapsed weeks. Security scenarios are tested throughout implementation.

| Milestone | Deliverable | Exit gate |
| --- | --- | --- |
| M0 — Contracts | Policy schema/semantics, trust matrix, OpenAPI, audit failure states, storage and CLI contracts; updated threat model. | Implementation prerequisites in requirements are resolved; fixtures specify boundary and failure cases. |
| M1 — Policy and audit vertical slice | Local validated YAML bundle, native Go evaluator, scoped caller authentication/assertion checks, REST authorization, bounded queue and PostgreSQL persistence; sample enforcing application. | Allow/deny/default-deny and assertion tests pass; denied/error responses block the sample action; events correlate with decisions; queue saturation follows strict/best-effort contract. |
| M2 — Safe policy lifecycle | Git polling, policy tests, immutable persistence, atomic activation, restart recovery, rollback/pin/resume CLI. | Invalid candidates preserve active state; concurrent evaluation sees complete snapshots; rollback survives restart and polling. |
| M3 — Audit and administration | Key management, scoped audit REST/CLI queries, retention, retry/recovery and shutdown behavior. | Revocation, rotation, restricted queries, retry exhaustion, database outages, and bounded cleanup/drain are tested. |
| M4 — Operations and validation | Metrics, traces, logs, readiness, Docker Compose, migrations, backup/restore and benchmark harness. | Fresh deployment and recovery reproduce; race/security/failure tests pass; benchmark methodology and results are published. |
| M5 — v0.1 release | Integration example, policy guide, API/CLI reference, threat model, ADRs, runbooks and tagged artifacts. | An independent engineer deploys, integrates, queries decisions, updates/rolls back policies, and operates the service using documentation. |

The vertical slice needs only the authentication and storage necessary to safely exercise policy and audit. Full administration follows; it must not delay proving the core path or turn unauthenticated scaffolding into a deployable service.

## Stage 2: AI gateways, separately reviewed after v0.1

Evaluate LLM gateway behavior, MCP tool authorization, and agent-to-agent identity/delegation incrementally. Provider routing, streaming, token accounting, credential brokerage, and end-user authority verification require explicit contracts before commitment. The old gateway requirements are historical input, not automatic acceptance criteria.

## Stage 3: secure agent runtime

Consider workload identity, sandboxing, network isolation, and execution lifecycle only after reviewing Stage 2 outcomes. Do not introduce unfinished runtime code in v0.1.

## Historical plans

The previous [gateway roadmap](archive/gateway-v1-roadmap.md) and [v1 requirements](archive/gateway-v1-requirements.md) are superseded by [ADR 003](ADRs/003-policy-audit-first.md).
