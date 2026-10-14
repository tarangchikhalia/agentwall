# AgentWall v0.1 requirements

Status: Architecture baseline; detailed implementation contracts pending
Date: 2026-10-14

## Authority and scope

The first focus is policy evaluation and audits. This document and [ADR 003](ADRs/003-policy-audit-first.md) replace the previous gateway release scope. See [architecture](architecture/v0.1.md) for design boundaries. These are planned requirements, not implemented capabilities.

v0.1 serves one organization on one service instance. Applications request authorization and must enforce allow/deny and fail closed on all errors or timeouts. AgentWall does not forward actions or attest execution.

## Functional requirements and acceptance evidence

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| POL-01 | A native Go evaluator interprets validated YAML policies using `agentwall.dev/v1alpha1`, compiled into immutable typed condition trees. Policies cannot execute arbitrary code; no OPA/Rego dependency is required. | Policy fixtures demonstrate equivalent YAML and evaluator behavior. |
| POL-02 | At least one matching allow and no matching deny are required to allow. Ordering and directories have no semantic effect. | Default denial, deny precedence, and reorder tests pass. |
| POL-03 | Reject unknown fields, unsupported schema versions/operators, invalid types, and policies exceeding configured limits. | Invalid candidates cannot replace the active bundle. |
| POL-04 | Support typed `eq`, `neq`, `in`, `notIn`, `startsWith`, `gt`, `gte`, `lt`, `lte`, and logical `all`, `any`, `not`. Use trusted server time for time conditions. | Published semantics and fixtures cover missing/null attributes, negation, type errors, wildcard boundaries, and nesting limits. Detailed truth tables remain a contract prerequisite. |
| LIFE-01 | Poll a configured Git branch or revision, default every 60 seconds; validate and run policy tests before preparing a candidate. | Failed fetch, validation, tests, or preparation preserve the current revision. |
| LIFE-02 | Persist immutable SHA-256-addressed bundles and atomically activate prepared snapshots. | Concurrent requests see one complete revision each; corruption is rejected. |
| LIFE-03 | Restore validated last-known-good state on startup; otherwise remain unready for authorization. | Restart and missing/corrupt bundle tests pass. |
| LIFE-04 | CLI rollback activates a validated bundle and persistently pins synchronization until explicit resume. | Rollback survives restart and subsequent polling. |
| AUTH-01 | Authenticate service callers using scoped API keys; generate secure secrets, display once, store hashes, support list/rotate/revoke through CLI. | Invalid/revoked keys fail; rotation overlap is bounded and documented; secrets never appear in diagnostics. |
| AUTH-02 | Restrict operations and asserted attributes per key; reject unauthorized assertions. | Tests prevent caller impersonation and assertions outside configured field/value constraints. Detailed assertion rules must be specified first. |
| AUTH-03 | Protect administrative commands with a separate local administrative identity or credential. | Unauthorized key, policy, rollback, and resume operations fail. Bootstrap and credential storage contracts must be specified first. |
| API-01 | Provide versioned REST authorization and audit-query APIs, plus liveness, readiness, and restricted metrics. | OpenAPI and contract tests cover schemas, limits, scopes, pagination, and errors. |
| API-02 | Return decision ID, allow boolean, reason code, and revision; distinguish decisions from failures. | Allow/deny return 200; invalid input 400; invalid key 401; insufficient scope 403; evaluation failure 500; unavailable engine 503; server timeout 504. Clients block on any failure. Audit admission failure status remains to be specified. |
| AUD-01 | Queue decision events in bounded memory and batch writes to PostgreSQL; bound retries and use unique decision IDs for idempotency. | Retry, saturation, outage, concurrency, and shutdown tests exercise the documented loss behavior. |
| AUD-02 | Default to strict queue admission; configurable best effort permits decisions with loss counters. | Strict mode never returns a successful decision without accepting its audit event; best effort exposes dropped-event metrics. Neither mode claims crash durability. |
| AUD-03 | Record organization, authenticated caller, principal, agent, session, action, resource, outcome, reason, policy revision, timestamp, and trace IDs. | Queryable records correlate with responses; redaction tests exclude credentials and unapproved payloads. |
| AUD-04 | Provide scoped REST and CLI audit queries and configurable retention, default 90 days, including indefinite retention. | Pagination/filter/access tests and bounded retention cleanup pass. |
| OPS-01 | Provide JSON logs, OpenTelemetry traces, Prometheus metrics, health checks, bounded requests/timeouts, and graceful shutdown. | Operators can diagnose queue pressure, sync failures, and unavailable evaluation; identifiers are excluded from metric labels. |
| OPS-02 | Provide Docker Compose, configuration guidance, migrations, backup/restore and rotation runbooks. | An independent engineer can deploy and operate a fresh installation. |

## Release gates

- All functional requirements have passing evidence; detailed contracts below are resolved.
- Critical authorization logic targets at least 80% coverage, with mandatory security scenarios regardless of percentage.
- Race/concurrency tests, atomic reload, rollback recovery, PostgreSQL outage, retry exhaustion, and queue saturation tests pass.
- Reproducible benchmarks target 1,000 requests/second, at least 100 concurrent requests, and p99 authorization latency below 5 ms under published conditions.
- Documentation distinguishes implemented behavior, residual risks, and deferred work. A tagged release can be installed independently.

## Contracts to resolve before dependent implementation

1. YAML schema, missing/null and negative comparison truth tables, wildcard semantics, and resource limits.
2. OpenAPI schemas, errors including audit admission failure, scopes, query pagination, and request limits.
3. Trust matrix: server-derived fields, allowed caller assertions, permitted values/namespaces, omissions, and rejection rules.
4. Audit state machine: capacity accounting including in-flight batches, retry exhaustion, loss accounting, shutdown deadline, and readiness during outages.
5. PostgreSQL schema, migrations, indexes, key storage, retention and backup behavior.
6. Administrative CLI bootstrap/authentication, rotation/revocation, rollback/pin persistence, resume, and recovery state transitions.
7. Git credential handling and source restrictions; bundle integrity and trust; filesystem permissions; TLS deployment and restricted operations endpoints.

## Deferred scope

Gateways and streaming, LLM routing, MCP/A2A protocol handling, credential brokerage, approvals, verified delegation and permission intersection, layered administration, replay/shadow mode, arbitrary policy-code execution, durable-before-response and tamper-evident audit, OIDC/mTLS, HA, multi-tenancy, web UI, Kubernetes, and isolated execution are outside v0.1. Future scope requires separate review; previous v1 scale and availability targets are not v0.1 release gates.
