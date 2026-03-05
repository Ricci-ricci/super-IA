from __future__ import annotations

import re

from knowledge_base import INTENTS, SERVICES_ACTIONS
from parser import get_nmap_imput, parse_nmap


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


def show_scan_results(nmap_text: str) -> None:
    parsed = parse_nmap(nmap_text)

    if not parsed:
        print(
            "I couldn't find any open services in that input.\n"
            "Make sure you pasted Nmap normal output that includes the line:\n"
            "  PORT  STATE  SERVICE  VERSION\n"
        )
        return

    for port, service, version in parsed:
        print(f"\nPort: {port}, Service: {service}, Version: {version}")

        actions = SERVICES_ACTIONS.get(
            service,
            "No specific actions found for this service. Consider general pentesting techniques.",
        )
        print(f"Recommended Actions: {actions}")


def main() -> None:
    print(
        "superPENTESTING - tiny pentest helper (authorized use only). Type 'help' for commands.\n"
    )

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
            show_scan_results(nmap_text)
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
