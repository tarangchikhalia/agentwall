# Open design decisions

The foundational plan establishes purpose, concerns and sequence. It does not finalize the choices below. Resolve each through milestone design before its implementation; the milestone column identifies the relevant capability, not a prohibition on earlier design.

| Area | Decisions to resolve | Relevant milestone |
| --- | --- | --- |
| Environment | Two or three concrete agents, protected resources, scenario fixtures, repeatable runner and acceptance criteria | v0.1.0 |
| Measurements | Direct baseline methodology; later numeric overhead budget, workload conditions and thresholds | v0.1.0; v0.6.0 |
| First enforcement | One integration protocol, bounded action/resource, identity verification, internal interfaces and decision/audit schemas | v0.2.0 |
| Delegation | Initial identity provider, credential lifecycle, authority provenance, scope and representation semantics | v0.3.0 |
| Policy management | Organization/team precedence, inheritance/conflicts, validation, versioning and safe activation | v0.4.0 |
| Context and obligations | Supported contextual rules, missing context, one approval workflow and exact execution binding | v0.5.0 |
| Audit integrity | Storage, delivery/durability guarantees, detectable gaps and tamper-evidence mechanism | Basic evidence v0.2.0; stronger guarantees v0.6.0 |
| Qualification | Realistic workflows, deployment, recovery, adverse conditions and acceptance suite | v0.7.0 |
| Future scope | Project/agent policy scope timing, extra adapters/providers and polished UI estimates | Uncommitted |
| Stable contract | Public API compatibility commitments and readiness evidence | Separate v1.0.0 decision |

Existing identity and secrets infrastructure is integrated, not rebuilt. Customer infrastructure prevents enforcement bypass; mandatory runtime isolation is outside product responsibility. Unknown execution outcomes must remain unknown in evidence. Historical queue, API, storage and policy specifications are reference material rather than answers to these decisions.
