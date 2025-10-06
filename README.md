# Network-Scanner-MacOS
Network Scanner (macOS + Linux)
================================

Ein einfacher, stabiler und erweiterbarer Netzwerkscanner für macOS und Linux. Aktuell führt er einen parallelen Ping-Sweep aus und meldet pro Host: erreichbar (up/down) und Latenz in Millisekunden.

Features (Stand jetzt)
- Parallele Pings mit konfigurierbarer Concurrency
- Unterstützt CIDR, IP‑Bereiche (z. B. 192.168.1.10-192.168.1.50 oder 192.168.1.10-50) und einzelne IPs
- Automatische Erkennung des lokalen Netzes (ohne Argumente wird z. B. 192.168.x.x/24 gescannt)
- Farbige, übersichtliche Tabelle (Status + Latenz) oder JSON-Ausgabe
- Keine externen Abhängigkeiten (nur Python-Standardbibliothek)

Voraussetzungen
- Python 3.9 oder neuer
- System-Ping vorhanden (macOS: /sbin/ping, Linux: /bin/ping oder ping im PATH)

Installation (lokal)
Option A: Direkt als Skript nutzen
```bash
python -m netscan <CIDR|Range|IP>
# ohne Argumente: lokales Netz automatisch scannen
python -m netscan
```

Option B: Installieren und als CLI nutzen
```bash
pip install -e .
netscan 192.168.1.0/24
```

Beispiele
```bash
# gesamtes /24-Netz scannen
netscan 192.168.1.0/24

# Bereichs-Scan
netscan 192.168.1.10-192.168.1.50
netscan 192.168.1.10-50

# Einzelne IP
netscan 192.168.1.20

# JSON-Ausgabe mit 200 gleichzeitigen Pings und 1.5s Timeout
netscan 10.0.0.0/24 -c 200 -t 1.5 --json

# Farbausgabe deaktivieren
netscan 192.168.1.0/24 --no-color
```

CLI-Optionen
- cidr: Ziel(e) als CIDR/Range/IP
- -c/--concurrency: Anzahl gleichzeitiger Pings (default 128)
- -t/--timeout: Timeout pro Paket in Sekunden (default 1.0)
- --count: ICMP Echo Requests pro Host (default 1)
- --json: JSON-Ausgabe
- --no-color: Farbige Ausgabe deaktivieren

Architektur und Erweiterbarkeit
- Modul `netscan.scanner` kapselt Ping-Logik und Ziel-Parsing
- Modul `netscan.cli` stellt die Kommandozeilenoberfläche bereit
- Ergebnisobjekt enthält ip, up, latency_ms

Nächste Schritte (Ideen)
- ARP/NDP-Discovery für lokale Netze (MAC, Hersteller)
- TCP-Portscan (syn/conn) optional
- Service-Erkennung (Banner Grab)
- IPv6-Unterstützung und parallele Scans gemischt
- Ausgabeformate: CSV, Markdown, HTML
- Konfigurierbare Rate Limits und Wiederholungen

Lizenz
MIT

