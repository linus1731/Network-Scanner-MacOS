# Network Scanner (macOS + Linux)

Ein moderner, stabiler und erweiterbarer Netzwerkscanner für macOS und Linux mit interaktiver Terminal-UI. Führt parallele Ping-Sweeps aus und bietet detaillierte Host-Informationen inklusive Port-Scanning.

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

### Kern-Funktionen
- **Parallele Netzwerk-Scans** mit konfigurierbarer Concurrency
- **Flexible Zielangabe**: CIDR, IP-Bereiche (z.B. `192.168.1.10-50`) und einzelne IPs
- **Automatische Netz-Erkennung** (ohne Argumente wird das lokale Netz gescannt)
- **Comprehensive Port-Scanning**: Top 10.000 Ports mit Service-Erkennung
- Hostname- und MAC-Auflösung via Reverse DNS, mDNS und ARP
- **Keine externen Abhängigkeiten** (nur Python-Standardbibliothek)

### Interaktive TUI (Terminal User Interface)
- **Modernes Split-Panel Layout**:
  - **Linkes Panel**: Detaillierte Host-Informationen
    - IP-Adresse, Hostname, MAC-Adresse
    - Status (UP/DOWN) mit farbiger Kennzeichnung
    - Latenz-Messung
    - Liste aller offenen Ports mit Service-Namen
  - **Rechtes Panel**: Scrollbare Host-Liste (bis zu 254 Hosts)
- **Live-Netzwerk-Traffic** mit geglätteten Sparkline-Graphen (RX/TX)
- **Echtzeit-Updates** während des Scannens
- **Intelligente Port-Scanning**: Automatischer Port-Scan beim Navigieren zwischen Hosts
- **Flexible Sortierung** nach IP, Status, Latenz, Hostname oder MAC
- **Filter-Optionen**: Alle Hosts oder nur aktive (UP) Hosts anzeigen

### Ausgabe-Optionen
- Farbige, übersichtliche Tabelle (CLI)
- JSON-Ausgabe für Automatisierung
- Debug-Modus mit detaillierten Informationen

## Voraussetzungen
- Python 3.9 oder neuer
- System-Ping vorhanden (macOS: `/sbin/ping`, Linux: `/bin/ping`)
- Optional (für bessere Hostnamen auf Linux): `avahi-utils` (`avahi-resolve-address`)

## Installation

### Option A: Direkt als Skript nutzen
```bash
python -m netscan <CIDR|Range|IP>
# ohne Argumente: lokales Netz automatisch scannen
python -m netscan
```

### Option B: Installieren und als CLI nutzen
```bash
pip install -e .
netscan 192.168.1.0/24
netscan-tui   # interaktive Terminal starten
```

## Verwendung

### CLI-Modus (Schnell-Scan)
```bash
# Gesamtes /24-Netz scannen
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

# Debug-Modus
netscan --debug
```

### TUI-Modus (Interaktiv)
```bash
netscan-tui
```

#### TUI-Tastenkombinationen
| Taste | Funktion |
|-------|----------|
| `s` | Netzwerk-Scan starten |
| `r` | Interface/Netz neu erkennen |
| `a` | Filter umschalten (ALL ↔ UP) |
| `↑`/`↓` oder `j`/`k` | Host auswählen |
| `Enter` | Ports des ausgewählten Hosts neu scannen |
| `1`-`5` | Sortierspalte wählen (1=IP, 2=Status, 3=Latenz, 4=Hostname, 5=MAC) |
| `o` | Sortierspalte zyklisch wechseln |
| `O` | Sortierreihenfolge umkehren (↑ ↔ ↓) |
| `q` | Beenden |

#### TUI-Features im Detail
- **Live-Traffic-Graphen**: Geglättete Sparklines für RX (magenta) und TX (blau) mit aktuellem Wert und dynamischem Maximum
- **Auto-Port-Scan**: Beim Navigieren zwischen Hosts werden automatisch die Ports gescannt
- **Detailliertes Host-Panel**: Zeigt alle relevanten Informationen zum ausgewählten Host
- **Service-Erkennung**: Bekannte Services werden automatisch erkannt (SSH, HTTP, HTTPS, MySQL, PostgreSQL, RDP, etc.)
- **Responsive Layout**: Passt sich automatisch an die Terminal-Größe an

## CLI-Optionen
- `cidr`: Ziel(e) als CIDR/Range/IP
- `-c`/`--concurrency`: Anzahl gleichzeitiger Pings (Standard: 128)
- `-t`/`--timeout`: Timeout pro Paket in Sekunden (Standard: 1.0)
- `--count`: ICMP Echo Requests pro Host (Standard: 1)
- `--json`: JSON-Ausgabe
- `--no-color`: Farbige Ausgabe deaktivieren
- `--debug`: Detaillierte Debug-Informationen ausgeben

## Port-Scanning
- **Scan-Bereich**: Top 10.000 Ports (1-10000)
- **Methode**: TCP-Connect (kein Root erforderlich)
- **Concurrency**: 256 parallele Verbindungen
- **Timeout**: 0.5 Sekunden pro Port
- **Service-Erkennung**: Automatische Zuordnung von Port-Nummern zu Service-Namen

## Architektur

### Module
- **`netscan.scanner`**: Ping-Logik, Ziel-Parsing, Port-Scanning
- **`netscan.cli`**: Kommandozeilen-Interface, farbige Tabelle, JSON-Ausgabe
- **`netscan.tui`**: Interaktive Terminal-UI mit Split-Panel-Layout
- **`netscan.netinfo`**: Lokales Netzwerk/IP-Ermittlung
- **`netscan.resolve`**: Hostname-Resolution (PTR + mDNS)
- **`netscan.arp`**: ARP/Nachbartabelle für MAC-Adressen
- **`netscan.vendor`**: OUI→Vendor-Zuordnung
- **`netscan.traffic`**: Netzwerk-Traffic-Monitoring

### Erweiterbarkeit
- Modularer Aufbau ermöglicht einfache Erweiterungen
- Ergebnisobjekte enthalten strukturierte Daten (IP, Status, Latenz, Hostname, MAC)
- Plugin-ready für zusätzliche Scanner-Funktionen

## Zukünftige Features (Roadmap)
- [ ] Erweiterte OUI-Datenbank für bessere Vendor-Erkennung
- [ ] Aktives mDNS-Browsing (dns-sd/avahi-browse)
- [ ] ARP/NDP-Discovery für lokale Netze
- [ ] Service-Banner-Grabbing
- [ ] IPv6-Unterstützung
- [ ] Zusätzliche Ausgabeformate (CSV, Markdown, HTML)
- [ ] Konfigurierbare Rate-Limits
- [ ] Scan-Profile (Quick, Normal, Thorough)
- [ ] Export-Funktion in TUI
- [ ] Historische Daten und Änderungsverfolgung

## Lizenz
MIT

## Hinweise

### Vendor-Erkennung
- Basiert auf OUI-Datenbanken von Wireshark (manuf) oder Nmap (nmap-mac-prefixes)
- Bevorzugt längste passende Präfixlänge (36 Bit vor 24 Bit)
- Fallback auf interne Mini-Datenbank
- Randomisierte MACs werden als "Locally administered (randomized)" erkannt

### Performance-Tipps
- Für große Netze: Concurrency erhöhen (`-c 256`)
- Für langsame Netze: Timeout erhöhen (`-t 2.0`)
- TUI: Auto-Port-Scan kann bei vielen Hosts CPU-intensiv sein

### Bekannte Einschränkungen
- Port-Scanning nutzt TCP-Connect (langsamer als SYN-Scan, aber kein Root erforderlich)
- MAC-Adressen nur im lokalen Subnetz verfügbar
- mDNS-Resolution abhängig vom System-Setup

## Credits
Entwickelt von Linus Malbertz  
Inspiriert von nmap, angry IP scanner und btop

---

**Version**: 0.1.1  
**Letztes Update**: Oktober 2025

## Siehe auch
- [Release Notes](RELEASE_NOTES.md) - Detaillierte Änderungen und neue Features
- [LICENSE](LICENSE) - MIT License
