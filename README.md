# AgentWall

## Overview

AgentWall is an AI security and authorization platform designed to enforce organization and team policies and make agent actions accountable:

**Which agent took what action, under whose authority, on behalf of whom?**

Before execution, it determines whether an agent may perform an action on a resource under applicable policies, delegated authority and context.

**Current status:** pre-alpha

## Architecture

AgentWall is one deployable service with five separated internal modules:

| Modules | Responsibility |
| --- | --- |
| **Gate** | Intercept and normalize requests, coordinate with other modules for authorization, enforcement and trace, and forward permitted actions. |
| **Delegate** | Verify agent identity, represented principal (user), the source and scope of delegated authority (resource). |
| **Guard** | Evaluate policies against trusted context and return decisions and required approvals or obligations. |
| **Codex** | Define, validate, test, version and activate policies; reuse Guard's evaluator for policy tests. |
| **Watchtower** | Trace and record the actions of AgentWall in a temperproof audit trail |

Guard decides; Gate enforces. Authorization failures fail closed. An allow decision or forwarding attempt does not establish successful execution; evidence must preserve uncertain outcomes.

Mandatory runtime isolation is outside AgentWall's product responsibility.

See the [architecture](docs/architecture.md).

## Quick Start

Install Go 1.26.9, as declared in `go.mod`, and Make. From the repository root:

```sh
make build
./bin/agentwall
./bin/agentwall -help
```

The default command prints the foundation status and exits. It does not enforce or forward agent actions.

For development checks:

```sh
make test
make check
```

Race tests require CGO and a C compiler. Full checks include a vulnerability scan and may require network access. See the [development guide](docs/development.md) for the workflow and legacy policy-test context.

## Roadmap

Each milestone follows **design → plan → implement → verify**, with defined acceptance evidence and a release tag.

| Milestone | Capability |
| --- | --- |
| **v0.1.0** | Reproducible test environment and direct-path measurements. |
| **v0.2.0** | Enforce and audit one action; begin end-to-end verification. |
| **v0.3.0** | Verify delegated authority and principal attribution. |
| **v0.4.0** | Apply organization/team policies with safe policy management. |
| **v0.5.0** | Enforce contextual conditions and one approval or obligation workflow. |
| **v0.6.0** | Strengthen operational reliability, audit durability and tamper evidence. |
| **v0.7.0** | Qualify the integrated product through realistic workflows and operational testing. |

See the [detailed roadmap](docs/roadmap.md). Immediate work is the [v0.1.0 test-environment design](docs/milestones/v0.1.0.md).

## Guidelines

- Build complete, bounded capability slices across the internal concerns they require.
- Define trust assumptions, contracts and acceptance criteria before dependent implementation.
- Verify expected outcomes, negative cases, relevant failures and integration throughout development.
- Distinguish planned capabilities from implemented and measured behavior.
- Highlight foundational contradictions and confirm deliberate changes with Tarang before modifying the baseline.

The [foundational plan](docs/foundational-plan.md) governs current development. Consult the [open decisions](docs/open-decisions.md) for unresolved choices and the [documentation index](docs/README.md) for supporting documents.

## Licensing

AgentWall is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
