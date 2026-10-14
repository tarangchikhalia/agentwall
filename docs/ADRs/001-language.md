# ADR 001: Use Go for the policy and audit service

Date: 2026-10-14
Status: Accepted

## Context

AgentWall v0.1 is a standalone authorization policy engine and audit service. Its first implementation must authenticate callers, validate trusted assertions, evaluate policies, admit decision events to a bounded queue, and expose REST and CLI interfaces.

The service also needs background Git synchronization, safe policy activation, PostgreSQL batch writes, graceful shutdown, and operational telemetry. Correctness under concurrency and dependency failure matters as much as request throughput. The project prioritizes engineering learning and a complete, maintainable first release.

The release boundary follows [ADR 003](003-policy-audit-first.md). Gateways and isolated agent execution are later-stage work.

## Decision

Use Go as the primary implementation language for the service and CLI. Build v0.1 as a modular monolith, introducing internal packages and interfaces at concrete boundaries rather than splitting components into separate services.

Implement the policy evaluator directly in Go over validated YAML policy structures, as described in [ADR 002](002-policy-engine.md). Use the Go version declared in `go.mod` consistently in development and CI.

## Rationale

- Go supports the HTTP service, background workers, cancellation, and synchronization needed by the authorization and audit paths.
- An in-process Go evaluator keeps policy matching in the same language as validation and avoids a separate policy runtime or network service.
- The standard tooling provides formatting, tests, race detection, profiling, and benchmarks for validating security-sensitive concurrent behavior.
- A compiled executable provides a straightforward deployment unit for the service and CLI. Static binaries and small container images remain packaging goals that must be verified with the selected dependencies.
- Go offers a practical balance between implementation effort, operational simplicity, and opportunities to study distributed-system and security failure modes.

## Alternative considered

Rust was considered for its memory-safety model and control over resource usage. It remains a viable systems language, but its additional learning and implementation effort was not justified for this release. AgentWall's immediate challenges are policy semantics, trust boundaries, concurrency, audit failure handling, and recovery; Go allows the project to focus on those areas.

## Consequences

Go's runtime and garbage collector make measurement of allocation, memory growth, and tail latency necessary. Choosing Go does not establish the performance targets in [benchmark conditions](../benchmark-conditions.md); reproducible results must demonstrate them.

Goroutines and channels do not automatically provide safe concurrency or bounded resource use. Implementations must enforce queue and worker limits, propagate cancellation, synchronize snapshot activation, and test races and shutdown behavior explicitly.

Dependencies require the review described in [CONTRIBUTING.md](../../CONTRIBUTING.md). This language choice does not establish air-gapped deployment, HA, or gateway support.

Revisit this decision only if measured requirements expose a limitation that cannot reasonably be addressed within the Go implementation.
