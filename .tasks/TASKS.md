# Network Scanner - Task Tracking

> **Letztes Update**: 6. Oktober 2025  
> **Aktueller Branch**: v0.1.1  
> **Aktuelle Version**: 0.1.1

---

## 📊 Projekt-Status Overview

### Abgeschlossen ✅
- [x] v0.1.1 - Modern TUI with Split-Panel Layout
- [x] Port-Scanning erweitert (10.000 Ports)
- [x] Auto-Port-Scan beim Navigieren
- [x] Unicode-Box-Design
- [x] Release Notes und README erstellt

### In Arbeit 🚧
- [ ] _Keine aktiven Tasks_

### Geplant 📋
- Phase 1: Export-Formate, Rate-Limits, Scan-Profile
- Phase 2: Banner-Grabbing, OUI-Datenbank
- Phase 3: IPv6, mDNS, ARP/NDP, History

---

## 🎯 Phase 1: Quick Wins (Status: 0/14 Tasks)

### Task 1: Zusätzliche Ausgabeformate
**Status**: 🚧 In Arbeit | **Priorität**: P0 | **Geschätzt**: 3-5 Tage

- [x] **1.1 CSV-Export**
  - [x] 1.1.1 `netscan/export.py` mit CSVExporter-Klasse
  - [x] 1.1.2 CLI-Option `--output-csv <datei>`
  - [x] 1.1.3 Spalten: IP, Status, Latenz, Hostname, MAC, Vendor, Ports
  - [x] 1.1.4 Escaping für Kommas und Anführungszeichen
  - [x] 1.1.5 Unit-Tests schreiben

- [x] **1.2 Markdown-Export**
  - [x] 1.2.1 MarkdownExporter-Klasse
  - [x] 1.2.2 CLI-Option `--output-md <datei>`
  - [x] 1.2.3 Pipe-Tabellen mit Header
  - [x] 1.2.4 Optional: Status-Emoji (✅/❌)
  - [x] 1.2.5 Unit-Tests schreiben

- [ ] **1.3 HTML-Export**
  - [ ] 1.3.1 HTML-Template mit CSS
  - [ ] 1.3.2 CLI-Option `--output-html <datei>`
  - [ ] 1.3.3 Interaktive sortierbare Tabelle (JS)
  - [ ] 1.3.4 Responsive Design
  - [ ] 1.3.5 Farbcodierung wie TUI
  - [ ] 1.3.6 Unit-Tests schreiben

- [x] **1.4 TUI-Export**
  - [x] 1.4.1 Hotkey `e` für Export-Menü
  - [x] 1.4.2 Popup mit Format-Auswahl
  - [x] 1.4.3 Dateiname-Eingabe mit Default
  - [x] 1.4.4 Fortschrittsanzeige
  - [x] 1.4.5 Erfolgsmeldung

**Dateien zu erstellen/ändern**:
- `netscan/export.py` (NEU)
- `netscan/cli.py` (CLI-Optionen)
- `netscan/tui.py` (Export-Menü)
- `tests/test_export.py` (NEU)

---

### Task 2: Konfigurierbare Rate-Limits
**Status**: ⬜ Nicht gestartet | **Priorität**: P1 | **Geschätzt**: 2-3 Tage

- [ ] **2.1 Rate-Limiter-Klasse**
  - [ ] 2.1.1 Token-Bucket-Algorithmus
  - [ ] 2.1.2 Konfigurierbare Rate (Pakete/Sekunde)
  - [ ] 2.1.3 Burst-Größe
  - [ ] 2.1.4 Thread-sicher mit Locks

- [ ] **2.2 Scanner-Integration**
  - [ ] 2.2.1 In `scan_cidr()` integrieren
  - [ ] 2.2.2 In `port_scan()` integrieren
  - [ ] 2.2.3 CLI `--rate-limit <n>`
  - [ ] 2.2.4 CLI `--burst <n>`

- [ ] **2.3 TUI-Integration**
  - [ ] 2.3.1 Rate im Header anzeigen
  - [ ] 2.3.2 Hotkey `+`/`-` für Anpassung
  - [ ] 2.3.3 Throttling-Indikator

- [ ] **2.4 Tests**
  - [ ] 2.4.1 Unit-Tests
  - [ ] 2.4.2 Integration-Tests
  - [ ] 2.4.3 Dokumentation

**Dateien zu erstellen/ändern**:
- `netscan/ratelimit.py` (NEU)
- `netscan/scanner.py` (Integration)
- `netscan/cli.py` (Optionen)
- `netscan/tui.py` (UI)
- `tests/test_ratelimit.py` (NEU)

---

### Task 3: Scan-Profile
**Status**: ⬜ Nicht gestartet | **Priorität**: P0 | **Geschätzt**: 4-6 Tage

- [ ] **3.1 Profile-System**
  - [ ] 3.1.1 Profile-Klasse mit Config
  - [ ] 3.1.2 Vordefinierte Profile: Quick, Normal, Thorough, Stealth
  - [ ] 3.1.3 YAML-Konfigurationsdatei-Support
  - [ ] 3.1.4 Custom-Profile (`~/.netscan/profiles/`)

- [ ] **3.2 Profile-Parameter**
  - [ ] 3.2.1 Quick: concurrency=256, timeout=0.5, ports=top100
  - [ ] 3.2.2 Normal: concurrency=128, timeout=1.0, ports=top1000
  - [ ] 3.2.3 Thorough: concurrency=64, timeout=2.0, ports=1-10000
  - [ ] 3.2.4 Stealth: concurrency=10, timeout=3.0, random-delay

- [ ] **3.3 CLI-Integration**
  - [ ] 3.3.1 `--profile <name>`
  - [ ] 3.3.2 `--list-profiles`
  - [ ] 3.3.3 `--save-profile <name>`
  - [ ] 3.3.4 Override-Optionen

- [ ] **3.4 TUI-Integration**
  - [ ] 3.4.1 Profil-Auswahl beim Start
  - [ ] 3.4.2 Hotkey `Shift+P` für Wechsel
  - [ ] 3.4.3 Aktives Profil im Header
  - [ ] 3.4.4 Profil-spezifische Farben

- [ ] **3.5 Dokumentation**
  - [ ] 3.5.1 Profil-Vergleichstabelle
  - [ ] 3.5.2 Beispiel-Custom-Profile
  - [ ] 3.5.3 Use-Cases dokumentieren

**Dateien zu erstellen/ändern**:
- `netscan/profiles.py` (NEU)
- `netscan/cli.py` (Optionen)
- `netscan/tui.py` (Profil-Auswahl)
- `~/.netscan/profiles/` (Config-Verzeichnis)
- `examples/custom-profiles/` (NEU)
- `tests/test_profiles.py` (NEU)

---

## 🚀 Phase 2: Core Features (Status: 0/23 Tasks)

### Task 4: Service-Banner-Grabbing
**Status**: ⬜ Nicht gestartet | **Priorität**: P1 | **Geschätzt**: 5-7 Tage

- [ ] **4.1 Banner-Grabbing-Engine**
  - [ ] 4.1.1 Socket-basierter Banner-Reader
  - [ ] 4.1.2 Protokoll-spezifische Probes (HTTP, SSH, FTP, SMTP)
  - [ ] 4.1.3 Timeout-Handling (2-5 Sek)
  - [ ] 4.1.4 SSL/TLS-Support

- [ ] **4.2 Service-Detection**
  - [ ] 4.2.1 Pattern-Matching für Services
  - [ ] 4.2.2 Version-Extraction
  - [ ] 4.2.3 OS-Fingerprinting (basic)
  - [ ] 4.2.4 Vulnerability-Keywords (optional)

- [ ] **4.3 Integration**
  - [ ] 4.3.1 Nach Port-Scan ausführen
  - [ ] 4.3.2 CLI `--grab-banners`
  - [ ] 4.3.3 TUI: Banner in Detail-Panel
  - [ ] 4.3.4 Export: Banner in Ausgaben

- [ ] **4.4 Datenbank**
  - [ ] 4.4.1 Service-Signature-DB
  - [ ] 4.4.2 Version-Datenbank
  - [ ] 4.4.3 Update-Mechanismus

- [ ] **4.5 Performance & Safety**
  - [ ] 4.5.1 Concurrency-Limit
  - [ ] 4.5.2 Sicheres Bytes-Handling
  - [ ] 4.5.3 Malformed-Banner-Handling

**Dateien zu erstellen/ändern**:
- `netscan/banners.py` (NEU)
- `netscan/scanner.py` (Integration)
- `netscan/tui.py` (Banner-Anzeige)
- `data/service-signatures.json` (NEU)
- `tests/test_banners.py` (NEU)

---

### Task 5: Erweiterte OUI-Datenbank
**Status**: ⬜ Nicht gestartet | **Priorität**: P1 | **Geschätzt**: 2-3 Tage

- [ ] **5.1 Datenbank-Downloads**
  - [ ] 5.1.1 Wireshark manuf auto-download
  - [ ] 5.1.2 IEEE OUI-Liste Fallback
  - [ ] 5.1.3 Nmap mac-prefixes Alternative
  - [ ] 5.1.4 Update-Check (cached)

- [ ] **5.2 Parser-Verbesserungen**
  - [ ] 5.2.1 24, 28, 36 Bit Präfixe
  - [ ] 5.2.2 Vendor-Namen-Normalisierung
  - [ ] 5.2.3 Company-Aliases

- [ ] **5.3 Cache-System**
  - [ ] 5.3.1 Lokaler Cache `~/.netscan/oui-cache/`
  - [ ] 5.3.2 Auto-Updates (wöchentlich)
  - [ ] 5.3.3 Offline-Fallback

- [ ] **5.4 CLI-Tools**
  - [ ] 5.4.1 `netscan-update-oui`
  - [ ] 5.4.2 `netscan-lookup-mac <mac>`
  - [ ] 5.4.3 DB-Statistiken

**Dateien zu erstellen/ändern**:
- `netscan/vendor.py` (erweitern)
- `netscan/oui_updater.py` (NEU)
- `scripts/update-oui.py` (NEU)
- `~/.netscan/oui-cache/` (Cache-Verzeichnis)
- `tests/test_vendor.py` (erweitern)

---

## 🔬 Phase 3: Advanced Features (Status: 0/32 Tasks)

### Task 6: IPv6-Unterstützung
**Status**: ⬜ Nicht gestartet | **Priorität**: P2 | **Geschätzt**: 8-12 Tage

- [ ] **6.1 IPv6-Grundlagen**
  - [ ] 6.1.1 IPv6-Parsing und -Validation
  - [ ] 6.1.2 CIDR-Notation-Support
  - [ ] 6.1.3 Link-Local vs Global
  - [ ] 6.1.4 Präfix-Handling (/64, /56)

- [ ] **6.2 ICMPv6-Scanning**
  - [ ] 6.2.1 ICMPv6 Echo Request/Reply
  - [ ] 6.2.2 Neighbor Discovery (NDP)
  - [ ] 6.2.3 Multicast-Discovery
  - [ ] 6.2.4 IPv6-Timeouts

- [ ] **6.3 Dual-Stack**
  - [ ] 6.3.1 IPv4/IPv6-Auto-Detection
  - [ ] 6.3.2 Paralleles Scannen
  - [ ] 6.3.3 CLI `--ipv4`/`--ipv6`/`--dual-stack`
  - [ ] 6.3.4 Separate TUI-Darstellung

- [ ] **6.4 IPv6-Features**
  - [ ] 6.4.1 SLAAC-Erkennung
  - [ ] 6.4.2 Privacy-Extensions
  - [ ] 6.4.3 IPv6-to-MAC-Mapping
  - [ ] 6.4.4 Reverse DNS (PTR)

- [ ] **6.5 Port-Scanning**
  - [ ] 6.5.1 TCP/IPv6-Connect
  - [ ] 6.5.2 Socket-Anpassungen
  - [ ] 6.5.3 Performance-Optimierungen

- [ ] **6.6 TUI-Anpassungen**
  - [ ] 6.6.1 Längere IPs in Tabelle
  - [ ] 6.6.2 IPv4/IPv6-Filter
  - [ ] 6.6.3 Dual-Stack-Hosts

**Dateien zu erstellen/ändern**:
- `netscan/scanner.py` (IPv6-Support)
- `netscan/netinfo.py` (IPv6-Detection)
- `netscan/resolve.py` (IPv6-PTR)
- `netscan/tui.py` (Layout-Anpassungen)
- `tests/test_ipv6.py` (NEU)

---

### Task 10: TUI Settings Panel & Feature-Integration 🎛️
**Status**: ⬜ Nicht gestartet | **Priorität**: P0 | **Geschätzt**: 1-2 Wochen

- [ ] **10.1 Settings-Panel-Framework**
  - [ ] 10.1.1 Settings-Datenstruktur (Settings-Klasse, Validation, Persistence)
  - [ ] 10.1.2 Settings-Panel-UI (Overlay, 7 Kategorien, Navigation)
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

- [ ] **10.4 Settings-Kategorien**
  - [ ] 10.4.1 General Settings (Theme, Language, Auto-Refresh)
  - [ ] 10.4.2 Scanning Settings (Concurrency, Timeout, Retry)
  - [ ] 10.4.3 Port Scanning Settings (Range, Banners, Auto-Scan)
  - [ ] 10.4.4 Network Settings (Rate-Limit, Interface, IPv6, mDNS)
  - [ ] 10.4.5 Display Settings (Colors, Layout, Panel-Width)
  - [ ] 10.4.6 Export Settings (Default-Format, Auto-Export)
  - [ ] 10.4.7 Advanced Settings (Debug, Logging, Cache)

- [ ] **10.5 Keyboard-Navigation**
  - [ ] 10.5.1 Global Hotkeys (F1-F10, Ctrl+Shortcuts)
  - [ ] 10.5.2 Context-Specific Hotkeys (View-abhängig)
  - [ ] 10.5.3 Hotkey-Hilfe (Context-sensitive, Cheatsheet-Export)

- [ ] **10.6 Theme-System (Optional)**
  - [ ] 10.6.1 Color-Themes (Dark, Light, High-Contrast, Solarized)
  - [ ] 10.6.2 Theme-Configuration (YAML-basiert)
  - [ ] 10.6.3 Theme-Switcher (Live-Preview, Hotkey `Ctrl+T`)

**Dateien zu erstellen**:
- `netscan/settings.py` (Settings-Management)
- `netscan/tui_settings.py` (Settings-Panel UI)
- `netscan/widgets.py` (Input-Widgets)
- `netscan/tui_export.py` (Export-Dialog)
- `netscan/tui_profile.py` (Profile-Menu)
- `netscan/tui_history.py` (History-Browser)
- `netscan/tui_menu.py` (Main-Menu)
- `netscan/tui_help.py` (Help-Overlay)
- `netscan/themes.py` (Theme-System)
- `netscan/config_manager.py` (Config-File-Handler)
- `~/.netscan/config.yaml` (User-Settings)

**Dateien zu ändern**:
- `netscan/tui.py` (Hotkey-Integration, Overlay-System)
- `netscan/cli.py` (Settings-Respekt)

**Siehe**: `.tasks/TASK_10_TUI_SETTINGS.md` für Details

---

### Task 7: Aktives mDNS-Browsing
**Status**: ⬜ Nicht gestartet | **Priorität**: P2 | **Geschätzt**: 6-8 Tage

- [ ] **7.1 mDNS-Client**
  - [ ] 7.1.1 mDNS-Query-Sender
  - [ ] 7.1.2 Response-Parser
  - [ ] 7.1.3 Service-Discovery-Queries
  - [ ] 7.1.4 Async-Collection

- [ ] **7.2 Service-Enumeration**
  - [ ] 7.2.1 Standard-mDNS-Services
  - [ ] 7.2.2 Auto-Service-Discovery
  - [ ] 7.2.3 TXT-Record-Parsing
  - [ ] 7.2.4 Service-Priorisierung

- [ ] **7.3 Integration**
  - [ ] 7.3.1 Als optionaler Schritt
  - [ ] 7.3.2 CLI `--mdns`
  - [ ] 7.3.3 TUI: Services in Detail-Panel
  - [ ] 7.3.4 Timeout 5-10 Sek

- [ ] **7.4 Platform-spezifisch**
  - [ ] 7.4.1 macOS: Bonjour-Integration
  - [ ] 7.4.2 Linux: avahi-browse
  - [ ] 7.4.3 Pure-Python-Fallback

**Dateien zu erstellen/ändern**:
- `netscan/mdns.py` (NEU)
- `netscan/resolve.py` (Integration)
- `netscan/tui.py` (Service-Anzeige)
- `tests/test_mdns.py` (NEU)

---

### Task 8: ARP/NDP-Discovery
**Status**: ⬜ Nicht gestartet | **Priorität**: P2 | **Geschätzt**: 5-7 Tage

- [ ] **8.1 ARP-Discovery**
  - [ ] 8.1.1 Raw-ARP-Requests
  - [ ] 8.1.2 ARP-Response-Listener
  - [ ] 8.1.3 Gratuitous-ARP
  - [ ] 8.1.4 ARP-Cache-Prefilling

- [ ] **8.2 NDP-Discovery**
  - [ ] 8.2.1 ICMPv6 Neighbor Solicitation
  - [ ] 8.2.2 Neighbor Advertisement
  - [ ] 8.2.3 Router Advertisement
  - [ ] 8.2.4 NDP-Cache

- [ ] **8.3 Permission-Handling**
  - [ ] 8.3.1 Root-Check
  - [ ] 8.3.2 Fallback ohne Root
  - [ ] 8.3.3 Platform-spezifische Hinweise

- [ ] **8.4 Integration**
  - [ ] 8.4.1 Als primäre Discovery
  - [ ] 8.4.2 CLI `--use-arp`/`--use-ndp`
  - [ ] 8.4.3 Kombination mit ICMP
  - [ ] 8.4.4 TUI: Discovery-Methode anzeigen

**Dateien zu erstellen/ändern**:
- `netscan/discovery.py` (NEU)
- `netscan/scanner.py` (Integration)
- `netscan/tui.py` (Discovery-Anzeige)
- `tests/test_discovery.py` (NEU)

---

### Task 9: Historische Daten & Änderungsverfolgung
**Status**: ⬜ Nicht gestartet | **Priorität**: P3 | **Geschätzt**: 10-14 Tage

- [ ] **9.1 Datenbank-Schema**
  - [ ] 9.1.1 SQLite in `~/.netscan/history.db`
  - [ ] 9.1.2 Schema: Scans, Hosts, Ports, Changes
  - [ ] 9.1.3 Indizes
  - [ ] 9.1.4 Auto-Cleanup

- [ ] **9.2 Scan-Historie**
  - [ ] 9.2.1 Scan mit Timestamp speichern
  - [ ] 9.2.2 Host-Status-Historie
  - [ ] 9.2.3 Port-Änderungen tracken
  - [ ] 9.2.4 Hostname/MAC-Änderungen

- [ ] **9.3 Diff-Engine**
  - [ ] 9.3.1 Scan-Vergleich
  - [ ] 9.3.2 Change-Detection
  - [ ] 9.3.3 Kategorien: New, Changed, Disappeared
  - [ ] 9.3.4 Confidence-Score

- [ ] **9.4 TUI-Integration**
  - [ ] 9.4.1 History-View mit Timeline
  - [ ] 9.4.2 Hotkey `h`
  - [ ] 9.4.3 Up/Down-Phasen-Grafik
  - [ ] 9.4.4 Change-Highlighting

- [ ] **9.5 CLI-Tools**
  - [ ] 9.5.1 `netscan-history --list`
  - [ ] 9.5.2 `netscan-history --diff <id1> <id2>`
  - [ ] 9.5.3 `netscan-history --export`
  - [ ] 9.5.4 `netscan-history --cleanup`

- [ ] **9.6 Visualisierungen**
  - [ ] 9.6.1 ASCII-Uptime-Statistiken
  - [ ] 9.6.2 Aktivitäts-Heatmap
  - [ ] 9.6.3 HTML-Report mit Charts

**Dateien zu erstellen/ändern**:
- `netscan/history.py` (NEU)
- `netscan/database.py` (NEU)
- `netscan/diff.py` (NEU)
- `netscan/tui.py` (History-View)
- `scripts/netscan-history` (NEU)
- `~/.netscan/history.db` (Datenbank)
- `tests/test_history.py` (NEU)

---

## 📈 Statistiken

### Task-Übersicht nach Priorität
- **P0 (Kritisch)**: Task 10 (TUI Settings) - 31 Subtasks
- **P0 (High)**: Task 1 (Export), Task 3 (Profile) - 19 Subtasks
- **P1 (Medium)**: Task 2 (Rate-Limits) - 9 Subtasks
- **P2 (Nice-to-have)**: Task 4-9 - 41 Subtasks

### Gesamt-Übersicht
- **Total Tasks**: 9 Haupt-Tasks
- **Total Subtasks**: 69 detaillierte Subtasks
- **Abgeschlossen**: 0/69 (0%)
- **In Arbeit**: 0/69 (0%)
- **Geplant**: 69/69 (100%)

### Nach Phase
- **Phase 1**: 14 Tasks (Quick Wins)
- **Phase 2**: 23 Tasks (Core Features)
- **Phase 3**: 32 Tasks (Advanced Features)

### Geschätzte Gesamtzeit
- **Minimum**: 42 Tage (6 Wochen)
- **Maximum**: 84 Tage (12 Wochen)
- **Realistisch**: 63 Tage (9 Wochen)

---

## 🎯 Nächste Aktionen

### Sofort:
1. [ ] Review des Roadmaps
2. [ ] GitHub Issues für Phase 1 erstellen
3. [ ] Feature-Branch für Task 1.1 erstellen

### Diese Woche:
- [ ] Task 1.1 (CSV-Export) starten
- [ ] Tests für Export-System schreiben
- [ ] Dokumentation für Export-Formate

### Dieser Monat:
- [ ] Phase 1 abschließen (Export, Rate-Limits, Profile)
- [ ] v0.2.0 Release vorbereiten

---

## 📝 Notizen

### Dependencies zu evaluieren:
- `pyyaml` für Config-Files (optional)
- `scapy` für Raw Packets (optional, Fallback)
- `jinja2` für HTML-Templates (optional)

### Zu berücksichtigen:
- Minimale Dependencies bevorzugen
- Pure-Python wo möglich
- Fallbacks für alle optionalen Features
- Backward-Compatibility

---

**Zuletzt bearbeitet**: 6. Oktober 2025, 18:45 Uhr  
**Bearbeitet von**: GitHub Copilot Agent  
**Branch**: v0.1.1
