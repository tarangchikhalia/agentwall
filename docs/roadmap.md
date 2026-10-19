# AgentWall roadmap

One service, five internal modules — Gate, Delegate, Guard, Codex, Watchtower — delivered through capability slices. 

Each milestone follows **design → plan → implement → verify** and has acceptance evidence and a release tag. 

Modules are neither separate deployments nor sequential stages. End-to-end verification starts in v0.2.0.

| Milestone | Scope and completion evidence | Duration | Baseline target window |
| --- | --- | --- | --- |
| v0.1.0 — Test environment | Two or three agents, controlled resources, repeatable permitted/denied/invalid-authority fixtures; documented expectations and direct-path latency, throughput and error measurements. Harness completion does not establish enforcement. | 2 weeks | October 19–November 1, 2026 |
| v0.2.0 — Enforce and audit one action | One integration and bounded action/resource, verified agent identity, minimal policy, enforcement and correlated evidence. Allow reaches resource; deny never reaches it; both recorded; decisions and observed outcomes distinguishable. | 5 weeks | November 2–December 6, 2026 |
| v0.3.0 — Delegated authority | Bounded delegation and initial identity-provider integration; represented principal and authority source/scope established. Forged, expired, invalid and insufficient authority cannot authorize execution; principals attributable in evidence. | 6 weeks | December 7, 2026–January 17, 2027 |
| v0.4.0 — Organization/team policies | Explicit scope/combination semantics, validation, versioning and safe activation. Conflicts predictable, invalid activation rejected, evaluated version recorded. | 5 weeks | January 18–February 21, 2027 |
| v0.5.0 — Context and obligations | Bounded contextual rules and one complete approval/obligation workflow bound to the action executed. Missing context/unmet obligations block; satisfied conditions permit intended action. | 6 weeks | February 22–April 4, 2027 |
| v0.6.0 — Reliability and audit integrity | Dependency failures, policy updates, audit durability/delivery failure, detectable gaps, tamper evidence, operational visibility and controlled-load overhead. Demonstrate integrity and explicit failure behavior against a budget defined during design. | 6 weeks | April 5–May 16, 2027 |
| v0.7.0 — Product qualification | Realistic integrated workflows, negative security cases, deployment/recovery/adverse conditions, documentation and findings resolved. Repeatable acceptance suite demonstrates enforcement, attribution, integrity and operations together. | 4 weeks | May 17–June 13, 2027 |
| Contingency | Holidays, integration uncertainty, findings and rework | 4–8 weeks | Buffer through July–August 2027 |

Patch releases fix a milestone (for example v0.2.1). v1.0.0 requires a separate stable-public-contract decision supported by qualification and practical feedback; v0.7.0 does not automatically imply readiness.

One integration path first, existing identity/secrets infrastructure, minimal management interface, bounded policy/delegation and one initial approval workflow underpin these estimates. Extra adapters/providers and polished UI need separate estimates. Delegation and approval/action binding are the largest uncertainties. Project/agent policy scopes have no separately committed delivery milestone.
