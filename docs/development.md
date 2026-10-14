# Development

Install Go 1.26.9 (the version in `go.mod`) and Make. CI uses the same Go version on Ubuntu 24.04. Race tests require CGO support and a C compiler; the executable builds with CGO disabled.

```sh
make build       # bin/agentwall
make test        # Full suite with race detection
make fmt        # Format Go sources
make check      # Formatting, vet, modules, tests, build, vulnerability scan
./bin/agentwall
./bin/agentwall -help
```

The executable prints its foundation status and exits without opening a listener. It does not implement proxy functionality. Exit codes: 0 for normal output/help, 2 for invalid arguments, 1 for output failure.

The project root owns executable startup and CLI tests. Introduce `internal/` packages as implementation needs arise. The module is `github.com/tarangchikhalia/agentwall`; the application currently uses only the standard library, so no `go.sum` is needed.

`make security` runs pinned `govulncheck` v1.1.4. Initial tool downloads and vulnerability database access require network access. CI actions are pinned to official commit SHAs with read-only permissions and no persisted checkout credential. Update pins deliberately; failures in formatting, tests, module consistency, or vulnerability scanning fail CI.

Before adding a dependency, follow the maintenance, security, and license review in [CONTRIBUTING.md](../CONTRIBUTING.md). Run `go mod tidy` and commit `go.sum` when dependencies are added. Keep generated binaries in ignored `bin/`.
