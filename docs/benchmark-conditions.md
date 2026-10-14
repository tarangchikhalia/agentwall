# Benchmark conditions

Date: 2026-10-14
Status: Planned v0.1 acceptance methodology; no benchmark results claimed

Targets follow [requirements](requirements.md). This measures the standalone policy and audit service, not gateway forwarding.

| Measure | v0.1 target |
| --- | --- |
| Sustained authorization throughput | At least 1,000 requests/second |
| Concurrent in-flight requests | At least 100 |
| p99 authorization processing latency | Below 5 ms, excluding network transit |
| Audit memory | Bounded under normal load and outages |
| Policy activation | No partial snapshots or interrupted in-flight evaluation |

Measure the full server path: API-key authentication, JSON decoding/validation, trusted context checks, native Go policy evaluation, audit admission, and response encoding. Separately report component timings and end-to-end client latency. Asynchronous database persistence is outside response latency but its throughput, backlog, and failures must be measured. Strict mode is the reference deployment; best-effort results must be labeled separately.

Publish hardware, OS, Go/PostgreSQL versions and evaluator semantics version, revision, policy count/complexity, input sizes, key population, queue/batch/retry settings, database placement, load generator, concurrency, warmup/run duration, and reproduction commands. Define workload proportions and acceptable error thresholds before release acceptance.

Report offered/completed throughput, allow/deny distribution, errors/timeouts, average/p50/p95/p99 latency, CPU/memory, queue depth, event persistence rate and loss. Fast errors do not satisfy throughput targets. A continuously growing backlog is not a sustainable passing result. Verify eventual persistence after a healthy run drains.

Exercise default deny, explicit deny, representative allows, concurrent reloads, invalid policies, database outages, queue saturation, and recovery. Validate strict/best-effort behavior separately; security controls must remain enabled.

The previous gateway target of at most 10 ms average added latency and 99% availability are historical future-stage inputs, not equivalent v0.1 measurements or gates. Reference hardware, precise workload, limits, durations, and error threshold remain contract work.
