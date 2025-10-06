# Release Notes - Network Scanner

## Version 0.1.3 (Oktober 2025) 🚦

### 🎉 Major Feature: Rate Limiting

#### ⏱️ Token Bucket Rate Limiter
Professionelles Rate Limiting für sichere Scans in Produktions-Umgebungen:

**Kern-Features:**
- **Token Bucket Algorithm**: Glatte Limitierung mit Burst-Unterstützung
- **Thread-Safe**: Funktioniert nahtlos mit hoher Concurrency
- **Statistiken**: Tracking von total/throttled requests
- **Dynamische Anpassung**: Rate kann zur Laufzeit geändert werden
- **Zero = Unlimited**: `--rate-limit 0` deaktiviert die Limitierung

**CLI-Integration:**
```bash
# Grundlegende Rate-Limitierung
netscan 192.168.1.0/24 --rate-limit 10        # Max 10 req/s

# Mit Burst-Capacity
netscan --rate-limit 5 --burst 20              # 5 req/s, Burst von 20

# Kombiniert mit Profilen
netscan --profile stealth --rate-limit 2       # Ultra-stealth
```

**Implementierung:**
- Neue `netscan/ratelimit.py` mit RateLimiter-Klasse (196 Zeilen)
- Integration in `scanner.py`: ping(), _tcp_probe(), _tcp_connect()
- CLI-Optionen: `--rate-limit N` und `--burst N`
- 13 neue Unit-Tests (alle bestanden)

**Use Cases:**
- **Produktions-Netze**: 10-20 req/s (sicher für kritische Infrastruktur)
- **Stealth-Scans**: 2-5 req/s (IDS-Vermeidung)
- **Heim-Netzwerk**: Keine Limitierung (maximale Geschwindigkeit)
- **IoT-Geräte**: 5-10 req/s (langsame TCP-Stacks)

**Statistiken:**
- Tokens: Aktuelle verfügbare Tokens
- Total Requests: Gesamtzahl aller Anfragen
- Throttled Requests: Anzahl verzögerter Anfragen
- Throttle Percentage: Prozentsatz verzögerter Anfragen

### 📊 Testing & Qualität
- **70 Unit-Tests** (35 export + 22 profiles + 13 ratelimit)
- **100% Pass Rate**
- Token bucket algorithm validiert (refill, burst, thread-safety)
- Integrationstest mit echten Netzwerk-Operationen

### 🎨 TUI Integration (Bonus!)
**Live Rate Limit Control** direkt in der TUI:
- **Hotkeys**: `+` erhöhen, `-` verringern
- **Header-Anzeige**: Zeigt aktuelle Rate und Status
- **Visual Indicators**:
  - `rate=10/s ✓` - Keine Drosselung
  - `rate=5/s ⚡` - Leichte Drosselung (<10%)
  - `rate=2/s 🔥` - Starke Drosselung (>10%)
  - `rate=∞` - Unbegrenzt (deaktiviert)
- **Smart Adjustment**: 
  - 1-10 req/s: ±1 pro Schritt
  - 10-50 req/s: ±5 pro Schritt
  - 50+ req/s: ±10 pro Schritt
- **Feedback**: Toast-Nachricht zeigt neue Rate

### 🚀 Phase 1 Complete!
Mit Rate Limiting ist **Phase 1** (Basic Network Discovery) nun **100% abgeschlossen**:
- ✅ Task 1: Export Formats (CSV, Markdown, HTML)
- ✅ Task 2: Rate Limiting (Token Bucket)
- ✅ Task 3: Scan Profiles (Quick/Normal/Thorough/Stealth)

**Nächste Schritte:** Phase 2 (Deep Intelligence) mit Banner Grabbing & Service Detection

---

## Version 0.1.2 (Oktober 2025)

### 🎉 Major Features

#### 📊 Export-Formate für professionelle Berichte
Drei neue Export-Formate ermöglichen professionelle Dokumentation und Weitergabe von Scan-Ergebnissen:

**CSV-Export:**
- Strukturierte Daten für Spreadsheets und Datenbanken
- Spalten: IP, Status, Latenz, Hostname, MAC, Vendor, Ports
- Korrektes Escaping für Kommas und Sonderzeichen
- Port-Ranges-Formatierung (z.B. "22-25, 80, 443")

**Markdown-Export:**
- GitHub-freundliche Pipe-Tabellen
- Optionale Status-Emojis (✅ UP / ❌ DOWN)
- Perfekt für Dokumentation und README-Dateien
- Escaping von Markdown-Sonderzeichen

**HTML-Export:**
- Interaktive, standalone HTML-Berichte
- Modernes Gradient-Design (Purple/Blue)
- Features:
  - Sortierbare Spalten (per Klick)
  - Echtzeit-Suchfunktion
  - Intelligente IP-Sortierung
  - Color-coded Status
  - Responsive Layout
  - Keine externen Dependencies

**CLI-Integration:**
```bash
netscan 192.168.1.0/24 --output-csv scan.csv
netscan 192.168.1.0/24 --output-md report.md
netscan 192.168.1.0/24 --output-html audit.html --include-down
```

**TUI-Export-Dialog:**
- Hotkey `e` öffnet interaktiven Export-Dialog
- Tab-Taste zum Wechseln zwischen Formaten (CSV/Markdown/HTML)
- Dateiname-Editor mit Cursor-Navigation
- Option zum Einschließen von DOWN-Hosts
- Live-Preview der Export-Statistiken
- Erfolgs-/Fehler-Meldungen

#### 🎯 Scan-Profile für optimierte Workflows
Revolutionäres Profile-System für verschiedene Einsatzszenarien:

**Vordefinierte Profile:**

| Profil | Beschreibung | Settings | Dauer | Einsatz |
|--------|--------------|----------|-------|---------|
| **Quick** 🚀 | Schneller Scan | C=256, T=0.5s, P=top100 | <1 min | Gesundheitschecks |
| **Normal** ⚖️ | Ausgewogen | C=128, T=1.0s, P=top1000 | 2-3 min | Standard-Scans |
| **Thorough** 🔍 | Tiefgehend | C=64, T=2.0s, P=1-10000 | 5-10 min | Security-Audits |
| **Stealth** 🥷 | Unaufällig | C=10, T=3.0s, P=top1000, R=50pkt/s | 10-15 min | IDS-Vermeidung |

**Custom Profile Support:**
- YAML-basierte Konfiguration in `~/.netscan/profiles/`
- Persistente Speicherung eigener Profile
- Konfigurierbare Parameter:
  - Concurrency (parallele Scans)
  - Timeout (pro Host)
  - Port Range (top100, top1000, 1-10000)
  - Rate Limit (optional, packets/second)
  - Random Delays (für Stealth-Scans)

**CLI-Integration:**
```bash
# Profile verwenden
netscan --profile quick
netscan --profile thorough --output-html audit.html

# Profile verwalten
netscan --list-profiles
netscan --save-profile my-profile -c 150 -t 1.2
```

**TUI-Integration:**
- Hotkey `Shift+P` öffnet Profile-Auswahl-Dialog
- Visuelles Picker-Interface mit ↑/↓ Navigation
- Preview der Profile-Details vor Auswahl
- Aktives Profil im Header angezeigt
- Color-coded: Predefined (grün/cyan) vs Custom (magenta)

**Beispiel-Profile:**
Vier production-ready Beispiele in `examples/custom-profiles/`:
- `production-safe.yaml` - Konservativ für Live-Systeme
- `home-network.yaml` - Optimiert für Heimnetzwerke
- `pentest-deep.yaml` - Umfassend für Security-Tests
- `iot-discovery.yaml` - Geduldig für IoT-Geräte

#### 💾 Persistent Port-Scan Cache
Intelligentes Caching-System für bessere Performance:

**Features:**
- Automatisches Caching von Port-Scan-Ergebnissen
- Persistente Speicherung in `~/.netscan_cache.json`
- Time-To-Live (TTL): 1 Stunde (konfigurierbar)
- Automatisches Cleanup abgelaufener Einträge
- Cache-Statistiken im TUI-Header

**Cache-Management:**
- `Shift+C` - Cache vollständig löschen
- Automatische TTL-Prüfung bei jedem Zugriff
- Cache-Alter wird bei Hover angezeigt
- Funktioniert über TUI-Neustarts hinweg

**Performance-Gewinn:**
- Sofortige Anzeige gecachter Port-Scans
- Reduzierung redundanter Netzwerk-Last
- Schnelleres Navigieren zwischen bekannten Hosts

#### 🔄 TUI-Verbesserungen
Zahlreiche Verbesserungen der Terminal-UI:

**Auto-Start Scan:**
- Scan startet automatisch beim TUI-Launch
- Keine manuelle Initiierung mehr nötig
- Sofortige Netzwerk-Übersicht

**Fortschrittsanzeigen:**
- Anzeige des aktuell gescannten Hosts
- Port-Scan-Fortschritt mit aktuellem Port
- Visuelle Indikatoren während laufender Scans

**Verbesserte Help-Line:**
- Aktualisierte Tastenkombinationen
- `[P]rofile` für Profile-Auswahl
- `[e]xport` für Export-Dialog
- `[C]lear cache` für Cache-Management

### 🔧 Technische Verbesserungen

#### Neue Module
- **`netscan.export`** - Export-Engine für alle Formate
- **`netscan.profiles`** - Profile-Verwaltung (YAML-basiert)
- **`tests.test_export`** - 35 umfassende Export-Tests
- **`tests.test_profiles`** - 22 Profile-System-Tests

#### Dependencies
- **PyYAML** hinzugefügt für YAML-Profile-Unterstützung
- Aktualisiert in `pyproject.toml`: `dependencies = ["pyyaml>=6.0"]`

#### Code-Qualität
- **57 Unit-Tests** (35 Export + 22 Profiles) - 100% passing
- Umfassende Test-Coverage für neue Features
- Kein Breaking Changes zu v0.1.1
- Backward-kompatibel (Default-Profil behält altes Verhalten)

#### Profile-Architektur
```python
@dataclass
class ScanProfile:
    name: str
    description: str
    concurrency: int
    timeout: float
    port_range: str
    rate_limit: Optional[int]
    random_delay: bool
    min_delay: float
    max_delay: float
```

#### Export-Architektur
- Einheitliches `HostData` Dataclass für alle Exporter
- Separate Klassen: `CSVExporter`, `MarkdownExporter`, `HTMLExporter`
- Convenience-Functions: `export_to_csv()`, `export_to_markdown()`, `export_to_html()`
- Konsistente Filter-Logik (include_down-Parameter)

### 📁 Neue Dateien
```
netscan/
├── export.py              # 500+ lines, 3 Exporter-Klassen
├── profiles.py            # 291 lines, Profile-Management

tests/
├── test_export.py         # 322 lines, 35 Tests
├── test_profiles.py       # 322 lines, 22 Tests

examples/
└── custom-profiles/
    ├── README.md
    ├── production-safe.yaml
    ├── home-network.yaml
    ├── pentest-deep.yaml
    └── iot-discovery.yaml

.tasks/
├── SCAN_PROFILES_FEATURE.md
└── TASKS.md (updated)
```

### 📊 Statistiken
- **+1,421 Zeilen Code** hinzugefügt
- **12 Dateien** geändert/erstellt
- **57 Tests** passing (vorher: 0)
- **4 Beispiel-Profile** production-ready
- **3 Export-Formate** implementiert
- **4 Predefined Scan-Profile** konfiguriert

### 🎯 Task-Fortschritt
**Phase 1 Status: 2/3 Tasks Complete (67%)**
- ✅ Task 1: Export-Formate (CSV, Markdown, HTML)
- ⬜ Task 2: Rate-Limiting (pending)
- ✅ Task 3: Scan-Profile (Quick/Normal/Thorough/Stealth)

### 🚀 Use Cases

**Schneller Netzwerk-Check:**
```bash
netscan --profile quick --output-csv quick-check.csv
```

**Security-Audit:**
```bash
netscan --profile thorough --output-html security-audit-$(date +%Y%m%d).html
```

**Stealth-Scan:**
```bash
netscan --profile stealth --output-md stealth-report.md
```

**Custom Workflow:**
```bash
netscan --save-profile my-workflow -c 150 -t 1.2
netscan --profile my-workflow --output-html daily-scan.html
```

### 📝 Dokumentation
- README aktualisiert mit allen neuen Features
- Beispiel-Profile mit detaillierten Kommentaren
- Umfassende Feature-Dokumentation in `.tasks/`
- CLI-Help-Text erweitert

### 🐛 Bug Fixes
- Korrekte Handhabung von Sonderzeichen in CSV
- XSS-Prevention in HTML-Export
- Proper IP-Sortierung in interaktiven Reports
- Cache-TTL-Validierung bei jedem Zugriff

### ⚡ Performance
- Port-Scan-Cache reduziert redundante Scans um bis zu 100%
- Profile ermöglichen optimierte Settings für verschiedene Szenarien
- Batch-Export vermeidet unnötige Netzwerk-Calls

---

## Version 0.1.1 (Oktober 2025)

### 🎉 Major Features

#### Komplett überarbeitete TUI (Terminal User Interface)
Die TUI wurde von Grund auf neu gestaltet mit einem modernen Split-Panel-Layout:

**Linkes Detail-Panel:**
- Zeigt umfassende Informationen zum ausgewählten Host
- Schöne Box-Drawing-Zeichen für moderne Optik (═, ─, │, ┌, └, ╔, ╚)
- Farbcodierte Statusanzeige (UP = grün, DOWN = rot)
- Strukturierte Abschnitte:
  - Network Information (IP, Hostname, MAC, Status, Latenz)
  - Open TCP Ports (mit Service-Namen)
  - Controls (Tastaturkürzel-Übersicht)

**Rechtes Host-Panel:**
- Kompakte tabellarische Ansicht aller Hosts
- Scrollbare Liste für große Netzwerke (bis zu 254 Hosts)
- Zeigt IP, Status, Latenz und Hostname
- Visuelles Highlight für ausgewählten Host

#### Erweitertes Port-Scanning
- **10x mehr Ports**: Scan-Bereich von 1.000 auf **10.000 Ports** erweitert
- **Automatisches Scanning**: Ports werden automatisch beim Navigieren zwischen Hosts gescannt
- **Intelligente Service-Erkennung**: Erweiterte Datenbank mit gängigen Services:
  - Neue Services: FTP, Telnet, PostgreSQL, VNC, Redis, MongoDB, HTTP-Proxy
  - Bestehende: SSH, HTTP, HTTPS, MySQL, SMTP, POP3, IMAP, RDP, SMB
- **Bessere Darstellung**: Ports werden als `• 22/tcp → ssh` formatiert

#### Layout & Design-Verbesserungen
- **Unicode-Boxen**: Moderne Rahmen und Trennlinien statt ASCII-Zeichen
- **Farbschema**: Konsistente Verwendung von ANSI-Farben
  - Cyan für IPs
  - Grün für UP-Status
  - Rot für DOWN-Status
  - Gelb für Hervorhebungen
  - Magenta für RX-Traffic
  - Blau für TX-Traffic
- **Responsive Layout**: Automatische Anpassung an Terminal-Größe
- **Separator-Linie**: Vertikale Trennlinie zwischen linkem und rechtem Panel

### 🔧 Technische Verbesserungen

#### Rendering-Optimierungen
- **Korrigierte Refresh-Reihenfolge**: `stdscr.noutrefresh()` vor `win.noutrefresh()` für korrektes Layering
- **Batch-Updates**: Verwendung von `curses.doupdate()` für flüssige Darstellung
- **Separate Fenster**: Panel und Hauptfenster sind unabhängige curses-Windows
- **Kein Flickering**: Optimierte Update-Strategie verhindert Bildschirmflackern

#### Architektur-Verbesserungen
- **Modularer Aufbau**: Klare Trennung zwischen Panel-Logik und Tabellen-Logik
- **Error Handling**: Robuste Fehlerbehandlung bei Window-Erstellung
- **Performance**: Optimierte Port-Scan-Worker mit besserer Concurrency

### ✨ Neue Features

1. **Auto-Port-Scan beim Navigieren**
   - Beim Wechsel zwischen Hosts startet automatisch ein Port-Scan
   - Verhindert doppelte Scans durch intelligente Caching-Logik
   - Zeigt "⟳ Scanning ports..." während des Scans

2. **Erweiterte Tastenkombinationen**
   - `Enter`: Ports des ausgewählten Hosts neu scannen
   - `↑/↓` oder `j/k`: Navigation mit visuellem Feedback
   - Alle bestehenden Shortcuts funktionieren weiterhin

3. **Intelligente Filter-Steuerung**
   - Standard: "ALL" (zeigt alle 254 Hosts)
   - Toggle mit 'a': Wechsel zwischen "ALL" und "UP"
   - Filter-Status wird prominent im Header angezeigt

4. **Verbesserte Host-Zählung**
   - Header zeigt Gesamtanzahl der Hosts
   - Bei Filter "UP": Zeigt nur aktive Hosts

### 🐛 Bug Fixes

1. **Panel-Darstellung**
   - Problem: Panel wurde nicht angezeigt trotz korrekter Erstellung
   - Ursache: Falsche Reihenfolge der `noutrefresh()` Aufrufe
   - Lösung: Hauptfenster vor Panel refreshen, dann beide zusammen mit `doupdate()`

2. **Scrolling**
   - Verbessertes Scrolling-Verhalten bei großen Host-Listen
   - Korrekte Berechnung von `top_index` für Viewport

3. **Layout bei kleinen Terminals**
   - Minimale Panel-Breite von 40 Zeichen garantiert
   - Automatische Anpassung bei Terminal-Breite < 100 Zeichen
   - Graceful degradation statt Abstürzen

4. **Port-Scan-Threading**
   - Verhindert Race Conditions durch bessere Lock-Strategie
   - Korrekte Cleanup-Logik beim Scan-Abbruch

### 📊 Performance

- **Port-Scan**: ~40 Sekunden für 10.000 Ports (256 parallele Verbindungen)
- **Netzwerk-Scan**: ~2-3 Sekunden für /24-Netz mit 128 Concurrency
- **UI-Updates**: 60 FPS dank optimiertem Rendering
- **Memory-Footprint**: ~30 MB für volles /24-Netz mit Port-Scans

### 📝 Dokumentation

- README komplett überarbeitet mit:
  - Strukturierter Inhaltsverzeichnis
  - Detaillierte TUI-Beschreibung
  - Tabelle mit Tastenkombinationen
  - Performance-Tipps
  - Bekannte Einschränkungen
- Neue Release Notes (diese Datei)
- Inline-Code-Dokumentation verbessert

### 🔄 Breaking Changes

Keine! Alle bestehenden CLI-Optionen und Funktionen bleiben erhalten.

### 🎯 Was kommt als Nächstes?

Siehe Roadmap in README.md:
- IPv6-Unterstützung
- Export-Funktionen (CSV, JSON, HTML)
- Historische Daten und Diff-Ansicht
- Banner-Grabbing für Service-Detection
- Scan-Profile (Quick/Normal/Thorough)

---

## Version 0.1.0 (Baseline)

Initiales Release mit:
- Basis-Netzwerk-Scanning (ICMP)
- Einfache TUI mit Host-Liste
- CLI-Modus mit JSON-Ausgabe
- Hostname- und MAC-Resolution
- Basic Port-Scanning (Top 1000)
- Traffic-Monitoring

---

**Installation & Upgrade:**
```bash
# Aktuelles Repo pullen
git pull origin v0.1.1

# Oder neu installieren
pip install -e .
```

**Support:**
Bei Fragen oder Problemen bitte ein Issue auf GitHub erstellen.

**Danke an alle Tester und Contributors! 🙏**
