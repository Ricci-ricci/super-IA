from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from knowledge_base import INTENTS, SERVICES_ACTIONS
from parser import get_nmap_imput, parse_nmap

# Try to import requests, fall back gracefully if not available
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class OllamaClient:
    """Simple Ollama HTTP client for local LLM integration."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.available = HAS_REQUESTS

    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Send a prompt to Ollama and return the response."""
        if not self.available:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "system": system_prompt,
                    "prompt": user_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                    },
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"[DEBUG] Ollama error: {response.status_code}")
                return None

        except Exception as e:
            print(f"[DEBUG] Ollama connection failed: {e}")
            return None


def detect_intent(user_text: str) -> str:
    """
    Very small keyword-based intent detector.

    IMPORTANT:
    - Uses token/word matching (not substring matching) to avoid cases like:
      "question" containing "q" and falsely triggering "exit".
    """
    text = (user_text or "").strip().lower()
    if not text:
        return "unknown"

    # Tokenize into words (letters/numbers/underscore). This ignores punctuation.
    tokens = set(re.findall(r"\b\w+\b", text))

    for intent, keywords in INTENTS.items():
        for kw in keywords:
            # match whole tokens only
            if kw in tokens:
                return intent

    return "unknown"


def print_help() -> None:
    print(
        "\nCommands / intents:\n"
        "- greeting: hello / hi / hey\n"
        "- scan: scan / nmap / analyze  (then paste Nmap output)\n"
        "- service: type a service name like ssh/http/https/smb/etc.\n"
        "- exit: exit / quit / bye\n"
        "\nHow to paste:\n"
        "- After entering scan mode, paste multi-line Nmap output\n"
        "- Press Enter on an empty line to finish\n"
    )


def build_pentesting_context(parsed_services: list) -> str:
    """Build structured context for LLM from parsed services."""
    if not parsed_services:
        return "No open services detected in scan."

    context_parts = [
        "SCAN RESULTS:",
        f"Found {len(parsed_services)} open service(s):",
        "",
    ]

    for port, service, version in parsed_services:
        context_parts.append(f"- {port}: {service} {version}")

    context_parts.extend(
        [
            "",
            "ENGAGEMENT CONTEXT:",
            "- This is an authorized penetration test",
            "- Focus on safe, non-destructive testing methods",
            "- Prioritize evidence collection and documentation",
            "- Suggest specific validation steps within scope",
        ]
    )

    return "\n".join(context_parts)


def get_llm_scan_analysis(
    parsed_services: list, llm_client: OllamaClient
) -> Optional[str]:
    """Get AI analysis of scan results using local LLM."""
    system_prompt = """You are a pentesting assistant for AUTHORIZED security assessments only.

Your role:
- Analyze scan results and provide actionable testing guidance
- Prioritize findings by potential security impact
- Suggest safe, non-destructive validation steps
- Focus on evidence collection and documentation
- Always emphasize authorized testing within scope

Format your response with:
1. Priority assessment (High/Medium/Low risk services)
2. Specific testing recommendations per service
3. Evidence collection guidance
4. Next steps within scope

Keep responses concise but detailed enough for action."""

    context = build_pentesting_context(parsed_services)
    user_prompt = f"{context}\n\nPlease analyze these services and provide testing recommendations."

    return llm_client.generate(system_prompt, user_prompt)


def show_scan_results(nmap_text: str, llm_client: OllamaClient) -> None:
    parsed = parse_nmap(nmap_text)

    if not parsed:
        print(
            "I couldn't find any open services in that input.\n"
            "Make sure you pasted Nmap normal output that includes the line:\n"
            "  PORT  STATE  SERVICE  VERSION\n"
        )
        return

    # Try to get AI analysis first
    llm_analysis = get_llm_scan_analysis(parsed, llm_client)

    if llm_analysis:
        print("=== AI ANALYSIS ===")
        print(llm_analysis)
        print("\n" + "=" * 50)
        print("=== SERVICE DETAILS ===")

    # Always show the traditional breakdown as backup/supplement
    for port, service, version in parsed:
        print(f"\nPort: {port}, Service: {service}, Version: {version}")

        actions = SERVICES_ACTIONS.get(
            service,
            "No specific actions found for this service. Consider general pentesting techniques.",
        )
        print(f"Recommended Actions: {actions}")

    if not llm_analysis and HAS_REQUESTS:
        print(
            "\n[INFO] Local LLM not available. Install Ollama and pull a model (e.g., 'ollama pull llama3.2:3b') for AI analysis."
        )
    elif not HAS_REQUESTS:
        print("\n[INFO] Install 'requests' library for AI analysis features.")


def main() -> None:
    # Initialize LLM client
    llm_client = OllamaClient()

    print("superPENTESTING - tiny pentest helper (authorized use only).")
    if llm_client.available:
        print(f"AI analysis enabled (model: {llm_client.model})")
    else:
        print("AI analysis disabled (install 'requests' and Ollama for AI features)")
    print("Type 'help' for commands.\n")

    while True:
        try:
            user_text = input(">").strip()
        except EOFError:
            print("\nbye. Happy pentesting!")
            return

        if not user_text:
            continue

        # Explicit help shortcut (kept simple on purpose)
        if user_text.lower() in {"help", "?"}:
            print_help()
            continue

        intent = detect_intent(user_text)

        if intent == "greeting":
            print(
                "Hey! You can say 'scan' to paste an Nmap scan, or type a service like 'ssh'/'http'."
            )
            continue

        if intent == "exit":
            print("bye. Happy pentesting!")
            return

        if intent == "scan":
            print(
                "Paste your Nmap scan here — I'm gonna analyze it. (Empty line to finish)\n"
            )
            nmap_text = get_nmap_imput()
            if nmap_text.strip().lower() in {"exit", "quit", "bye"}:
                print("bye. Happy pentesting!")
                return
            show_scan_results(nmap_text, llm_client)
            continue

        if intent == "question":
            print(
                "Tell me what you want to do.\n"
                "- Say 'scan' to paste an Nmap scan\n"
                "- Or type a service name like 'ssh' or 'http'\n"
            )
            continue

        # Fallback: treat the input as a service name if it matches knowledge base
        maybe_service = user_text.strip().lower()
        if maybe_service in SERVICES_ACTIONS:
            print(f"Exploring {maybe_service} service...\n")
            print(SERVICES_ACTIONS[maybe_service])
            continue

        print(
            "I don't understand. Type 'help', say 'scan', or type a known service (e.g., ssh/http)."
        )


if __name__ == "__main__":
    main()
