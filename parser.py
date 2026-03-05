import re

# create a regex to match the open ports in the nmap output
PORT_ROW = re.compile(r"^(\d+/tcp)\s+open\s+(\S+)\s+(.+)$")


def parse_nmap(file_path: str):
    open_services = []
    # ensure that we know when the open ports section starts and ends
    in_table = False
    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        for raw in file:
            line = raw.rstrip("\n")
            # we have to detect when the port table starts and ends, because nmap outputs a lot of other information before and after the table
            if line.startswith("PORT"):
                in_table = True
                continue
            if not in_table:
                continue

            # stop at the end of the nmap script
            if line.strip() == "":
                break
            if line.startswith("Servince info ") or line.startswith("Nmap Done"):
                break

            # only parse the actual port rows , not everythings
            if not PORT_ROW.match(line):
                continue

            # split into the 4 expected groups: port, state, service, version
            parts = line.split(None, 3)
            if len(parts) < 3:
                continue
            ports = parts[0]
            state = parts[1]
            service = parts[2]
            version = parts[3] if len(parts) > 3 else ""

            if state != "open":
                continue

            open_services.append((ports, service, version))
        return open_services
