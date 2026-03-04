def parse_nmap(file_path):
    open_services = []

    with open(file_path, "r") as file:
        for line in file:
            if "open" in line:
                parts = line.split()
                port = parts[0]
                service = parts[2]
                version = parts[3]
                open_services.append((port, service, version))
        return open_services
