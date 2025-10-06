# Network Scanner (macOS + Linux)

Ein moderner, stabiler und erweiterbarer Netzwerkscanner für macOS und Linux mit interaktiver Terminal-UI. Führt parallele Ping-Sweeps aus und bietet detaillierte Host-Informationen inklusive Port-Scanning.

![Version](https://img.shields.io/badge/version-0.1.3-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

### Kern-Funktionen
- **Parallele Netzwerk-Scans** mit konfigurierbarer Concurrency
- **Rate Limiting**: Token-Bucket-Algorithmus für sichere Scans in Produktions-Umgebungen
- **Scan-Profile**: Vordefinierte Profile (Quick/Normal/Thorough/Stealth) für verschiedene Einsatzzwecke
- **Export-Formate**: CSV, Markdown und HTML für professionelle Berichte
- **Flexible Zielangabe**: CIDR, IP-Bereiche (z.B. `192.168.1.10-50`) und einzelne IPs
- **Automatische Netz-Erkennung** (ohne Argumente wird das lokale Netz gescannt)
- **Comprehensive Port-Scanning**: Top 10.000 Ports mit Service-Erkennung
- **Persistent Cache**: Port-Scan-Ergebnisse werden zwischengespeichert (1 Stunde TTL)
- Hostname- und MAC-Auflösung via Reverse DNS, mDNS und ARP
- **Minimal Dependencies**: Nur PyYAML (für Profile-Konfiguration)

### Interaktive TUI (Terminal User Interface)
- **Modernes Split-Panel Layout**:
  - **Linkes Panel**: Detaillierte Host-Informationen
    - IP-Adresse, Hostname, MAC-Adresse
    - Status (UP/DOWN) mit farbiger Kennzeichnung
    - Latenz-Messung
    - Liste aller offenen Ports mit Service-Namen
  - **Rechtes Panel**: Scrollbare Host-Liste (bis zu 254 Hosts)
- **Live-Netzwerk-Traffic** mit geglätteten Sparkline-Graphen (RX/TX)
- **Echtzeit-Updates** während des Scannens mit Fortschrittsanzeige
- **Scan-Profile**: Schnellwahl mit Shift+P (Quick/Normal/Thorough/Stealth)
- **Export-Dialog**: Shift+E für interaktiven Export (CSV/Markdown/HTML)
- **Intelligente Port-Scanning**: Automatischer Port-Scan mit persistentem Cache
- **Cache-Management**: Shift+C zum Löschen, Anzeige des Cache-Alters
- **Flexible Sortierung** nach IP, Status, Latenz, Hostname oder MAC
- **Filter-Optionen**: Alle Hosts oder nur aktive (UP) Hosts anzeigen

### Ausgabe-Optionen
- **CSV-Export**: Strukturierte Daten für Spreadsheets und Datenbanken
- **Markdown-Export**: GitHub-freundliche Dokumentation mit Tabellen
- **HTML-Export**: Interaktive Berichte mit Sortierung und Suchfunktion
- Farbige, übersichtliche Tabelle (CLI)
- JSON-Ausgabe für Automatisierung
- Debug-Modus mit detaillierten Informationen

## Voraussetzungen
- Python 3.9 oder neuer
- PyYAML (`pip install pyyaml`)
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

# Mit Scan-Profil (quick/normal/thorough/stealth)
netscan --profile quick
netscan --profile thorough --output-html audit.html

# Alle verfügbaren Profile anzeigen
netscan --list-profiles

# Eigenes Profil speichern
netscan --save-profile my-profile -c 100 -t 1.5

# Export-Optionen
netscan 192.168.1.0/24 --output-csv scan.csv
netscan 192.168.1.0/24 --output-md scan.md
netscan 192.168.1.0/24 --output-html scan.html

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

# Rate Limiting (Bandbreite begrenzen)
netscan 192.168.1.0/24 --rate-limit 10        # Max 10 req/s
netscan --rate-limit 5 --burst 20              # Max 5 req/s mit Burst von 20
```

### Rate Limiting

Das Rate Limiting schützt vor Netzwerk-Überlastung und verhindert das Auslösen von IDS/IPS-Systemen:

```bash
# Grundlegende Rate-Limitierung
netscan 192.168.1.0/24 --rate-limit 10    # Maximal 10 Anfragen pro Sekunde

# Mit Burst-Capacity
netscan --rate-limit 5 --burst 20          # 5 req/s mit Burst von 20

# Für Stealth-Scans
netscan --profile stealth --rate-limit 2   # Sehr langsam für maximale Unauffälligkeit
```

**Features:**
- **Token Bucket Algorithm**: Glatte Rate-Limitierung mit Burst-Unterstützung
- **Thread-Safe**: Funktioniert mit hoher Concurrency
- **Statistiken**: Tracking von total/throttled requests
- **Dynamische Anpassung**: Rate kann zur Laufzeit geändert werden (CLI)
- **Zero = Unlimited**: `--rate-limit 0` deaktiviert die Limitierung

**Empfohlene Werte:**
- **Produktions-Netze**: `--rate-limit 10-20` (sicher für kritische Infrastruktur)
- **Stealth-Scans**: `--rate-limit 2-5` (IDS-Vermeidung)
- **Heim-Netzwerk**: Keine Limitierung oder `--rate-limit 50+` (maximale Geschwindigkeit)
- **IoT-Geräte**: `--rate-limit 5-10` (viele IoT-Geräte haben langsame Stacks)

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
| `Shift+P` | Scan-Profil auswählen (Quick/Normal/Thorough/Stealth) |
| `e` | Export-Dialog öffnen (CSV/Markdown/HTML) |
| `Shift+C` | Port-Scan-Cache löschen |
| `↑`/`↓` oder `j`/`k` | Host auswählen |
| `Enter` | Ports des ausgewählten Hosts neu scannen |
| `1`-`5` | Sortierspalte wählen (1=IP, 2=Status, 3=Latenz, 4=Hostname, 5=MAC) |
| `o` | Sortierspalte zyklisch wechseln |
| `O` | Sortierreihenfolge umkehren (↑ ↔ ↓) |
| `q` | Beenden |

#### TUI-Features im Detail
- **Live-Traffic-Graphen**: Geglättete Sparklines für RX (magenta) und TX (blau) mit aktuellem Wert und dynamischem Maximum
- **Auto-Port-Scan**: Beim Navigieren zwischen Hosts werden automatisch die Ports gescannt
- **Persistent Cache**: Port-Scan-Ergebnisse werden für 1 Stunde gespeichert (~/.netscan_cache.json)
- **Scan-Profile**: Schnellwahl optimierter Einstellungen für verschiedene Szenarien
- **Export-Dialog**: Interaktiver Export mit Format-Auswahl und Dateinamen-Editor
- **Detailliertes Host-Panel**: Zeigt alle relevanten Informationen zum ausgewählten Host
- **Service-Erkennung**: Bekannte Services werden automatisch erkannt (SSH, HTTP, HTTPS, MySQL, PostgreSQL, RDP, etc.)
- **Responsive Layout**: Passt sich automatisch an die Terminal-Größe an

## Scan-Profile

### Vordefinierte Profile

| Profil | Beschreibung | Concurrency | Timeout | Ports | Dauer | Einsatzzweck |
|--------|--------------|-------------|---------|-------|-------|--------------|
| **Quick** 🚀 | Schneller Scan | 256 | 0.5s | Top 100 | <1 min | Gesundheitschecks, schnelle Übersicht |
| **Normal** ⚖️ | Ausgewogen | 128 | 1.0s | Top 1000 | 2-3 min | Tägliches Monitoring, Standard-Scans |
| **Thorough** 🔍 | Tiefgehend | 64 | 2.0s | 1-10000 | 5-10 min | Sicherheits-Audits, vollständiges Inventar |
| **Stealth** 🥷 | Unaufällig | 10 | 3.0s | Top 1000 | 10-15 min | IDS-Vermeidung, Produktions-Scans |

### Custom Profile

Eigene Profile können gespeichert und wiederverwendet werden:

```bash
# Profil mit eigenen Einstellungen speichern
netscan --save-profile my-profile -c 150 -t 1.2

# Gespeichertes Profil verwenden
netscan --profile my-profile

# Alle Profile anzeigen (inkl. custom)
netscan --list-profiles
```

Profile werden in `~/.netscan/profiles/` als YAML-Dateien gespeichert.

Beispiel-Profile finden Sie in `examples/custom-profiles/`:
- **production-safe**: Konservative Einstellungen für Live-Systeme
- **home-network**: Optimiert für Heimnetzwerke
- **pentest-deep**: Umfassend für Security-Tests
- **iot-discovery**: Geduldig für IoT-Geräte

## CLI-Optionen
- `cidr`: Ziel(e) als CIDR/Range/IP
- `-c`/`--concurrency`: Anzahl gleichzeitiger Pings (Standard: 128)
- `-t`/`--timeout`: Timeout pro Paket in Sekunden (Standard: 1.0)
- `--count`: ICMP Echo Requests pro Host (Standard: 1)
- `-p`/`--profile`: Scan-Profil verwenden (quick/normal/thorough/stealth/custom)
- `--list-profiles`: Alle verfügbaren Profile anzeigen
- `--save-profile`: Aktuelle Einstellungen als Profil speichern
- `--output-csv`: Export nach CSV
- `--output-md`: Export nach Markdown
- `--output-html`: Export nach HTML (interaktiv)
- `--include-down`: DOWN-Hosts in Export einschließen
- `--no-emoji`: Emoji in Markdown-Export deaktivieren
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
- **`netscan.profiles`**: Scan-Profile-Verwaltung (YAML-basiert)
- **`netscan.export`**: Export-Engine für CSV, Markdown und HTML
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
- [ ] Konfigurierbare Rate-Limits (Token-Bucket-Algorithmus)
- [ ] Erweiterte OUI-Datenbank für bessere Vendor-Erkennung
- [ ] Service-Banner-Grabbing mit Version-Detection
- [ ] IPv6-Unterstützung
- [ ] Aktives mDNS-Browsing (dns-sd/avahi-browse)
- [ ] ARP/NDP-Discovery für lokale Netze
- [ ] Historische Daten und Änderungsverfolgung
- [ ] TUI Settings Panel mit allen Konfigurationen

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

**Version**: 0.1.2  
**Letztes Update**: Oktober 2025

## Siehe auch
- [Release Notes](RELEASE_NOTES.md) - Detaillierte Änderungen und neue Features
- [LICENSE](LICENSE) - MIT License
