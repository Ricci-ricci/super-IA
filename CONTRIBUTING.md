# Contributing to superPENTESTING

Thanks for your interest in contributing. This project is intended to support **authorized** security testing and defensive workflows. Contributions should improve safety, usability, and reproducibility for legitimate pentesting engagements.

## Code of conduct

Be respectful, professional, and constructive. Assume good intent and focus on improving the project.

## Scope and project goals

Contributions are welcome in these areas:

- Project structure, developer experience, docs, and examples
- Prompting patterns and guardrails for authorized testing
- Reporting templates and engagement workflows
- Integrations that help parse, organize, and summarize **user-provided** tool output
- Testing, CI, linting, packaging, and release automation

Contributions are **not** welcome if they primarily enable misuse, including:

- Guidance or automation for unauthorized access
- Malware development or deployment
- Credential theft, phishing, persistence, evasion, or stealth techniques aimed at real-world abuse
- Features that remove or weaken safety boundaries (scope enforcement, disclaimers, logging controls, consent checks)

If you're unsure whether something crosses the line, open an issue and discuss first.

## Legal & ethical requirements

By contributing, you agree that:

- You will not add content that encourages or facilitates illegal activity.
- Any examples should be framed for **authorized** engagements only.
- You will respect applicable laws, rules of engagement (ROE), client contracts, and privacy obligations.

## How to contribute

### 1) Discuss changes early (recommended)

Before large changes, open an issue describing:

- The problem you’re solving and why it matters
- Proposed approach and alternatives
- Any security/privacy implications
- How you plan to test the change

### 2) Make focused pull requests

- Keep PRs small and focused (one logical change per PR).
- Include documentation updates when changing behavior or configuration.
- Add tests for new functionality or bug fixes when feasible.
- Avoid reformatting unrelated files.

### 3) Write good commit messages

Use clear, descriptive messages, e.g.:

- `docs: add reporting template example`
- `feat: add prompt guardrail for scope exclusions`
- `fix: handle empty tool output parsing`

## Development guidelines

### Documentation

- Prefer plain, explicit language.
- Avoid including real secrets, tokens, or sensitive client data.
- When showing outputs, use sanitized placeholders.

### Security & privacy

- Treat pentest artifacts as sensitive by default.
- Do not introduce telemetry that phones home without explicit opt-in.
- Avoid logging secrets; provide redaction helpers when relevant.
- Prefer least-privilege defaults.

### Prompting and model behavior

If you contribute prompts/agents/guardrails:

- Emphasize authorization, explicit scope, and ROE.
- Encourage non-destructive validation and safe rate limits.
- Avoid “unbounded” tasking (e.g., “keep trying until you succeed”).
- Require user-provided context rather than inventing targets or assumptions.

## Adding new dependencies

- Keep dependencies minimal.
- Prefer well-maintained libraries with permissive licenses.
- Document new dependencies and why they’re needed.
- Avoid dependencies that introduce high-risk behavior, unclear licensing, or supply-chain concerns.

## Reporting a security issue

If you discover a security issue in this repository:

- Do **not** open a public issue with exploit details.
- Instead, contact the maintainers privately (add contact details here once established).

## License

By contributing, you agree that your contributions will be licensed under the project’s license (see `LICENSE` if present).

---
If you have questions, open an issue with context and your proposed direction.