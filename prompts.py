"""
Prompts for the local LLM pentesting assistant.

This module contains system prompts and templates for generating
context-aware pentesting advice using a local language model.
"""

PENTEST_SYSTEM_PROMPT = """You are a penetration testing assistant designed to help authorized security professionals.

CORE PRINCIPLES:
- Only provide guidance for AUTHORIZED penetration testing with explicit written permission
- Always emphasize scope boundaries, rules of engagement (ROE), and safe testing practices
- Prefer non-destructive validation steps over aggressive exploitation
- Focus on evidence collection, risk assessment, and professional reporting
- When in doubt about authorization, ask for scope clarification

RESPONSE STYLE:
- Be concise and actionable
- Structure responses with clear steps or bullet points
- Include risk levels (Critical/High/Medium/Low) when relevant
- Suggest evidence to collect for reporting
- Recommend remediation alongside findings

SAFETY BOUNDARIES:
- Refuse requests for unauthorized access or illegal activity
- Don't provide step-by-step exploitation without ROE confirmation
- Avoid destructive commands (rm, dd, format, etc.)
- Don't generate malware, persistence mechanisms, or stealth techniques for unauthorized use

When analyzing services or providing recommendations, always consider:
1. Is this within the authorized scope?
2. What's the business risk if this vulnerability exists?
3. What evidence should be collected?
4. What's the recommended remediation?
5. Are there safer ways to validate the finding?

You are helping a security professional improve their authorized testing methodology and reporting quality."""

SCAN_ANALYSIS_TEMPLATE = """Analyze these scan results from an authorized penetration test:

SERVICES FOUND:
{services_summary}

ENGAGEMENT CONTEXT:
- Scope: {scope}
- Testing Phase: {phase}

Provide:
1. Risk prioritization of discovered services
2. Recommended testing approach for each service
3. Evidence collection suggestions
4. Any immediate security concerns

Format as structured recommendations suitable for a professional pentest."""

SERVICE_DEEP_DIVE_TEMPLATE = """Provide detailed pentesting guidance for this service:

SERVICE: {service_name}
PORT: {port}
VERSION: {version}
CONTEXT: {context}

Include:
1. Common vulnerabilities for this service/version
2. Safe enumeration techniques (authorized scope only)
3. Configuration security checks
4. Evidence to collect
5. Reporting considerations

Focus on professional methodology within authorized scope."""

REPORT_GENERATION_TEMPLATE = """Generate a professional security finding based on this information:

FINDING: {finding_title}
AFFECTED SERVICE: {service_details}
DISCOVERY METHOD: {how_found}
SCOPE: {engagement_scope}

Create a structured finding with:
1. Executive Summary
2. Technical Details
3. Risk Rating (with justification)
4. Business Impact
5. Remediation Steps
6. Validation Steps

Format for inclusion in a professional penetration test report."""


def build_scan_context(
    services: list, scope: str = "Not specified", phase: str = "Discovery"
) -> str:
    """
    Build context for LLM scan analysis.

    Args:
        services: List of (port, service, version) tuples from parser
        scope: Engagement scope description
        phase: Current testing phase

    Returns:
        Formatted context string for the LLM
    """
    if not services:
        return "No services detected in scan output."

    services_summary = []
    for port, service, version in services:
        risk_indicator = "🔴" if service in ["ssh", "rdp", "smb"] else "🟡"
        services_summary.append(f"  {risk_indicator} {port} - {service} ({version})")

    return SCAN_ANALYSIS_TEMPLATE.format(
        services_summary="\n".join(services_summary), scope=scope, phase=phase
    )


def build_service_context(
    port: str, service: str, version: str, context: str = ""
) -> str:
    """
    Build context for detailed service analysis.

    Args:
        port: Service port (e.g., "22/tcp")
        service: Service name (e.g., "ssh")
        version: Service version string
        context: Additional context about the service

    Returns:
        Formatted context string for the LLM
    """
    return SERVICE_DEEP_DIVE_TEMPLATE.format(
        service_name=service,
        port=port,
        version=version or "Version not detected",
        context=context or "Standard service discovery",
    )
