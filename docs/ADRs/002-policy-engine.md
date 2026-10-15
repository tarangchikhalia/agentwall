# ADR 002: Evaluate YAML policies directly in Go

Date: 2026-10-14
Status: Accepted; replaces the earlier OPA proposal

## Context

AgentWall v0.1 needs predictable authorization decisions over principal, agent, session, action, resource, and trusted context attributes. The public policy language is a constrained YAML schema with allow/deny rules, typed comparisons, and logical composition.

OPA was initially proposed as an embedded evaluator, with YAML normalized into data consumed by a fixed Rego module. Custom Rego policies were outside the release scope. That design still required AgentWall to define and implement the YAML matching semantics while adding another language, runtime, and translation boundary.

The maintainer selected a native Go evaluator for this bounded language. The release boundary remains the policy and audit service in [ADR 003](003-policy-audit-first.md).

## Decision

Implement policy evaluation directly in Go. YAML is the authoring and serialization format; Go code defines and executes its semantics. Do not introduce an OPA dependency or translate policies into Rego.

The preparation path is YAML parsing → strict schema/type validation → immutable typed policy structures and condition trees → policy fixtures → candidate snapshot. Evaluation uses that prepared snapshot; it does not parse YAML on each authorization request.

Support the documented `path`, `resource`, and `apiPath` scope matching, `eq`, `neq`, `in`, `notIn`, `startsWith`, `gt`, `gte`, `lt`, `lte`, `range`, logical `all`, `any`, `not`, and explicit `always: true`. Keep the language finite and explicit. Do not execute arbitrary policy code, scripts, template expressions, or dynamically loaded functions.

An action is allowed only when at least one applicable allow condition is true and all applicable deny conditions are false. Unknown deny conditions block, and unknown allow conditions grant nothing. Policy order and directory location have no semantic effect. Invalid candidates cannot activate; evaluation errors return system errors and never become allow decisions.

## Rationale

- The initial language is small enough to implement through typed Go matching and comparison functions.
- Validation and evaluation share explicit types and one implementation language, making behavior easier to inspect and debug.
- Removing the YAML-to-Rego translation and separate runtime reduces implementation and dependency complexity.
- Owning the evaluator supports the project's learning objective without requiring a general-purpose policy language.

## Alternative considered

Embedded OPA provides a general policy evaluation foundation and would become relevant if a concrete future requirement demanded Rego compatibility or substantially more expressive rules. For v0.1, those capabilities do not justify the additional dependency and language boundary. Reconsider an external engine only against demonstrated needs, not speculative gateway requirements.

## Integration and lifecycle

Authentication and assertion validation precede evaluation. The evaluator receives only inputs accepted under the caller's trust constraints; it does not independently verify end-user authority or delegation.

Prepare candidates outside the request path. Validate, test, persist, and atomically activate immutable snapshots. In-flight requests may finish on an older snapshot, and decisions/events must identify the revision actually evaluated. Failed preparation leaves the active snapshot unchanged.

Persist source or normalized policy material with schema and evaluator-semantics compatibility metadata. Revalidate and rebuild runtime snapshots on recovery; do not rely on serialized executable state. Restore validated last-known-good state or remain unavailable for authorization. Rollback pinning and explicit resume follow [requirements](../requirements.md).

The audit queue and PostgreSQL persistence remain separate from evaluation. Strict audit admission is required before a successful decision response but does not provide crash durability.

## Consequences and validation

AgentWall owns all matching and condition correctness. A small evaluator still needs precise semantics: implement the AGE-7 [schema](../policy-schema-v1alpha1.md), [semantics](../policy-semantics.md), [truth tables](../policy-operator-tables-v1alpha1.md), and [Go representation contract](../policy-go-model-v1alpha1.md). The [shared corpus](../../tests/policy_schema/README.md) is executable contract evidence; its test-only Python oracle is not a production evaluator. Go implementations must consume these fixtures and add implementation-specific tests.

Bound document size, policy count, condition depth, and evaluation work. Keep evaluation free of network/database calls and shared mutable request state. Propagate cancellation and deadlines according to the request contract.

Tests must cover every operator, default deny, deny precedence, ordering independence, malformed inputs, error paths, concurrency, reload, and recovery. Fuzz parsing/validation and condition evaluation to detect crashes and unexpected acceptance. Benchmarks must distinguish preparation, evaluation, and complete authorization processing.

Compatibility changes to policy semantics must be versioned and tested against persisted bundles. This decision establishes the implementation direction; the evaluator is not yet implemented.
