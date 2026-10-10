# AgentWall v1.0 Requirements

Status: Draft — maintainer scope and scale decisions incorporated; remaining implementation and measurement details are listed below.
Date: 2026-10-09

## Purpose and basis

AgentWall is an open-source, self-hosted security and governance layer that governs calls between AI agents and their tools and between agents. It identifies the authority behind each call, enforces policy, brokers credentials, and records explainable, tamper-evident decisions.

This document describes the requirements for the v1.0 release. Maintainer decisions in this document take precedence over conflicting roadmap statements in the README.

AgentWall v1.0 governs all LLM calls, MCP calls, external API calls, and agent-to-agent traffic routed through it. Each deployment serves a single organization and must accommodate thousands of users and hundreds of agents. Required interfaces are Streamable HTTP for MCP, REST APIs, and A2A for agent-to-agent communication. SSO must be provider-agnostic. Credential backends remain undecided.

## Users and operating boundary

- Platform operators deploy and operate AgentWall, configure integrations.
- Security administrators define organization policies and investigate activity.
- Team administrators configure team rules and agent manifests within organization limits.
- End users initiate work under their own authority; approvers decide requests requiring human review.
- Agent developers integrate callers and tools with the gateway.
- Auditors inspect decisions and independently verify audit integrity.

Enforcement applies to traffic routed through AgentWall. Deployment documentation must explain how operators prevent direct tool access from bypassing the gateway. AgentWall cannot inspect information held entirely inside a model's context or guarantee prevention of every attack.

## Functional requirements

### Gateway and action model

| ID    | Requirement                                                                                                                                                   | Acceptance evidence                                                                                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-01 | Proxy MCP tool traffic using Streamable HTTP, with support for concurrent sessions and long-lived streams.                                                                           | Supported transports pass protocol interoperability tests; concurrent streams preserve message boundaries and cancellation behavior. Streamable HTTP interoperability is required; supported MCP protocol versions remain pending. |
| FR-02 | Apply the same identity, policy, approval, credential-brokerage, and audit controls to all LLM, REST API, and A2A traffic crossing the gateway (FR-26–FR-28).                                                                                            | A permitted call reaches its configured destination; a denied call causes no upstream invocation. REST and A2A interoperability is required; supported A2A versions and LLM provider/API adapters remain pending.                           |
| FR-03 | Represent each governed call as a common Action containing caller, initiating authority, delegation chain, target, operation, and policy-relevant attributes. | Equivalent calls through supported adapters produce consistent policy inputs and correlated audit records. Exact schema is published before v1.0.                         |
| FR-04 | Evaluate authorization before forwarding a governed action or acquiring its upstream credential.                                                              | Deny and approval-pending outcomes produce no upstream action. Streaming authorization occurs before upstream execution; authorization behavior for policy changes or failures during an active stream must be documented.     |
| FR-05 | Validate requests, restrict destinations to configured targets, and apply configurable request, connection, and stream limits.                  | Malformed requests, unconfigured destinations, and limit violations terminate with documented errors and auditable reasons.                                               |

### Required traffic integrations

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-26 | Authorize and proxy all direct LLM calls routed through AgentWall, including streaming calls where supported by the upstream interface. | For each supported LLM adapter, allow forwards the call, deny prevents upstream invocation, and require-approval blocks execution until approved. Streaming responses preserve protocol behavior. Every decision identifies caller authority and policy. LLM adapter selection remains pending. |
| FR-27 | Authorize and proxy external REST API calls using the target, HTTP method, and policy-relevant request attributes. | Tests cover permitted and denied methods/resources, approval-required operations, credential injection, upstream errors, and correlated audit records. Denied or pending requests cause no upstream invocation. |
| FR-28 | Authorize and proxy agent-to-agent traffic using A2A while preserving the initiating authority and delegation chain. | Supported A2A interactions pass interoperability tests; downstream agents cannot obtain authority beyond the effective permission intersection. Every governed interaction has a policy decision and correlated audit record. Supported A2A versions remain pending. |

### Identity and delegated authority

| ID    | Requirement                                                                                                                                                    | Acceptance evidence                                                                                                                                                                |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-06 | Identify the calling agent, initiating user or non-user authority, and intermediate agents.                                                                    | Audit and policy inputs identify the complete authority chain for supported invocation types. Webhook and autonomous-agent authority models are pending.                           |
| FR-07 | Authenticate identity assertions and bind them to the request; do not trust arbitrary caller-supplied user headers.                              | Forged, missing, expired, or invalid assertions cannot authorize a call. Supported identity mechanisms are pending.                                                                |
| FR-08 | Enforce effective permissions as the intersection of the initiating authority and every agent in the delegation chain. Delegation must never expand authority. | Tests deny user-to-agent and agent-to-agent requests whenever any participant lacks the required permission, including attempts to obtain inaccessible data through another agent. |
| FR-09 | Validate delegation provenance and reject invalid, incomplete, or cyclic chains according to documented limits.                                  | Tampering, omission, replay, and excessive-depth tests cannot bypass permission intersection.                                                                                      |

### Policy administration and evaluation

| ID    | Requirement                                                                                                                           | Acceptance evidence                                                                                                                                                                                                |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FR-10 | Use Policy Engine for attribute-based decisions with allow, deny, and require-approval outcomes.                                                | Each outcome is exercised using Action attributes; decisions include an explainable reason and policy identifier/version.                                                                                          |
| FR-11 | Support layered organization guardrails, team rules, and per-agent manifests. Lower layers must not weaken higher-level restrictions. | A team or agent configuration cannot override an organization denial or broaden the effective permission intersection. Conflict-resolution semantics are documented.                                               |
| FR-12 | Provide an API and CLI for policy and manifest administration through the control plane.                                              | Operators can validate, activate, inspect, and update configuration using documented interfaces. rejected updates leave the active policy intact; activation and rollback are versioned and audited. |
| FR-13 | Replay candidate policies against recorded traffic and run policies in shadow mode before enforcement.                                | Reports compare candidate outcomes with enforced decisions; shadow decisions do not grant or revoke live access. Replay fidelity and retained inputs are documented.                                               |

### Credential brokerage

| ID    | Requirement                                                                                                                                                                | Acceptance evidence                                                                                                                                                                                                                |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-14 | Keep real upstream secrets out of agent possession. Acquire short-lived, narrowly scoped credentials for each allowed call and inject them only into the upstream request. | Agents, downstream responses, logs, approval messages, and traces do not expose credentials; expired or out-of-scope credentials cannot authorize operations. Supported credential providers and upstream limitations are pending. |
| FR-15 | Deny calls when the credential broker cannot securely issue the required credential.                                                                                       | Broker outages or issuance failures cause no upstream invocation and yield an explainable failure record where audit storage remains available.                                                                                    |

### Human approvals

| ID    | Requirement                                                                                                                                                                                | Acceptance evidence                                                                                                                                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-16 | Support human-in-the-loop approval through Slack with signed decision records. Policy defines eligible approvers, approval validity, and the authority permitted by an approval; no additional approval channel is required for v1.0.                                                                                                             | A policy-triggered request stays blocked until an authorized approver decides; approval and rejection are attributable and their signatures can be verified.                                                        |
| FR-17 | Bind approval to the exact action, authority chain, and policy context; enforce policy-defined expiry and prevent reuse. Any exceptional authority must be explicitly permitted by policy and remain within organization guardrails. | Altered, expired, duplicate, or unauthorized decisions cannot execute an action. Approval cannot bypass authentication or organization guardrails; approval grants follow explicit policy rules.                                                                         |
| FR-18 | Revalidate authorization before executing an approved action and fail closed on timeout or approval-service failure.                                                         | Revocation or a stricter policy applied while approval is pending prevents execution. Retry and one-time-consumption semantics are documented without claiming exactly-once execution for arbitrary upstream tools. |

### Audit and observability

| ID    | Requirement                                                                                                                                          | Acceptance evidence                                                                                                                                                                                                                                     |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-19 | Maintain an append-only, hash-chained audit log with signed checkpoints and a `verify` command.                                                      | Verification detects modified records and broken chains. Documentation describes how trusted checkpoints expose truncation and what the scheme cannot prove after signer compromise.                                                                    |
| FR-20 | Record every governed decision, its reason, policy version, caller authority, target/action, approval linkage, and execution outcome when available. | Allow, deny, approval, and upstream-error scenarios produce correlated records sufficient to explain the decision. security-relevant administrative changes are also audited.                                                             |
| FR-21 | Fail closed if a required audit record cannot be durably written before forwarding.                                                                  | Storage failure or exhaustion prevents new upstream actions; operators receive a visible health failure. recovery reconciles attempts whose final outcomes could not be recorded. Ordering and durability across HA replicas are pending. |
| FR-22 | Export OpenTelemetry traces and supply a Langfuse and Grafana demonstration stack.                                                                   | A sample request can be followed across gateway stages and linked to its audit record. metrics expose request rates, decision outcomes, dependency failures, and latency without secrets.                                                 |
| FR-23 | Provide an audit viewer with provider-agnostic SSO for v1.0, without requiring a particular identity vendor.                                                                                                           | Authorized users can find and inspect decisions and verification status. access is role-restricted and audit export is supported. SSO protocol(s), roles, filters, and broader management UI scope are pending; acceptance must demonstrate that SSO is not tied to one vendor.                              |

### Organization configuration

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-29 | Allow each organization to configure audit retention, payload capture, storage backend, signing/key custody, and checkpoint anchoring within supported options. | Document and validate every setting; demonstrate that configuration is honored and that invalid settings cannot silently disable mandatory audit persistence or integrity guarantees. Document how retention and key/checkpoint changes affect verification and replay. Supported options and defaults remain pending. |
| FR-30 | Configure Slack approval rules through policy, including eligible approvers, validity period, and any explicitly permitted exceptional authority. | Different policies select different approvers and validity periods; unauthorized, expired, or reused decisions fail. Exceptional authority requires explicit policy permission and cannot bypass authentication, delegation limits, or organization guardrails. |

### Stable interfaces

| ID    | Requirement                                                                                                                                    | Acceptance evidence                                                                                                                                                                     |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-25 | Publish stable v1.0 APIs, Action/configuration schemas, CLI behavior, and integration contracts.                                               | Documentation and compatibility tests cover supported interfaces; changes follow a documented versioning and migration policy.                                                          |

## Non-functional requirements

| ID                           | Requirement                                                                                                                                                                       | Acceptance evidence                                                                                                                                                                                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-01 Security              | Fail closed when identity cannot be established or required policy evaluation, credential issuance, or audit persistence fails. Approval-service failure must not imply approval. | Fault-injection tests show no unauthorized upstream calls. Existing-stream behavior on dependency failure is explicitly specified before release.                                                                                       |
| NFR-02 Confidentiality       | Protect credentials and sensitive traffic in transit and at rest; minimize retained payloads and redact secrets from diagnostic outputs.                            | Security tests cover transport protection, storage access controls, and leakage paths. Audit retention, payload capture, storage backend, signing/key custody, and checkpoint anchoring must be configurable by the organization. Supported mechanisms and secure defaults remain pending.                                                       |
| NFR-03 Isolation             | Within a single-organization deployment, team boundaries and administrative privileges must preserve policy restrictions. Enforce least privilege for control-plane and audit access.           | Cross-boundary and privilege-escalation tests fail safely. Independent organizations use separate deployments; multi-tenant operation is outside v1.0 scope.                                                                                                     |
| NFR-04 Availability          | Provide 99% availability and support production HA without weakening authorization, approval, or audit guarantees.                                                                                             | Replica/dependency failure and recovery tests validate documented consistency and recovery behavior. Measure availability against the 99% target; measurement window, service boundary, exclusions, supported topology, RPO, and RTO remain pending.                                                                 |
| NFR-05 Performance           | Support 1,000 requests per second with average gateway-added latency of at most 10 ms. Preserve streaming behavior and bound resource use. Publish reproducible load benchmarks.                                                             | Benchmarks report added latency, throughput, concurrent sessions, resource consumption, and behavior under overload. Load tests must demonstrate 1,000 requests per second and average added latency at most 10 ms. Human approval wait and upstream execution time are measured separately from gateway overhead. Workload mix, credential issuance accounting, concurrent sessions, test duration, and reference hardware remain pending.                                                  |
| NFR-06 Deployment            | Be self-hostable as a single-organization deployment for organizations needing on-premises or in-country operation. Use Go, with static binaries and small container images as deployment goals.                      | Installation and upgrade instructions work in supported environments; operators can identify all external dependencies and outbound data flows. Air-gapped support, operating systems, orchestration, and artifact targets are pending. |
| NFR-07 Operability           | Expose health/readiness diagnostics, configurable limits/timeouts, and documented backup, restore, key rotation, and incident procedures.                           | Operators can distinguish unavailable security dependencies from upstream faults and perform a tested restore and rotation.                                                                                                             |
| NFR-08 Maintainability       | Follow repository contribution standards, handle errors explicitly, document user-facing behavior, and justify dependencies.                                                      | Review and CI cover relevant unit, integration, end-to-end, regression, security, and performance checks; release documentation matches behavior.                                                                                       |
| NFR-09 Security assurance    | Complete an independent security review before v1.0 and maintain a threat model and private vulnerability-reporting process.                                                      | Review scope and findings are recorded; unresolved release-blocking findings are remediated and retested. Severity/release-blocking criteria are pending.                                                                 |
| NFR-10 Compatibility         | Maintain documented stable public contracts and migration guidance for breaking changes.                                                                                          | Contract tests and upgrade tests cover supported versions and deployment modes; version support follows the security policy.                                                                                                            |
| NFR-11 Privacy and residency | Self-hosted operation must make the destinations of audit, telemetry, and approval data explicit. Optional external exports can be disabled.              | A deployment's data-flow documentation accounts for all outbound integrations; retention and deletion behavior preserve stated audit-verification limits. No regulatory certification is implied.                                       |
| NFR-12 Threat model | Develop and maintain a version-controlled threat model in `docs/threat-model.md`, beginning during foundations and updating it as architecture and integrations change. | Document assets, actors, data flows, trust boundaries, deployment assumptions, abuse cases, mitigations, and residual risks. Cover identity spoofing, delegation/approval abuse, policy bypass, direct-access bypass, credential exposure, malicious upstreams, audit tampering, and denial of service across LLM, MCP, REST, A2A, and control-plane interfaces. Link mitigations to requirements and security tests; review the model before v1.0 and provide it to the independent security reviewer. |
| NFR-13 Benchmark harness | Set up a version-controlled, repeatable benchmark harness during foundations and extend it as gateway capabilities become available. | Provide documented commands, configurable load/concurrency/duration, representative LLM, Streamable HTTP MCP, REST, and A2A fixtures, and controlled upstream baselines. Exercise allow, deny, streaming, policy evaluation, credential brokerage, and audit persistence paths. Report throughput, average and percentile gateway-added latency, errors, concurrent sessions, and CPU/memory usage with workload, hardware, configuration, and revision metadata. Separate approval wait and upstream execution from gateway overhead; retain reproducible results and evaluate the 1,000 requests/second and 10 ms average-overhead targets under agreed conditions. |

| NFR-14 Identity scale | Support thousands of users and hundreds of agents within a single organization while preserving identity resolution, policy isolation, delegation checks, and audit attribution. | Populate representative user and agent identities and exercise authorization under the benchmark workload. Report tested identity counts and demonstrate that permissions and audit records remain correctly attributed. Exact counts and active-session concurrency remain pending. |

## Scope exclusions

- Model routing, model selection, and replacement of an LLM gateway such as LiteLLM.
- Inspection of information that never crosses the gateway.
- Detectors, including prompt-injection and data-leak detectors, are outside v1.0 scope.
- Compliance certification, a hosted SaaS service, and integrations not selected for the v1.0 support matrix are not established requirements.
- A full management web UI is not established by the roadmap; the audit viewer and SSO are included, while additional UI scope remains pending.

## Resolved scope traceability

| Agreed scope | Requirements |
| --- | --- |
| All LLM, MCP, REST API, and A2A traffic | FR-01, FR-02, FR-26, FR-27, FR-28 |
| Streamable HTTP for MCP | FR-01 |
| Provider-agnostic SSO | FR-23 |
| Slack approvals governed by policy | FR-16–FR-18, FR-30 |
| Single-organization deployment | NFR-03, NFR-06 |
| Thousands of users and hundreds of agents | NFR-14 |
| 1,000 requests/second and average added latency at most 10 ms | NFR-05, NFR-13 |
| 99% availability | NFR-04 |
| Organization-configurable audit settings | FR-29, NFR-02 |
| No detectors | Scope exclusions |

Implementation choices and measurement details explicitly marked pending in the requirements remain unresolved, including credential backends. They do not change the agreed scope.

## v1.0 release acceptance

Release evidence must demonstrate the agreed 1,000 requests/second throughput, average gateway-added latency of at most 10 ms, 99% availability, and capacity for thousands of users and hundreds of agents under the documented measurement conditions.
