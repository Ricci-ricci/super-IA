from action import detect_intents, get_input
from knowledge_base import SERVICES_ACTIONS
from parser import parse_nmap


def print_help() -> None:
    print(
        "\nCommands:\n"
        "- hello / hi / hey: greeting\n"
        "- scan / nmap / analyze: enter scan mode (paste Nmap output)\n"
        "- <service>: show recommendations for a service (e.g., ssh, http)\n"
        "- exit / quit / bye: quit\n"
        "\nTip: In scan mode, paste multi-line Nmap output then press Enter on an empty line.\n"
    )


def show_services(parsed) -> None:
    if not parsed:
        print("No open services detected (or input wasn't an Nmap PORT table).")
        return

    for port, service, version in parsed:
        print(f"\nPort: {port}, Service: {service}, Version: {version}")

        actions = SERVICES_ACTIONS.get(
            service,
            "No specific actions found for this service. Consider general pentesting techniques.",
        )
        print(f"Recommended Actions: {actions}")


print("superPENTESTING - tiny assistant (portfolio). Type 'help' for commands.")

while True:
    user_text = input(">").strip()
    if not user_text:
        continue

    intent = detect_intents(user_text)

    if intent == "exit":
        print("bye. Happy pentesting!")
        break

    if user_text.lower() in {"help", "?"}:
        print_help()
        continue

    if intent == "greeting":
        print(
            "Hey! Tell me what you want to do: say 'scan' to paste an Nmap scan, or type a service like 'ssh'."
        )
        continue

    if intent == "scan":
        print(
            "Paste your Nmap scan here — I’m gonna analyze it. (Empty line to finish)"
        )
        nmap_text = get_input()
        if nmap_text.lower().strip() == "exit":
            print("bye. Happy pentesting!")
            break

        parsed = parse_nmap(nmap_text)
        show_services(parsed)
        continue

    # If the user typed a service name directly (e.g., "ssh", "http")
    maybe_service = user_text.strip().lower()
    if maybe_service in SERVICES_ACTIONS:
        print(f"Exploring {maybe_service} service...")
        print(SERVICES_ACTIONS[maybe_service])
        continue

    if intent == "question":
        print(
            "Ask me something concrete, or say 'scan' to paste Nmap output.\n"
            "Example: 'scan' or 'ssh' or 'http'."
        )
        continue

    print(
        "I don't understand. Type 'help' for commands, or say 'scan' to paste Nmap output."
    )
