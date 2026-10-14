# ADR 003: Policy and audit first

Date: 2026-10-14
Status: Accepted direction

## Context

The earlier roadmap made the first preview an integrated gateway with identity delegation, credential brokerage, approvals, and durable tamper-evident audit. The implementation remains a Go service scaffold. The new architecture proposal and maintainer direction make policy evaluation and audits the first focus.

## Decision

AgentWall v0.1 is a standalone Policy Decision Point and authorization-decision audit service. Use Go, a native Go policy evaluator, declarative YAML, Git policy synchronization, immutable local bundles, REST, scoped API keys, PostgreSQL, and Docker Compose. Start with a single organization and a single service instance.

Applications enforce decisions. Caller assertion permissions do not independently establish user authority or delegation provenance. The default audit mode is strict queue admission, with configurable best effort. Neither mode guarantees crash-durable or tamper-evident audit.

This decision supersedes the previous release sequencing and conflicting gateway guarantees in active documentation. Historical [v1 requirements](../archive/gateway-v1-requirements.md) and [roadmap](../archive/gateway-v1-roadmap.md) are retained for context, not current acceptance criteria. [ADR 001](001-language.md) selects Go; [ADR 002](002-policy-engine.md) selects a native YAML-based Go evaluator in place of the previously proposed OPA integration.

## Consequences

The first release can be integrated independently and tested without protocol proxies. Security documentation must distinguish authorization from action enforcement and queue admission from durable persistence.

Gateway protocols, credential brokerage, approvals, delegation verification, permission intersection, audit signing, HA, and runtime isolation are deferred. LLM routing was previously excluded; it is now a candidate Stage 2 topic, not an implementation commitment. Each later stage requires a separate review.

Detailed policy, trust, API, audit failure, storage, and CLI contracts must be resolved before implementing their dependent components. Do not treat unresolved design details as approved guarantees.
