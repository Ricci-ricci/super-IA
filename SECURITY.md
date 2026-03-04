# Security Policy

This document describes how to report security vulnerabilities for **superPENTESTING** and how maintainers handle security issues.

---

## Supported Versions

Because this project is under active development, security support is provided for the **latest `main` branch** only.

If you are using a fork or a pinned commit, please reproduce the issue on the latest `main` before reporting (when feasible).

---

## Reporting a Vulnerability

If you believe you have found a security vulnerability, please **do not** open a public GitHub issue with details.

Instead, use one of the following private channels:

1. **GitHub Security Advisories (preferred)**  
   - Go to the repository page → **Security** → **Advisories** → **Report a vulnerability**.

2. **Email (if available)**  
   - If the repository lists a security contact email in the README or profile, you may contact that address.

When reporting, please include:

- A clear description of the vulnerability and impact
- Steps to reproduce (proof-of-concept code or requests are helpful)
- Affected component(s) and version/commit hash
- Any relevant logs, stack traces, or screenshots (avoid sensitive client data)
- Your suggested fix or mitigation (optional)

### Sensitive Data Guidance

- **Do not** include real credentials, API keys, secrets, private keys, or session tokens.
- **Do not** include client/customer data.
- If you must share sensitive information to reproduce the issue, redact it or provide a minimal synthetic reproduction.

---

## What to Expect

Maintainers aim to respond to valid security reports within **7 days**.

If the report is confirmed, maintainers will:

- Work on a fix or mitigation
- Decide on a coordinated disclosure timeline (when applicable)
- Credit the reporter if requested (and appropriate)

Because project maintainers may be volunteers, exact timelines may vary.

---

## Disclosure Policy

Please allow maintainers a reasonable amount of time to address the vulnerability before public disclosure.

If you believe immediate public disclosure is necessary (e.g., active exploitation), notify maintainers first with your rationale so we can coordinate.

---

## Scope

This security policy covers vulnerabilities in this repository’s code and configuration, including:

- Dependency or supply-chain risks introduced by this repository
- Insecure defaults or unsafe recommended configurations
- Leaks of secrets committed to the repository

The following are typically **out of scope**:

- Issues in third-party services/providers outside the project’s control
- Social engineering, physical attacks, and attacks requiring unauthorized access to infrastructure not controlled by this project
- Misuse of the project in violation of law, ethics, or engagement scope

---

## Secure Development Notes

This project is intended only for **authorized** pentesting and defensive workflows. Safety and compliance are core requirements.

If you contribute code, please:

- Avoid adding features primarily intended for unauthorized access or harmful activity
- Minimize data retention and logging of sensitive content
- Never commit secrets (use environment variables and example `.env` templates instead)
- Prefer least-privilege defaults and secure-by-default configurations

---

## Acknowledgements

Thanks to the security community and all responsible reporters who help improve the safety of this project.