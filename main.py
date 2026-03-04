from knowledge_base import SERVICES_ACTIONS
from parser import parse_nmap

services = parse_nmap("dreaming.txt")


for port, service, version in services:
    print(f"\nPort: {port}, Service: {service}, Version: {version}")

    actions = SERVICES_ACTIONS.get(
        service,
        "No specific actions found for this service. Consider general pentesting techniques.",
    )
    print(f"Recommended Actions: {actions}")
print("\n What service do you want to explore deeper? (Type 'exit' to quit)")
user_input = input(">").strip().lower()
if user_input in SERVICES_ACTIONS:
    print(f"Exploring {user_input} service...")
    print(SERVICES_ACTIONS[user_input])
elif user_input == "exit":
    print("bye. Happy pentesting!")
else:
    print(
        "Service not recognized or no specific actions available. Please choose a valid service or type 'exit' to quit."
    )
