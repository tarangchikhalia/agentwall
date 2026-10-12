.PHONY: build test fmt fmt-check vet dependencies security check

build:
	CGO_ENABLED=0 go build -trimpath -o bin/agentwall .

test:
	go test -race ./...

fmt:
	gofmt -w $$(git ls-files --cached --others --exclude-standard '*.go')

fmt-check:
	@files=$$(gofmt -l $$(git ls-files --cached --others --exclude-standard '*.go')) || exit 1; \
	if [ -n "$$files" ]; then echo "Unformatted Go files:"; echo "$$files"; exit 1; fi

vet:
	go vet ./...

dependencies:
	go mod verify
	go mod tidy -diff

security:
	go run golang.org/x/vuln/cmd/govulncheck@v1.1.4 ./...

check: fmt-check vet dependencies test build security
