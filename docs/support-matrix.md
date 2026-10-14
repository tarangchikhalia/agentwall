# Support matrix

Date: 2026-10-14
Status: Planned v0.1 contracts; no released integration support is claimed

| Interface or deployment | v0.1 direction | Status |
| --- | --- | --- |
| Authorization and audit | REST/JSON, `/v1` | OpenAPI contract pending |
| Policy authoring | YAML, `agentwall.dev/v1alpha1` | Exact schema and semantics pending |
| Policy evaluation | Native Go evaluator over typed YAML policy structures | Evaluator implementation pending |
| Caller authentication | Scoped API keys | Assertion and administration contracts pending |
| Audit storage | PostgreSQL | Supported database version and migrations pending |
| Policy source | Configured Git branch or revision; polling | Git implementation and credentials pending |
| Deployment | Docker Compose; single instance, single organization | Packaging and TLS prerequisites pending |
| Tooling | Go version declared in `go.mod` | See development setup |

MCP, LLM-provider and A2A adapters, gRPC, OIDC/mTLS, HA, Kubernetes, and arbitrary policy-code execution are outside v0.1. Prior protocol-version entries did not establish implemented support and are not v0.1 commitments. Later integrations must explicitly select and test supported versions; support for all future versions is not promised.
