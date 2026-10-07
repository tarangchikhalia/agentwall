# Security Policy

Security is taken seriously. We appreciate responsible reports from security researchers, contributors, and users.

## Supported Versions

Security fixes are generally applied to the latest released version of the project.

| Version                     | Supported    |
| --------------------------- | ------------ |
| Latest release              | Yes          |
| Older releases              | Best effort  |
| Unreleased development code | No guarantee |

As the project matures, this policy may be updated to define explicit long-term support versions.

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues, discussions, pull requests, or other public channels.**

If you believe you have discovered a security vulnerability, report it privately using one of the following methods:

1. Use GitHub's **Private Vulnerability Reporting** feature, if enabled for this repository.
2. Email the maintainers with title `[SECURITY]` at:

   `tarang.chikhalia@gmail.com`

Please include as much of the following information as possible:

- A description of the vulnerability
- The affected component or version
- Steps to reproduce the issue
- A proof of concept, if available
- The potential security impact
- Known mitigations or workarounds
- Any relevant logs, traces, screenshots, or configuration
- Whether you believe the vulnerability is already being exploited

Avoid including sensitive credentials, personal information, production data, or third-party secrets in the report.

## What to Expect

After receiving a vulnerability report, maintainers will attempt to:

- Acknowledge receipt within 5 business days
- Validate and reproduce the reported issue
- Assess its severity and affected versions
- Coordinate remediation and disclosure
- Release a fix when appropriate
- Credit the reporter if requested and appropriate

Response times may vary depending on project availability and the complexity of the vulnerability.

## Coordinated Disclosure

Please allow maintainers reasonable time to investigate and remediate a vulnerability before publicly disclosing it.

If a vulnerability is confirmed, maintainers may:

1. Develop and review a fix privately.
2. Prepare patched releases.
3. Publish a security advisory.
4. Release technical details after users have had a reasonable opportunity to upgrade.

Reporters are encouraged to coordinate disclosure timing with the maintainers.

## Security Advisories

Confirmed vulnerabilities may be published through GitHub Security Advisories or another appropriate disclosure mechanism.

Advisories may include:

- Affected versions
- Severity
- Impact
- Mitigations
- Fixed versions
- Upgrade instructions
- CVE identifiers, when applicable

## Severity Assessment

Security issues may be evaluated using factors such as:

- Exploitability
- Required privileges
- Attack complexity
- User interaction
- Confidentiality impact
- Integrity impact
- Availability impact
- Scope of affected deployments

Where appropriate, maintainers may use CVSS as one input when determining severity.

## Security Best Practices

Users should:

- Keep the project and its dependencies up to date.
- Review configuration before production deployment.
- Use least-privilege permissions.
- Protect secrets and credentials using an appropriate secret-management system.
- Avoid committing credentials, tokens, private keys, or sensitive configuration to source control.
- Restrict network access to services that do not need to be publicly accessible.
- Review release notes and security advisories before upgrading.

## Dependency Vulnerabilities

If a vulnerability originates in a third-party dependency, maintainers may:

- Upgrade the affected dependency
- Apply a temporary mitigation
- Replace the dependency
- Document the issue until an upstream fix is available

Dependency scanner findings that do not represent an exploitable vulnerability in this project may be handled as normal maintenance issues rather than security vulnerabilities.

## Scope

Examples of issues that are generally considered security vulnerabilities include:

- Authentication or authorization bypass
- Privilege escalation
- Remote code execution
- Command or code injection
- SQL or query injection
- Path traversal
- Server-side request forgery
- Unauthorized access to sensitive information
- Improper isolation between users or workloads
- Cryptographic weaknesses with practical security impact
- Secret or credential exposure
- Significant denial-of-service vulnerabilities

The following generally do not require private security reporting unless they have meaningful security impact:

- General bugs
- Feature requests
- Missing security hardening recommendations
- Dependency scanner warnings without demonstrated impact
- Issues requiring unrealistic or already-compromised environments

## Safe Harbor

Security research performed in good faith and consistent with this policy is welcome.

Maintainers will not intentionally pursue action against researchers who:

- Avoid privacy violations and destruction of data
- Avoid disrupting project infrastructure or third-party systems
- Do not exploit vulnerabilities beyond what is necessary to demonstrate impact
- Report vulnerabilities privately and provide reasonable time for remediation
- Comply with applicable laws

This safe-harbor statement applies only to systems and software controlled by this project and does not authorize testing of third-party systems.
