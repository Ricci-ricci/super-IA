from __future__ import annotations

import re
from typing import Optional

from knowledge_base import INTENTS, SERVICES_ACTIONS
from parser import get_nmap_imput, parse_nmap

# Try to import the LLM client, fall back gracefully if not available
try:
    from llm import PENTEST_SYSTEM_PROMPT, OllamaClient

    HAS_LLM = True
except ImportError:
    HAS_LLM = False

    # Create a simple fallback that doesn't conflict with types
    class _StubClient:
        def __init__(self, base_url="http://localhost:11434", model="llama3.2:1b"):
            self.base_url = base_url
            self.model = model
            self.available = False
            self.timeout = 20

        def chat(self, model, message, system_prompt=None, temperature=0.3):
            return None

        def is_available(self):
            return False

    OllamaClient = _StubClient
    PENTEST_SYSTEM_PROMPT = ""


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


def get_llm_scan_analysis(parsed_services: list, llm_client) -> Optional[str]:
    """Get AI analysis of scan results using local LLM with quick timeout."""
    if not llm_client.is_available():
        return None

    # Very simplified prompt for CPU inference
    services_text = []
    for port, service, version in parsed_services:
        services_text.append(f"{service}")

    simple_prompt = f"Security analysis for: {', '.join(services_text)}. Priority?"

    try:
        # Set a shorter timeout for CPU inference
        llm_client.timeout = 20
        return llm_client.chat(
            model=llm_client.model,
            message=simple_prompt,
            system_prompt="",  # Empty string instead of None
            temperature=0.0,
        )
    except Exception:
        return None


def show_scan_results(nmap_text: str, llm_client) -> None:
    parsed = parse_nmap(nmap_text)

    if not parsed:
        print(
            "I couldn't find any open services in that input.\n"
            "Make sure you pasted Nmap normal output that includes the line:\n"
            "  PORT  STATE  SERVICE  VERSION\n"
        )
        return

    # Try to get AI analysis first (quick attempt only)
    llm_analysis = None
    if parsed and len(parsed) <= 2 and HAS_LLM:  # Only try AI for very small scans
        print("Getting AI analysis (20s timeout)...")
        llm_analysis = get_llm_scan_analysis(parsed, llm_client)
        if not llm_analysis:
            print("AI analysis timed out - showing traditional analysis.")

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

    if not llm_analysis and HAS_LLM and len(parsed) <= 2:
        print(
            "\n[INFO] AI analysis skipped (CPU inference too slow). Traditional analysis shown above."
        )
    elif not HAS_LLM:
        print("\n[INFO] LLM module not available. Check llm.py file.")


def main() -> None:
    # Initialize LLM client
    llm_client = OllamaClient()

    print("super-AI - tiny pentest helper (authorized use only).")
    if HAS_LLM and llm_client.is_available():
        print(f"AI analysis enabled (model: {llm_client.model})")
    else:
        print("AI analysis disabled (check Ollama installation)")
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
