.PHONY: build test policy-test fmt fmt-check vet dependencies security check

PYTHON ?= python3

build:
	CGO_ENABLED=0 go build -trimpath -o bin/agentwall .

test:
	go test -race ./...

policy-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests/policy_schema -v

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
