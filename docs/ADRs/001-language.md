# Language Selection

We select [Go](https://go.dev) as the choice of programming language for this project.

## Why Go?

1. This project in its simplest term is a proxy gateway that accepts the requests, analyze the request and either forward or deny the request based on the policy check.
This require multiple concurrent sessions, long-lived streams, etc. Go provide extensive support for such operations. 
2. Ecosystem of Go is matured. Most of the SDKs, and external adapters we depend on has official support for Go.
3. Go produce static binaries and small images which suits onpremise or airgapped installation.
4. Go allow faster development of the project.

## What other option were considered?

Rust was considered during this evaluation. Rust's superpower is system-level development. Though Rust is one of the best choice for this project and ticks all our requirement boxes, the slow development speed, a steep learning curve to learn the programming language made us choose Go.

## Future Notes

This decision can change in future if Go cannot meet our requirements. A full evaluation will be done in future.