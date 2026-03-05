from knowledge_base import INTENTS


def get_input():
    print("Hello you can paste a nmap scan result here or type 'exit' to quit:")
    print("(Paste multi-line output, then press Enter on an empty line to finish.)")

    lines = []
    while True:
        try:
            line = input(">").rstrip("\n")
        except EOFError:
            # stdin closed; treat as end of paste (allows piping too)
            break

        # Empty line ends the paste block
        if line == "":
            break

        lines.append(line)

    return "\n".join(lines)


def detect_intents(user_input: str):
    user_input = user_input.lower()
    for intents, words in INTENTS.items():
        for word in words:
            if word in user_input:
                return intents
    return "i don t understand what u're talking about sowwy"
