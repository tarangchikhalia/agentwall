# Contributing

Thank you for your interest in contributing.

Contributions may include bug fixes, documentation, tests, performance improvements, new features, design discussions, issue triage, and other improvements to the project.

By participating in this project, you agree to follow the project's [Code of Conduct](CODE_OF_CONDUCT.md).

## Before You Start

Before making a substantial change:

1. Search existing issues and pull requests to determine whether the work is already being discussed or implemented.
2. For significant features, architectural changes, or changes that introduce new dependencies, open an issue before implementation.
3. Keep changes focused. Large unrelated changes should normally be submitted as separate pull requests.

Small bug fixes, documentation improvements, tests, and similarly scoped changes generally do not require prior discussion.

## Development Workflow

This project uses a **fork-based contribution model**.

Do not create feature branches directly in the upstream repository unless you are a maintainer explicitly working in that repository.

### 1. Fork the Repository

Create a fork of the repository under your GitHub account or organization.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/<repository>.git
cd <repository>
```

### 3. Add the Upstream Repository

```bash
git remote add upstream https://github.com/<upstream-owner>/<repository>.git
```

Verify the configured remotes:

```bash
git remote -v
```

You should normally have:

- `origin` pointing to your fork
- `upstream` pointing to the official repository

### 4. Synchronize Your Fork

Before starting new work:

```bash
git fetch upstream
git checkout main
git rebase upstream/main
git push origin main
```

If the project uses a default branch other than `main`, substitute that branch name accordingly.

### 5. Create a Branch

Create a separate branch for each contribution:

```bash
git checkout -b <type>/<short-description>
```

Examples:

```text
fix/request-timeout
feat/runtime-isolation
docs/security-policy
test/authentication
```

Avoid making contributions directly from your fork's default branch.

### 6. Make Your Changes

Keep changes:

- Focused on one logical problem
- Consistent with the existing architecture and coding conventions
- Backward compatible where practical
- Covered by tests where applicable
- Documented when they affect user-facing behavior

Avoid unrelated formatting, refactoring, or dependency changes in the same pull request unless they are required for the contribution.

## Development Setup

Follow the setup instructions in the project's README or development documentation.

Before submitting a pull request, ensure you can:

- Build the project successfully
- Run the relevant test suite
- Run configured linters and formatters
- Reproduce the behavior affected by your change

Project-specific commands should be documented in the repository as the project evolves.

## Coding Standards

Contributions should:

- Follow the established code style
- Prefer clear and maintainable implementations over unnecessary complexity
- Use descriptive names
- Handle errors explicitly
- Avoid unnecessary abstractions
- Avoid introducing dependencies without a clear justification
- Include comments when behavior or reasoning would otherwise be difficult to understand

Do not commit:

- API keys
- Passwords
- Authentication tokens
- Private keys
- Production credentials
- Customer data
- Personal information
- Generated secrets
- Sensitive configuration

If a secret is accidentally committed, treat it as compromised and rotate it immediately.

## Tests

Changes should include appropriate tests whenever practical.

Depending on the change, this may include:

- Unit tests
- Integration tests
- End-to-end tests
- Regression tests
- Security tests
- Performance tests

Bug fixes should ideally include a regression test that fails before the fix and succeeds afterward.

Do not modify or remove tests solely to make a failing implementation pass unless the test itself is incorrect.

## Documentation

Update documentation when a change affects:

- Public APIs
- Configuration
- Installation
- Deployment
- Command-line interfaces
- Security behavior
- User-visible behavior
- Architecture or operational requirements

Code and documentation should be updated in the same pull request when practical.

## Commit Guidelines

Use clear, descriptive commit messages.

A recommended format is:

```text
<type>: <description>
```

Examples:

```text
feat: add isolated execution environment
fix: prevent duplicate session creation
docs: document authentication configuration
test: add coverage for expired credentials
refactor: simplify policy evaluation
```

Common commit types include:

```text
feat
fix
docs
test
refactor
perf
build
ci
chore
security
```

Keep commits logically organized. Contributors may be asked to rebase, squash, or reorganize commits before a pull request is merged.

## Keep Your Branch Current

Before submitting or updating a pull request:

```bash
git fetch upstream
git rebase upstream/main
```

Resolve conflicts locally and update your fork:

```bash
git push --force-with-lease origin <your-branch>
```

Use `--force-with-lease` rather than `--force`.

## Submitting a Pull Request

Push your branch to your fork:

```bash
git push -u origin <your-branch>
```

Then open a pull request from:

```text
<your-fork>:<your-branch>
```

into:

```text
<upstream-repository>:main
```

Pull requests should contain:

- A clear title
- A description of the problem
- An explanation of the proposed solution
- Relevant issue references
- Testing performed
- Documentation changes, when applicable
- Screenshots, logs, or benchmarks when relevant
- Any known limitations or follow-up work

Prefer small, focused pull requests. Smaller changes are generally easier to review, test, and merge safely.

## Pull Request Checklist

Before requesting review, verify that:

- [ ] The change addresses a single clear problem.
- [ ] The branch is based on the current upstream default branch.
- [ ] The project builds successfully.
- [ ] Relevant tests pass.
- [ ] New behavior has appropriate tests.
- [ ] Formatting and lint checks pass.
- [ ] Documentation has been updated where necessary.
- [ ] No credentials or sensitive information are included.
- [ ] No unrelated changes are included.
- [ ] The pull request description explains the motivation and implementation.

## Pull Request Reviews

Maintainers may request changes for:

- Correctness
- Security
- Maintainability
- Performance
- Architecture
- API compatibility
- Testing
- Documentation
- Project scope

A pull request may go through several review iterations before being accepted.

Address review feedback with additional commits or rebased changes as appropriate.

Resolve review conversations only after the concern has been addressed or agreement has been reached.

## Automated Checks

Pull requests may be required to pass automated checks such as:

- Build validation
- Unit tests
- Integration tests
- Linting
- Formatting
- Static analysis
- Dependency scanning
- Security scanning
- License checks

Required checks must pass before merging unless a maintainer explicitly approves an exception.

## Merge Strategy

Maintainers determine the appropriate merge strategy.

The project may use:

- Squash merging
- Rebase merging
- Merge commits

Contributors should not depend on their original commit structure being preserved.

## Issues

Before opening an issue:

1. Search existing issues.
2. Confirm the issue applies to a supported version.
3. Collect enough information to reproduce the problem.

Bug reports should ideally include:

- Project version or commit
- Operating system
- Runtime or environment information
- Configuration relevant to the issue
- Expected behavior
- Actual behavior
- Reproduction steps
- Minimal reproduction when possible
- Relevant logs or error messages

Do not include secrets or sensitive information.

## Feature Requests

Feature requests should explain:

- The problem being solved
- The intended users
- The proposed behavior
- Existing workarounds
- Alternatives considered

Requests framed around a concrete problem are easier to evaluate than requests for a particular implementation.

## Security Issues

Do **not** open public issues for suspected security vulnerabilities.

Follow the instructions in [SECURITY.md](SECURITY.md).

## Dependencies

New dependencies should be introduced carefully.

A pull request adding a dependency should consider:

- Maintenance status
- Security history
- License compatibility
- Size and complexity
- Runtime impact
- Transitive dependencies
- Whether equivalent functionality already exists in the project

Maintainers may reject a dependency even if the implementation using it is technically correct.

## Backward Compatibility

Avoid breaking public interfaces without prior discussion.

Breaking changes should normally:

- Have a clear justification
- Be discussed before implementation
- Include migration guidance
- Be clearly documented
- Follow the project's versioning policy

## AI-Assisted Contributions

AI-assisted development tools may be used, but contributors remain responsible for everything they submit.

Contributors must:

- Review and understand generated code
- Verify correctness
- Verify licensing and provenance where applicable
- Test generated changes
- Ensure generated code does not introduce secrets or insecure behavior
- Be able to explain the implementation during review

AI-generated output is not exempt from normal review, testing, security, or licensing requirements.

## Licensing

By submitting a contribution, you represent that you have the right to submit the work under the project's license.

Unless explicitly stated otherwise, contributions are made under the same license as the project.

Do not submit code copied from sources with incompatible licenses.

## Contributor License Agreement

This project does not require a Contributor License Agreement unless explicitly stated elsewhere.

If this policy changes, contributors will be informed before a CLA becomes required for future contributions.

## Maintainer Discretion

Submitting a contribution does not guarantee that it will be merged.

Maintainers may decline contributions because of:

- Project scope
- Architecture
- Maintenance burden
- Security considerations
- Compatibility concerns
- Duplication
- Insufficient testing
- Long-term project direction

Where practical, maintainers will explain the reason.
