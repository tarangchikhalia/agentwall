> Historical document, superseded on 2026-10-14 by [ADR 003](../ADRs/003-policy-audit-first.md). This is not the current release scope.

# AgentWall roadmap to v1.0

> Current Status: M0-Foundations

## Milestone plan

| Milestone | Deliverable | Exit gate |
| --- | --- | --- |
| M0 — Foundations | Agreed support/trust/storage/deployment contracts, initial threat model, Go build/CI, runnable benchmark runner and protocol fixtures. | Pending foundation choices have reviewed decisions; clean build and controlled baseline benchmarks reproduce; threat boundaries and risks are documented. |
| M1 — Core gateway, development alpha | Shared Action schema, configuration, OPA evaluation, durable audit append, secure outbound transport, fail-closed dispatch, and MCP/REST/LLM/A2A adapters. | All adapters normalize Actions and pass protocol fixtures; deny/pending and dependency-failure tests cause no upstream execution; streaming/cancellation preserve boundaries. Identity/broker/approval fakes are development-only and cannot enable production readiness. |
| M2 — Identity and authority | Verified users/workloads, delegation provenance, permission intersection, layered policy/manifests, versioned administration API and CLI, administrative roles. | User/agent-chain authority only shrinks; forged/replayed assertions fail; team rules cannot weaken organization guardrails; policy activation/rollback is attributable. |
| M3 — v0.1 integrated preview | Selected per-call credential backend, hash-chained audit with signed checkpoints and verification CLI, policy-driven Slack approvals, telemetry and demo stack. | Every supported traffic family passes real integration tests for allow/deny/approval, credential secrecy, durable pre-forward audit, and revalidation. Corruption/truncation tests validate the declared audit guarantees. Publish scope/limitations; this milestone does not claim final HA, availability, performance, or independent-review completion. |
| M4 — v0.5 production-hardening beta | Policy replay/shadow mode, health diagnostics, supported deployment packaging, HA audit/approval/policy consistency, failover/streaming validation, operations runbooks. | Replica/dependency failures cannot weaken security; shadow evaluation cannot affect enforcement; replay never executes tools; restore/rotation and bypass-prevention instructions are exercised. Beta remains subject to final release gates. |
| M5 — v1.0 release candidate to stable | Provider-agnostic SSO audit viewer, security regressions, scale/performance and availability evidence, stable contracts, updated threat model, independent review, release artifacts and documentation. | All accepted requirements link to passing evidence; 1,000 requests/sec and at most 10 ms average overhead meet the agreed workload; identity scale and 99% availability are demonstrated; recovery targets pass; blocking review findings are fixed and retested. |
