# Security Policy

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, use GitHub's [private vulnerability reporting](https://github.com/patarra/captioneer/security/advisories/new).

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

You can expect an acknowledgement within 48 hours and a fix or mitigation plan within 14 days depending on severity.

## Dependency updates

Dependencies are monitored automatically via [Dependabot](https://docs.github.com/en/code-security/dependabot). Security patches are reviewed and merged promptly.

## Scope

captioneer is a local CLI tool — it does not run a server, handle user accounts, or transmit data beyond translation requests to Google Translate. The main areas of concern are:

- Malicious input files causing unexpected behaviour (video or SRT files)
- Command injection via filenames passed to ffmpeg
