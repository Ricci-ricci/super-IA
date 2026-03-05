import re

# create a regex to match the open ports in the nmap output
PORT_ROW = re.compile(r"^(\d+/(tcp|udp))\s+(\S+)\s+(\S+)\s*(.*)$")


def parse_nmap(nmap_text: str):
    open_services = []
    in_table = False

    for raw in (nmap_text or "").splitlines():
        line = raw.rstrip("\n")

        # detect start of the ports table
        if line.startswith("PORT"):
            in_table = True
            continue

        if not in_table:
            continue

        # stop conditions (end of table / new sections)
        if line.strip() == "":
            break
        if line.startswith("Service Info:") or line.startswith("# Nmap done"):
            break

        # ignore script output lines and other non-row lines
        if not re.match(r"^\d+/(tcp|udp)\s+", line):
            continue

        # split into the 4 expected columns; VERSION can contain spaces
        parts = line.split(None, 3)  # maxsplit=3
        if len(parts) < 3:
            continue

        port_proto = parts[0]  # e.g. "80/tcp"
        state = parts[1]  # e.g. "open" / "filtered"
        service = parts[2]  # e.g. "http"
        version = parts[3] if len(parts) == 4 else ""

        if state != "open":
            continue

        open_services.append((port_proto, service, version))

    return open_services


def get_nmap_imput():
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
