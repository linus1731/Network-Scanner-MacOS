# Network Scanner - Projekt Roadmap

## Übersicht
Dieser Dokument enthält einen detaillierten Plan für alle zukünftigen Features, organisiert nach Priorität und Komplexität.

---

## 🎯 Phase 1: TUI Enhancement & Usability (v0.2.0)
**Zeitraum**: 3-4 Wochen  
**Fokus**: TUI-Settings, Feature-Integration, dann Export & Profile

### Task 10: TUI Settings Panel & Feature-Integration 🎛️
**Priorität**: P0 (MUSS ZUERST!) | **Komplexität**: Mittel-Hoch | **Geschätzte Zeit**: 1-2 Wochen

**Warum zuerst?** Legt das Framework fest, damit alle nachfolgenden Features (Export, Profile, Rate-Limits) direkt über die TUI nutzbar sind!

#### Subtasks (31 insgesamt):
- [ ] **10.1 Settings-Panel-Framework**
  - [ ] 10.1.1 Settings-Datenstruktur mit allen konfigurierbaren Parametern
  - [ ] 10.1.2 Settings-Panel-UI mit 7 Kategorien-Navigation
  - [ ] 10.1.3 Input-Widgets (Text, Number, Toggle, Dropdown, Slider, etc.)
  - [ ] 10.1.4 Hotkeys im Settings-Panel (Navigation, Edit, Save, Reset)

- [ ] **10.2 Feature-Integration in TUI**
  - [ ] 10.2.1 Export-Integration (Hotkey `e`, Format-Auswahl, Live-Vorschau)
  - [ ] 10.2.2 Profile-Integration (Hotkey `p`, Auswahl, Bearbeiten, Erstellen)
  - [ ] 10.2.3 Scan-Optionen-Dialog (Hotkey `Ctrl+N`, CIDR, Concurrency, Port-Range)
  - [ ] 10.2.4 Rate-Limit-Control (Hotkey `Ctrl+L`, Live-Graph, Presets)
  - [ ] 10.2.5 History-Browser (Hotkey `h`, Timeline, Diff-View, Load/Export)
  - [ ] 10.2.6 Banner-Info-Panel (Auto-Anzeige, Per-Port-Details, Copy)
  - [ ] 10.2.7 mDNS-Services-Panel (Hotkey `m`, Service-Typen, TXT-Records)
  - [ ] 10.2.8 Network-Interface-Selector (Hotkey `i`, Interface-Liste, Auto-CIDR)

- [ ] **10.3 Main Menu & Quick Actions**
  - [ ] 10.3.1 Main Menu (Hotkey `F1`, alle Funktionen aufrufbar)
  - [ ] 10.3.2 Quick Actions Bar (F1-F10 Shortcuts in Statusleiste)
  - [ ] 10.3.3 Help-Overlay (Hotkey `?`, alle Hotkeys dokumentiert)

- [ ] **10.4 Settings-Kategorien** (7 Kategorien mit ~30 Einstellungen)
- [ ] **10.5 Keyboard-Navigation** (Global + Context Hotkeys)
- [ ] **10.6 Theme-System** (Optional: Dark/Light/Custom)

**Impact**: 🚀 **MASSIVE UX-Verbesserung** - Alle Features werden über intuitive TUI zugänglich, keine CLI-Kenntnisse mehr nötig!

**Dateien**: `settings.py`, `tui_settings.py`, `widgets.py`, `tui_export.py`, `tui_profile.py`, `tui_history.py`, `tui_menu.py`, `tui_help.py`, `themes.py`, `config_manager.py`, `~/.netscan/config.yaml`

**Details**: Siehe `.tasks/TASK_10_TUI_SETTINGS.md` für vollständige Spezifikation

---

### Task 1: Zusätzliche Ausgabeformate
**Priorität**: P0 | **Komplexität**: Niedrig | **Geschätzte Zeit**: 3-5 Tage

**Hinweis**: Wird durch Task 10.2.1 direkt in TUI integrierbar!

#### Subtasks:
- [ ] **1.1 CSV-Export implementieren**
  - [ ] 1.1.1 CSV-Writer-Funktion in `netscan/export.py` erstellen
  - [ ] 1.1.2 CLI-Option `--output-csv <datei>` hinzufügen
  - [ ] 1.1.3 Spalten: IP, Status, Latenz, Hostname, MAC, Vendor, Ports
  - [ ] 1.1.4 Escaping für Kommas und Anführungszeichen
  - [ ] 1.1.5 Tests schreiben

- [ ] **1.2 Markdown-Export implementieren**
  - [ ] 1.2.1 Markdown-Tabellen-Generator erstellen
  - [ ] 1.2.2 CLI-Option `--output-md <datei>` hinzufügen
  - [ ] 1.2.3 Schöne Formatierung mit Pipes und Header
  - [ ] 1.2.4 Optional: Emoji für Status (✅/❌)
  - [ ] 1.2.5 Tests schreiben

- [ ] **1.3 HTML-Export implementieren**
  - [ ] 1.3.1 HTML-Template mit CSS erstellen
  - [ ] 1.3.2 CLI-Option `--output-html <datei>` hinzufügen
  - [ ] 1.3.3 Interaktive Tabelle mit Sortierung (JavaScript)
  - [ ] 1.3.4 Responsive Design für mobile Geräte
  - [ ] 1.3.5 Farbcodierung wie in TUI
  - [ ] 1.3.6 Tests schreiben

- [ ] **1.4 Export-Funktion in TUI**
  - [ ] 1.4.1 Tastenkombination `e` für Export-Menü
  - [ ] 1.4.2 Popup-Menü mit Format-Auswahl (CSV/MD/HTML/JSON)
  - [ ] 1.4.3 Dateiname-Eingabe (mit Default: `scan_YYYYMMDD_HHMMSS.ext`)
  - [ ] 1.4.4 Fortschrittsanzeige während Export
  - [ ] 1.4.5 Erfolgsmeldung oder Fehlerbehandlung

**Vorgehensweise:**
1. Neues Modul `netscan/export.py` erstellen
2. Basis-Klasse `Exporter` mit Interface definieren
3. Subklassen: `CSVExporter`, `MarkdownExporter`, `HTMLExporter`
4. Integration in CLI und TUI
5. Dokumentation und Tests

---

### Task 2: Konfigurierbare Rate-Limits
**Priorität**: Mittel | **Komplexität**: Niedrig | **Geschätzte Zeit**: 2-3 Tage

#### Subtasks:
- [ ] **2.1 Rate-Limiter-Klasse erstellen**
  - [ ] 2.1.1 Token-Bucket-Algorithmus implementieren
  - [ ] 2.1.2 Konfigurierbare Rate (Pakete/Sekunde)
  - [ ] 2.1.3 Burst-Größe konfigurierbar
  - [ ] 2.1.4 Thread-sicher mit Locks

- [ ] **2.2 Integration in Scanner**
  - [ ] 2.2.1 Rate-Limiter in `scan_cidr()` integrieren
  - [ ] 2.2.2 Rate-Limiter in `port_scan()` integrieren
  - [ ] 2.2.3 CLI-Option `--rate-limit <n>` (Pakete/Sekunde)
  - [ ] 2.2.4 CLI-Option `--burst <n>` (Max. gleichzeitige Pakete)

- [ ] **2.3 TUI-Integration**
  - [ ] 2.3.1 Rate-Limit-Anzeige im Header
  - [ ] 2.3.2 Hotkey für Rate-Limit-Anpassung (z.B. `+`/`-`)
  - [ ] 2.3.3 Visuelle Throttling-Indikator

- [ ] **2.4 Tests und Dokumentation**
  - [ ] 2.4.1 Unit-Tests für Rate-Limiter
  - [ ] 2.4.2 Integration-Tests mit verschiedenen Raten
  - [ ] 2.4.3 Dokumentation in README

**Vorgehensweise:**
1. `netscan/ratelimit.py` mit Token-Bucket erstellen
2. Wrapper um ThreadPoolExecutor für Rate-Limiting
3. CLI-Optionen hinzufügen
4. TUI-Features implementieren
5. Performance-Tests durchführen

---

## 🚀 Phase 2: Core Features (2-4 Wochen)

### Task 3: Scan-Profile
**Priorität**: Hoch | **Komplexität**: Mittel | **Geschätzte Zeit**: 4-6 Tage

#### Subtasks:
- [ ] **3.1 Profile-System entwerfen**
  - [ ] 3.1.1 Profil-Klasse mit Konfigurationsparametern
  - [ ] 3.1.2 Vordefinierte Profile: Quick, Normal, Thorough, Stealth
  - [ ] 3.1.3 YAML/JSON-Konfigurationsdatei-Support
  - [ ] 3.1.4 Custom-Profile-Support (`~/.netscan/profiles/`)

- [ ] **3.2 Profile-Parameter definieren**
  - [ ] 3.2.1 **Quick**: concurrency=256, timeout=0.5, ports=top100
  - [ ] 3.2.2 **Normal**: concurrency=128, timeout=1.0, ports=top1000
  - [ ] 3.2.3 **Thorough**: concurrency=64, timeout=2.0, ports=1-10000
  - [ ] 3.2.4 **Stealth**: concurrency=10, timeout=3.0, ports=custom, random-delay

- [ ] **3.3 CLI-Integration**
  - [ ] 3.3.1 Option `--profile <name>` hinzufügen
  - [ ] 3.3.2 Option `--list-profiles` für Übersicht
  - [ ] 3.3.3 Option `--save-profile <name>` für Custom-Profiles
  - [ ] 3.3.4 Profil-Override mit anderen Optionen erlauben

- [ ] **3.4 TUI-Integration**
  - [ ] 3.4.1 Profil-Auswahl beim Start
  - [ ] 3.4.2 Hotkey `Shift+P` für Profil-Wechsel während Laufzeit
  - [ ] 3.4.3 Anzeige des aktiven Profils im Header
  - [ ] 3.4.4 Profil-spezifische Farben/Symbole

- [ ] **3.5 Dokumentation**
  - [ ] 3.5.1 Profil-Vergleichstabelle in README
  - [ ] 3.5.2 Beispiel-Custom-Profile im Repo
  - [ ] 3.5.3 Use-Cases für jedes Profil dokumentieren

**Vorgehensweise:**
1. `netscan/profiles.py` mit Profile-Management erstellen
2. Vordefinierte Profile implementieren
3. Config-File-Loader (YAML) hinzufügen
4. CLI und TUI integrieren
5. Beispiel-Profiles erstellen

---

### Task 4: Service-Banner-Grabbing
**Priorität**: Mittel | **Komplexität**: Mittel | **Geschätzte Zeit**: 5-7 Tage

#### Subtasks:
- [ ] **4.1 Banner-Grabbing-Engine**
  - [ ] 4.1.1 Socket-basierter Banner-Reader
  - [ ] 4.1.2 Protokoll-spezifische Probes (HTTP, SSH, FTP, SMTP, etc.)
  - [ ] 4.1.3 Timeout-Handling (2-5 Sekunden)
  - [ ] 4.1.4 SSL/TLS-Support für HTTPS, SMTPS, etc.

- [ ] **4.2 Service-Detection**
  - [ ] 4.2.1 Pattern-Matching für bekannte Services
  - [ ] 4.2.2 Version-Extraction aus Bannern
  - [ ] 4.2.3 OS-Fingerprinting (basic) aus Bannern
  - [ ] 4.2.4 Vulnerability-Keywords-Detection (optional)

- [ ] **4.3 Integration**
  - [ ] 4.3.1 Banner-Grabbing als optionaler Schritt nach Port-Scan
  - [ ] 4.3.2 CLI-Option `--grab-banners`
  - [ ] 4.3.3 TUI: Banner in Detail-Panel anzeigen
  - [ ] 4.3.4 Export: Banner-Informationen in Ausgabe-Formaten

- [ ] **4.4 Datenbank**
  - [ ] 4.4.1 Service-Signature-Datenbank (nmap-service-probes inspiriert)
  - [ ] 4.4.2 Version-Datenbank für bekannte Software
  - [ ] 4.4.3 Update-Mechanismus für Signaturen

- [ ] **4.5 Performance & Safety**
  - [ ] 4.5.1 Concurrency-Limit für Banner-Grabbing
  - [ ] 4.5.2 Sichere Bytes-Handling (kein Code-Execution)
  - [ ] 4.5.3 Malformed-Banner-Handling

**Vorgehensweise:**
1. `netscan/banners.py` mit Basic-Implementation
2. Protokoll-spezifische Probes implementieren
3. Pattern-Matching-Engine erstellen
4. Integration in Port-Scanner
5. TUI-Anzeige erweitern
6. Tests mit verschiedenen Services

---

### Task 5: Erweiterte OUI-Datenbank
**Priorität**: Hoch | **Komplexität**: Niedrig | **Geschätzte Zeit**: 2-3 Tage

#### Subtasks:
- [ ] **5.1 Datenbank-Downloads**
  - [ ] 5.1.1 Wireshark manuf-Datei automatisch herunterladen
  - [ ] 5.1.2 IEEE OUI-Liste als Fallback
  - [ ] 5.1.3 Nmap mac-prefixes als Alternative
  - [ ] 5.1.4 Update-Check bei Start (optional, cached)

- [ ] **5.2 Parser-Verbesserungen**
  - [ ] 5.2.1 Unterstützung für 24, 28, 36 Bit Präfixe
  - [ ] 5.2.2 Bessere Normalisierung von Vendor-Namen
  - [ ] 5.2.3 Company-Aliases und Mergers behandeln

- [ ] **5.3 Cache-System**
  - [ ] 5.3.1 Lokaler Cache in `~/.netscan/oui-cache/`
  - [ ] 5.3.2 Automatische Updates (wöchentlich)
  - [ ] 5.3.3 Offline-Fallback auf embedded DB

- [ ] **5.4 CLI-Tools**
  - [ ] 5.4.1 `netscan-update-oui` Kommando
  - [ ] 5.4.2 `netscan-lookup-mac <mac>` Utility
  - [ ] 5.4.3 Statistiken über DB-Größe und Abdeckung

**Vorgehensweise:**
1. Download-Script für OUI-Datenbanken
2. Erweiterten Parser implementieren
3. Cache-System mit Versionierung
4. CLI-Tools erstellen
5. Dokumentation

---

## 🔬 Phase 3: Advanced Features (4-8 Wochen)

### Task 6: IPv6-Unterstützung
**Priorität**: Mittel | **Komplexität**: Hoch | **Geschätzte Zeit**: 8-12 Tage

#### Subtasks:
- [ ] **6.1 IPv6-Grundlagen**
  - [ ] 6.1.1 IPv6-Adress-Parsing und -Validation
  - [ ] 6.1.2 IPv6-CIDR-Notation-Support
  - [ ] 6.1.3 Link-Local vs Global Addresses
  - [ ] 6.1.4 IPv6-Präfix-Handling (/64, /56, etc.)

- [ ] **6.2 ICMPv6-Scanning**
  - [ ] 6.2.1 ICMPv6 Echo Request/Reply
  - [ ] 6.2.2 Neighbor Discovery Protocol (NDP)
  - [ ] 6.2.3 Multicast-basierte Discovery
  - [ ] 6.2.4 IPv6-spezifische Timeouts

- [ ] **6.3 Dual-Stack-Support**
  - [ ] 6.3.1 Automatische Erkennung von IPv4/IPv6-Fähigkeit
  - [ ] 6.3.2 Paralleles Scannen von IPv4 und IPv6
  - [ ] 6.3.3 CLI-Option `--ipv4` / `--ipv6` / `--dual-stack`
  - [ ] 6.3.4 Separate Darstellung in TUI

- [ ] **6.4 IPv6-spezifische Features**
  - [ ] 6.4.1 SLAAC-Adress-Generierung-Erkennung
  - [ ] 6.4.2 Privacy-Extensions-Erkennung
  - [ ] 6.4.3 IPv6-to-MAC-Mapping
  - [ ] 6.4.4 Reverse DNS für IPv6 (PTR)

- [ ] **6.5 Port-Scanning für IPv6**
  - [ ] 6.5.1 TCP/IPv6-Connect-Scan
  - [ ] 6.5.2 Anpassungen für IPv6-Sockets
  - [ ] 6.5.3 Performance-Optimierungen

- [ ] **6.6 TUI-Anpassungen**
  - [ ] 6.6.1 Längere IP-Adressen in Tabelle anzeigen
  - [ ] 6.6.2 IPv4/IPv6-Filter-Toggle
  - [ ] 6.6.3 Dual-Stack-Hosts zusammenfassen oder trennen

**Vorgehensweise:**
1. IPv6-Parser und -Validator implementieren
2. ICMPv6-Scanning (erfordert ggf. Raw Sockets)
3. Dual-Stack-Logik entwickeln
4. TUI-Layout für längere Adressen anpassen
5. Umfangreiche Tests in IPv6-Netzwerken
6. Dokumentation mit IPv6-Beispielen

---

### Task 7: Aktives mDNS-Browsing
**Priorität**: Mittel | **Komplexität**: Mittel-Hoch | **Geschätzte Zeit**: 6-8 Tage

#### Subtasks:
- [ ] **7.1 mDNS-Client**
  - [ ] 7.1.1 mDNS-Query-Sender (Multicast zu 224.0.0.251:5353)
  - [ ] 7.1.2 mDNS-Response-Parser
  - [ ] 7.1.3 Service-Discovery-Queries (_http._tcp, _ssh._tcp, etc.)
  - [ ] 7.1.4 Async-Collection von Responses

- [ ] **7.2 Service-Enumeration**
  - [ ] 7.2.1 Liste von Standard-mDNS-Services
  - [ ] 7.2.2 Automatische Service-Type-Discovery
  - [ ] 7.2.3 TXT-Record-Parsing für zusätzliche Infos
  - [ ] 7.2.4 Priorisierung von bekannten Services

- [ ] **7.3 Integration**
  - [ ] 7.3.1 mDNS-Scan als optionaler Schritt
  - [ ] 7.3.2 CLI-Option `--mdns`
  - [ ] 7.3.3 TUI: mDNS-Services in Detail-Panel
  - [ ] 7.3.4 Timeout für mDNS-Discovery (5-10 Sekunden)

- [ ] **7.4 Platform-spezifisch**
  - [ ] 7.4.1 macOS: Bonjour-Integration (optional)
  - [ ] 7.4.2 Linux: avahi-browse als Fallback
  - [ ] 7.4.3 Pure-Python-Fallback für alle Plattformen

**Vorgehensweise:**
1. mDNS-Protokoll-Implementation (RFC 6762)
2. Service-Discovery-Logik
3. Integration in Resolution-Pipeline
4. Platform-spezifische Optimierungen
5. Tests in mDNS-reichen Netzwerken

---

### Task 8: ARP/NDP-Discovery
**Priorität**: Hoch | **Komplexität**: Mittel-Hoch | **Geschätzte Zeit**: 5-7 Tage

#### Subtasks:
- [ ] **8.1 ARP-Discovery (IPv4)**
  - [ ] 8.1.1 Raw-ARP-Requests senden (erfordert Root/Admin)
  - [ ] 8.1.2 ARP-Response-Listener
  - [ ] 8.1.3 Gratuitous-ARP für passive Discovery
  - [ ] 8.1.4 ARP-Cache-Prefilling

- [ ] **8.2 NDP-Discovery (IPv6)**
  - [ ] 8.2.1 ICMPv6 Neighbor Solicitation senden
  - [ ] 8.2.2 Neighbor Advertisement empfangen
  - [ ] 8.2.3 Router Advertisement auswerten
  - [ ] 8.2.4 NDP-Cache-Integration

- [ ] **8.3 Permission-Handling**
  - [ ] 8.3.1 Root-Check und User-Warnung
  - [ ] 8.3.2 Fallback auf Ping-basierte Discovery ohne Root
  - [ ] 8.3.3 Platform-spezifische Privilege-Escalation-Hinweise

- [ ] **8.4 Integration**
  - [ ] 8.4.1 ARP/NDP als primäre Discovery-Methode
  - [ ] 8.4.2 CLI-Option `--use-arp` / `--use-ndp`
  - [ ] 8.4.3 Kombination mit ICMP-Scan
  - [ ] 8.4.4 TUI: Discovery-Methode anzeigen

**Vorgehensweise:**
1. Raw-Socket-Implementation für ARP
2. ICMPv6-NDP-Implementation
3. Permission-Handling und Fallbacks
4. Integration als primäre Discovery
5. Tests mit/ohne Root-Rechten
6. Dokumentation mit Security-Hinweisen

---

### Task 9: Historische Daten und Änderungsverfolgung
**Priorität**: Niedrig | **Komplexität**: Hoch | **Geschätzte Zeit**: 10-14 Tage

#### Subtasks:
- [ ] **9.1 Datenbank-Schema**
  - [ ] 9.1.1 SQLite-Datenbank in `~/.netscan/history.db`
  - [ ] 9.1.2 Schema: Scans, Hosts, Ports, Changes
  - [ ] 9.1.3 Indizes für schnelle Queries
  - [ ] 9.1.4 Auto-Cleanup alter Daten (configurable)

- [ ] **9.2 Scan-Historie**
  - [ ] 9.2.1 Jeden Scan mit Timestamp speichern
  - [ ] 9.2.2 Host-Status-Historie (UP/DOWN über Zeit)
  - [ ] 9.2.3 Port-Änderungen tracken (neu geöffnet/geschlossen)
  - [ ] 9.2.4 Hostname/MAC-Änderungen erkennen

- [ ] **9.3 Diff-Engine**
  - [ ] 9.3.1 Vergleich zwischen zwei Scans
  - [ ] 9.3.2 Change-Detection-Algorithmus
  - [ ] 9.3.3 Kategorisierung: New, Changed, Disappeared
  - [ ] 9.3.4 Confidence-Score für Änderungen

- [ ] **9.4 TUI-Integration**
  - [ ] 9.4.1 History-View mit Timeline
  - [ ] 9.4.2 Hotkey `h` für History-Panel
  - [ ] 9.4.3 Grafische Darstellung von Up/Down-Phasen
  - [ ] 9.4.4 Change-Highlighting in Host-Liste

- [ ] **9.5 CLI-Tools**
  - [ ] 9.5.1 `netscan-history --list` für Scan-Übersicht
  - [ ] 9.5.2 `netscan-history --diff <id1> <id2>` für Vergleich
  - [ ] 9.5.3 `netscan-history --export` für Datenexport
  - [ ] 9.5.4 `netscan-history --cleanup` für alte Daten

- [ ] **9.6 Visualisierungen**
  - [ ] 9.6.1 ASCII-Grafiken für Uptime-Statistiken
  - [ ] 9.6.2 Heatmap für Netzwerk-Aktivität
  - [ ] 9.6.3 HTML-Report mit Charts (Chart.js)

**Vorgehensweise:**
1. Datenbank-Schema und ORM (sqlite3)
2. Background-Writer für Scan-Results
3. Diff-Engine implementieren
4. TUI-History-View erstellen
5. CLI-Tools für History-Management
6. Visualisierungen und Reports
7. Performance-Tests mit großen Datenmengen

---

## 📊 Implementierungs-Strategie

### Gesamte Vorgehensweise:

1. **Phase 1 (Quick Wins)** - 2-3 Wochen
   - Start mit Export-Formaten (sofortiger Mehrwert)
   - Parallel: Rate-Limits implementieren
   - Abschluss: Scan-Profile

2. **Phase 2 (Core Features)** - 4-5 Wochen
   - Banner-Grabbing für bessere Service-Detection
   - Erweiterte OUI-Datenbank
   - Parallel: Dokumentation aktualisieren

3. **Phase 3 (Advanced Features)** - 6-10 Wochen
   - IPv6-Support (größte Änderung)
   - mDNS und ARP/NDP Discovery
   - Historische Daten als Abschluss

### Prioritäten-Matrix:

| Feature | Business Value | Technical Complexity | Priority Score |
|---------|---------------|---------------------|----------------|
| Export-Formate | ⭐⭐⭐⭐⭐ | ⭐⭐ | **P0** |
| Scan-Profile | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **P0** |
| Rate-Limits | ⭐⭐⭐⭐ | ⭐⭐ | **P1** |
| OUI-Datenbank | ⭐⭐⭐⭐ | ⭐⭐ | **P1** |
| Banner-Grabbing | ⭐⭐⭐⭐ | ⭐⭐⭐ | **P1** |
| IPv6-Support | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **P2** |
| mDNS-Browsing | ⭐⭐⭐ | ⭐⭐⭐⭐ | **P2** |
| ARP/NDP-Discovery | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **P2** |
| History & Diff | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **P3** |

### Testing-Strategie:

Für jedes Feature:
1. **Unit-Tests**: Einzelne Funktionen testen
2. **Integration-Tests**: Zusammenspiel mit bestehendem Code
3. **System-Tests**: End-to-End in realen Netzwerken
4. **Performance-Tests**: Skalierbarkeit und Geschwindigkeit
5. **Security-Tests**: Insbesondere bei Raw Sockets

### Dokumentations-Plan:

Nach jeder Phase:
- README aktualisieren
- Release Notes erweitern
- Code-Kommentare vervollständigen
- Beispiele in `examples/` Ordner
- GIFs/Screenshots für neue Features

---

## 🔧 Technische Entscheidungen

### Neue Abhängigkeiten (optional):

| Dependency | Zweck | Priorität |
|------------|-------|-----------|
| `pyyaml` | Config-Files für Profile | Optional |
| `scapy` | Raw Packet Crafting (ARP/NDP) | Optional (Fallback auf System-Tools) |
| `sqlite3` | History-Datenbank | Built-in |
| `jinja2` | HTML-Template-Engine | Optional (Simple Alternative möglich) |

**Philosophie**: Minimale Dependencies, Pure-Python bevorzugen, optionale Features mit Fallbacks

---

## 📈 Milestones

- **M1**: Export-Formate + Rate-Limits (v0.2.0)
- **M2**: Scan-Profile + Banner-Grabbing (v0.3.0)
- **M3**: Erweiterte OUI + mDNS (v0.4.0)
- **M4**: IPv6-Support (v0.5.0)
- **M5**: History & Diff (v1.0.0)

---

## 🎯 Nächste Schritte

1. **Review dieses Plans** mit Team/Community
2. **Issue-Tracking**: GitHub Issues für jeden Task erstellen
3. **Branch-Strategy**: Feature-Branches für größere Tasks
4. **CI/CD**: Automatische Tests bei jedem Push
5. **Start mit Task 1.1** (CSV-Export) als Proof-of-Concept

---

**Erstellt am**: 6. Oktober 2025  
**Status**: 📋 Planning Phase  
**Nächstes Update**: Nach M1-Release

**Fragen oder Vorschläge?** → GitHub Issues oder Diskussionen
