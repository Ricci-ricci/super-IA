SERVICES_ACTIONS = {
    "ssh": (
        "SSH service detected.\n"
        "- Verify scope/ROE allows auth testing.\n"
        "- Enumerate banner/version and compare with known CVEs.\n"
        "- Check config posture: password auth vs keys, root login, MFA, weak ciphers.\n"
        "- If authorized, test only approved credentials and rate limits.\n"
    ),
    "http": (
        "HTTP service detected.\n"
        "- Identify app/framework, endpoints, and auth flows.\n"
        "- Check common web issues (OWASP Top 10) and misconfigurations.\n"
        "- Capture evidence: headers, status codes, tech stack hints.\n"
    ),
    "https": (
        "HTTPS service detected.\n"
        "- Check TLS config (protocols/ciphers), cert validity, HSTS.\n"
        "- Same web testing approach as HTTP.\n"
    ),
    "ftp": (
        "FTP service detected.\n"
        "- Check for anonymous access (if allowed) and exposed files.\n"
        "- Review banner/version for known issues.\n"
        "- Validate if cleartext credentials are being used (risk note).\n"
    ),
    "smtp": (
        "SMTP service detected.\n"
        "- Identify server banner/version.\n"
        "- Check for open relay (safe test) if within ROE.\n"
        "- Enumerate supported auth and TLS (STARTTLS).\n"
    ),
    "dns": (
        "DNS service detected.\n"
        "- Determine if recursion is enabled for external clients.\n"
        "- Check zone transfer misconfig (only if authorized).\n"
        "- Map records to expand asset inventory.\n"
    ),
    "snmp": (
        "SNMP service detected.\n"
        "- Check version (v1/v2c/v3) and whether default communities exist (authorized only).\n"
        "- If authorized, try read-only enumeration to identify exposed system info.\n"
    ),
    "smb": (
        "SMB service detected.\n"
        "- Identify SMB version/signing support.\n"
        "- Enumerate shares and permissions (authorized scope only).\n"
        "- Document risky configs (guest access, weak share ACLs).\n"
    ),
    "rdp": (
        "RDP service detected.\n"
        "- Confirm NLA requirement and TLS.\n"
        "- Review exposure: is this meant to be internet-facing?\n"
        "- If authorized, validate account lockout policy and MFA posture (no brute force unless ROE allows).\n"
    ),
    "mysql": (
        "MySQL service detected.\n"
        "- Identify version.\n"
        "- Check network exposure and whether remote auth is required.\n"
        "- If authorized, review weak/default creds policy and least privilege.\n"
    ),
    "postgresql": (
        "PostgreSQL service detected.\n"
        "- Identify version.\n"
        "- Check exposure and auth methods.\n"
        "- If authorized, validate role separation and TLS.\n"
    ),
    "mssql": (
        "MSSQL service detected.\n"
        "- Identify version.\n"
        "- Check exposure and auth posture.\n"
        "- If authorized, validate least privilege and configuration hardening.\n"
    ),
    "redis": (
        "Redis service detected.\n"
        "- Check if it is exposed without auth/TLS (common critical misconfig).\n"
        "- Document bind settings and network restrictions.\n"
    ),
    "mongodb": (
        "MongoDB service detected.\n"
        "- Check whether auth is enabled and if it’s exposed publicly.\n"
        "- Validate correct binding and network ACLs.\n"
    ),
    "ldap": (
        "LDAP service detected.\n"
        "- Determine if LDAPS is available/required.\n"
        "- If authorized, enumerate directory schema and exposed info carefully.\n"
    ),
}


INTENTS = {
    "greeting": ["hello", "hi", "hey"],
    "exit": ["exit", "quit", "bye"],
    "scan": ["scan", "nmap", "analyze"],
    "question": ["what", "how", "why"],
}
