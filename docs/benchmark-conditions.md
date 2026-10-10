# Benchmark conditions

Supported interfaces and versions follow [support-matrix.md](support-matrix.md). Performance targets follow [requirements.md](requirements.md).

## Targets

| Measure | Target |
| --- | --- |
| Completed requests | At least 1,000 requests/second |
| Average gateway-added latency | At most 10 ms |
| Concurrent requests | 100 |
| Initial identity population | 1,000 users and 100 agents |
| Maximum MCP request body | 4 MiB; each file at most 512 KiB |
| Maximum REST/LLM API request body | 20 MiB |

The initial identity population is a baseline. Larger populations must separately validate the requirement for thousands of users and hundreds of agents.

## Measurement and acceptance

- Gateway-added latency includes validation, identity, policy, credential issuance, durable audit, queueing, and forwarding overhead. Exclude measured upstream execution and human approval wait; avoid double-counting overlapping work.
- Report offered versus completed throughput, errors/timeouts, average and p95/p99 latency, CPU/memory, concurrent requests, and active streams. Fast failures or pending approvals do not count toward allowed-call throughput.
- Each measured run must meet 1,000 completed requests/second and average added latency at most 10 ms within the agreed error threshold. Preserve raw results and reproduction commands.
- Denied/pending calls must not reach upstreams; required dependency failures must fail closed. Disabled security controls invalidate the result.

Reference hardware, workload proportions, run timing, error threshold, and A2A payload limits remain to be agreed before release acceptance. These benchmarks do not establish the separate 99% availability requirement.
