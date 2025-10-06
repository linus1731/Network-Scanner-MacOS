# Task 10: TUI Settings Panel & Feature Integration

## Übersicht
**Priorität**: P0 (Kritisch für Usability)  
**Komplexität**: Mittel-Hoch  
**Geschätzte Zeit**: 5-7 Tage  
**Status**: ⬜ Nicht gestartet

## Ziel
Alle Features über die TUI zugänglich machen und ein umfassendes Settings-Panel für Programmkonfiguration erstellen.

---

## 📋 Subtasks

### Task 10.1: Settings-Panel-Framework
**Status**: ⬜ | **Geschätzt**: 2-3 Tage

- [ ] **10.1.1 Settings-Datenstruktur**
  - [ ] Settings-Klasse mit allen konfigurierbaren Parametern
  - [ ] Default-Werte definieren
  - [ ] Validierung für jeden Setting-Typ
  - [ ] Persistence in `~/.netscan/config.yaml`
  - [ ] Auto-Load beim Start
  - [ ] Auto-Save bei Änderungen

- [ ] **10.1.2 Settings-Panel-UI**
  - [ ] Neues Overlay-Window für Settings
  - [ ] Hotkey `Ctrl+S` oder `F2` für Settings-Panel
  - [ ] Kategorien-Navigation (links: Kategorien, rechts: Einstellungen)
  - [ ] Kategorien:
    - General (Interface, Theme, Sprache)
    - Scanning (Concurrency, Timeouts, Retries)
    - Port Scanning (Port-Range, Timeout, Services)
    - Network (Rate-Limits, Interface-Selection)
    - Display (Colors, Layout, Auto-Updates)
    - Export (Default-Format, Auto-Export)
    - Advanced (Debug, Logging, Cache)
  - [ ] Scroll-Support für lange Listen
  - [ ] Visuelles Feedback bei Änderungen

- [ ] **10.1.3 Input-Widgets**
  - [ ] Text-Input (für Pfade, IPs, etc.)
  - [ ] Number-Input mit +/- Buttons
  - [ ] Toggle-Switch (ON/OFF)
  - [ ] Dropdown-Menü (für Enums)
  - [ ] Color-Picker (für Theme-Anpassung)
  - [ ] Slider (für Bereiche wie 1-1000)
  - [ ] Multi-Select (für z.B. Protokolle)

- [ ] **10.1.4 Hotkeys im Settings-Panel**
  - [ ] `↑`/`↓`: Navigation durch Optionen
  - [ ] `←`/`→`: Kategorie-Wechsel
  - [ ] `Tab`: Zwischen Kategorien und Einstellungen
  - [ ] `Enter`: Einstellung bearbeiten
  - [ ] `Space`: Toggle bei ON/OFF
  - [ ] `Esc`: Zurück ohne Speichern
  - [ ] `Ctrl+S`: Speichern und Zurück
  - [ ] `Ctrl+R`: Reset zu Defaults

**Dateien**:
- `netscan/settings.py` (NEU)
- `netscan/tui_settings.py` (NEU)
- `netscan/widgets.py` (NEU)
- `~/.netscan/config.yaml` (Config-File)

---

### Task 10.2: Feature-Integration in TUI
**Status**: ⬜ | **Geschätzt**: 3-4 Tage

#### 10.2.1 Export-Integration
- [ ] **Export-Menü im TUI**
  - [ ] Hotkey `e` für Export-Overlay
  - [ ] Format-Auswahl mit Radio-Buttons (CSV, JSON, MD, HTML)
  - [ ] Dateiname-Input mit File-Browser
  - [ ] Filter-Optionen (All Hosts / Only UP / Selected)
  - [ ] Include-Options (Ports, Services, Banners)
  - [ ] Live-Vorschau der ersten 5 Zeilen
  - [ ] Export-Progress-Bar
  - [ ] Erfolgs-/Fehler-Meldung mit Dateipfad
  - [ ] Quick-Export mit Default-Settings (Shift+E)

#### 10.2.2 Profile-Integration
- [ ] **Profile-Menü**
  - [ ] Hotkey `p` für Profile-Auswahl
  - [ ] Liste aller Profile mit Beschreibung
  - [ ] Visual Indicator für aktives Profil
  - [ ] Hotkey `Shift+P` für Quick-Profile-Switch
  - [ ] Profile-Parameter-Vorschau
  - [ ] Profile bearbeiten (öffnet Settings-Panel)
  - [ ] Neues Profil erstellen
  - [ ] Profil löschen (mit Confirmation)

#### 10.2.3 Scan-Optionen-Dialog
- [ ] **Advanced Scan Options**
  - [ ] Hotkey `Ctrl+N` für "New Scan with Options"
  - [ ] CIDR/IP-Range-Input
  - [ ] Profile-Auswahl
  - [ ] Concurrency-Slider (1-512)
  - [ ] Timeout-Input (0.1-10.0 Sek)
  - [ ] Port-Range-Input (Start-End)
  - [ ] Additional Options:
    - [ ] TCP-Fallback (Toggle)
    - [ ] Grab Banners (Toggle)
    - [ ] mDNS Discovery (Toggle)
    - [ ] ARP/NDP Scan (Toggle)
    - [ ] IPv6 Support (Toggle)
  - [ ] "Start Scan" Button
  - [ ] "Save as Profile" Option

#### 10.2.4 Rate-Limit-Control
- [ ] **Rate-Limit-Overlay**
  - [ ] Hotkey `Ctrl+L` für Rate-Limit-Panel
  - [ ] Live-Anzeige: Current Rate (Pakete/Sek)
  - [ ] Slider für Rate-Limit (1-1000 pps)
  - [ ] Burst-Size-Input
  - [ ] Echtzeit-Graph der tatsächlichen Rate
  - [ ] "Apply" ohne Scan-Neustart
  - [ ] Preset-Buttons (Slow, Normal, Fast, Unlimited)

#### 10.2.5 History-Browser
- [ ] **History-View**
  - [ ] Hotkey `h` für History-Panel
  - [ ] Timeline-Ansicht aller Scans
  - [ ] Scan-Details (Timestamp, Duration, Hosts-Found)
  - [ ] Diff-View zwischen zwei Scans (Dropdown)
  - [ ] Changes-Highlighting:
    - [ ] New Hosts (grün)
    - [ ] Disappeared Hosts (rot)
    - [ ] Changed Status (gelb)
    - [ ] Port Changes (cyan)
  - [ ] Export-History-Scan
  - [ ] Load-History-Scan (in aktueller View)
  - [ ] Delete-Scan (mit Confirmation)

#### 10.2.6 Banner-Info-Panel
- [ ] **Banner-Details**
  - [ ] Automatische Anzeige wenn verfügbar
  - [ ] Sektion "Service Information" im Host-Details-Panel
  - [ ] Per-Port-Banner-Anzeige:
    - [ ] Port-Nummer + Service-Name
    - [ ] Banner-Text (erste 200 Zeichen)
    - [ ] Detected Version
    - [ ] OS-Fingerprint (falls erkannt)
    - [ ] CVE-Links (optional, wenn Keywords gefunden)
  - [ ] Hotkey `b` für vollständigen Banner-Text
  - [ ] Copy-to-Clipboard-Funktion (Ctrl+C)

#### 10.2.7 mDNS-Services-Panel
- [ ] **mDNS-Discovery-View**
  - [ ] Hotkey `m` für mDNS-Overlay
  - [ ] Liste aller entdeckten mDNS-Services
  - [ ] Service-Typen gruppiert:
    - [ ] HTTP (_http._tcp)
    - [ ] SSH (_ssh._tcp)
    - [ ] Printer (_ipp._tcp)
    - [ ] Airplay (_airplay._tcp)
    - [ ] etc.
  - [ ] TXT-Records-Anzeige
  - [ ] Service-Filter
  - [ ] "Scan for Services" Button

#### 10.2.8 Network-Interface-Selector
- [ ] **Interface-Auswahl**
  - [ ] Hotkey `i` für Interface-Auswahl
  - [ ] Liste aller Netzwerk-Interfaces
  - [ ] Status: UP/DOWN
  - [ ] IP-Adresse(n) anzeigen
  - [ ] Link-Speed anzeigen
  - [ ] Auto-CIDR-Berechnung für gewähltes Interface
  - [ ] "Scan this Network" Quick-Action

---

### Task 10.3: Main Menu / Quick Actions
**Status**: ⬜ | **Geschätzt**: 1 Tag

- [ ] **10.3.1 Main Menu**
  - [ ] Hotkey `F1` oder `Ctrl+M` für Main-Menu
  - [ ] Menü-Struktur:
    ```
    ┌─ NETSCAN MAIN MENU ─────────┐
    │                              │
    │  [S] Start New Scan          │
    │  [E] Export Results          │
    │  [P] Change Profile          │
    │  [H] View History            │
    │  [I] Select Interface        │
    │  [M] mDNS Discovery          │
    │  [L] Rate Limit Settings     │
    │  [⚙] Settings (Ctrl+S)      │
    │  [?] Help                    │
    │  [Q] Quit                    │
    │                              │
    └──────────────────────────────┘
    ```
  - [ ] Keyboard-Navigation
  - [ ] Mouse-Support (optional)

- [ ] **10.3.2 Quick Actions Bar**
  - [ ] Untere Statusleiste mit Quick-Actions
  - [ ] Immer sichtbare Shortcuts:
    ```
    [F1]Help  [F2]Settings  [F3]Export  [F4]Profile  [F5]Refresh  [F10]Quit
    ```
  - [ ] Context-sensitive Actions (ändern sich je nach View)

- [ ] **10.3.3 Help-Overlay**
  - [ ] Hotkey `F1` oder `?` für Help
  - [ ] Scrollbare Liste aller Hotkeys
  - [ ] Kategorisiert nach Funktion
  - [ ] Suchfunktion (Ctrl+F)
  - [ ] "Show Tips" Option für Anfänger

---

### Task 10.4: Settings-Kategorien im Detail
**Status**: ⬜ | **Geschätzt**: 1 Tag

#### 10.4.1 General Settings
```yaml
general:
  theme: "dark"              # dark, light, auto
  language: "en"             # en, de
  auto_refresh: true
  refresh_interval: 5        # seconds
  confirm_quit: true
  save_window_size: true
  start_fullscreen: false
```

#### 10.4.2 Scanning Settings
```yaml
scanning:
  concurrency: 128
  timeout: 1.0               # seconds
  retry_count: 1
  tcp_fallback: true
  icmp_count: 1
  auto_scan_on_start: true
  scan_on_interface_change: true
```

#### 10.4.3 Port Scanning Settings
```yaml
port_scanning:
  enabled: true
  port_range_start: 1
  port_range_end: 10000
  concurrency: 256
  timeout: 0.5               # seconds
  auto_scan_on_select: true
  scan_common_ports_first: true
  grab_banners: false
```

#### 10.4.4 Network Settings
```yaml
network:
  rate_limit_enabled: false
  rate_limit_pps: 100        # packets per second
  burst_size: 50
  preferred_interface: "auto"
  enable_ipv6: false
  enable_mdns: false
  enable_arp_discovery: false
```

#### 10.4.5 Display Settings
```yaml
display:
  show_down_hosts: true      # ALL vs UP filter default
  color_scheme: "default"
  show_traffic_graph: true
  graph_history_seconds: 300
  table_font_size: "normal"  # small, normal, large
  panel_width_percent: 35    # 20-50%
  auto_scroll_to_new: true
```

#### 10.4.6 Export Settings
```yaml
export:
  default_format: "csv"
  auto_timestamp: true
  include_down_hosts: false
  include_port_details: true
  default_export_dir: "~/Documents/netscan-exports"
  auto_export_on_scan: false
```

#### 10.4.7 Advanced Settings
```yaml
advanced:
  debug_mode: false
  log_level: "info"          # debug, info, warn, error
  log_file: "~/.netscan/netscan.log"
  cache_enabled: true
  cache_ttl: 3600            # seconds
  max_history_scans: 100
  database_auto_cleanup: true
```

---

### Task 10.5: Keyboard-Navigation-System
**Status**: ⬜ | **Geschätzt**: 1 Tag

- [ ] **10.5.1 Global Hotkeys** (funktionieren immer)
  ```
  F1 / ?          Help
  F2 / Ctrl+S     Settings
  F3 / e          Export
  F4 / p          Profiles
  F5              Refresh
  F10 / q         Quit
  Ctrl+N          New Scan
  Ctrl+L          Rate Limits
  h               History
  m               mDNS
  i               Interface
  ```

- [ ] **10.5.2 Context-Specific Hotkeys**
  ```
  Main View:
    ↑/↓           Navigate hosts
    Enter         Rescan ports
    s             Start scan
    a             Toggle ALL/UP filter
    1-5           Sort columns
    o/O           Sort order
  
  Overlay/Dialog:
    Esc           Close/Cancel
    Enter         Confirm/Apply
    Tab           Next field
    Shift+Tab     Previous field
  ```

- [ ] **10.5.3 Hotkey-Hilfe**
  - [ ] Overlay zeigt verfügbare Hotkeys
  - [ ] Context-sensitive Hilfe
  - [ ] Hotkey-Cheatsheet als PDF-Export

---

### Task 10.6: Theme-System
**Status**: ⬜ | **Geschätzt**: 1 Tag (Optional)

- [ ] **10.6.1 Color-Themes**
  - [ ] Dark Theme (default)
  - [ ] Light Theme
  - [ ] High Contrast
  - [ ] Solarized Dark/Light
  - [ ] Custom Theme (über Settings definierbar)

- [ ] **10.6.2 Theme-Configuration**
  ```yaml
  themes:
    dark:
      background: "black"
      foreground: "white"
      ip_color: "cyan"
      up_color: "green"
      down_color: "red"
      accent_color: "yellow"
      graph_rx_color: "magenta"
      graph_tx_color: "blue"
      panel_border: "white"
  ```

- [ ] **10.6.3 Theme-Switcher**
  - [ ] In Settings-Panel unter Display
  - [ ] Live-Preview
  - [ ] Quick-Switch mit Hotkey `Ctrl+T`

---

## 📂 Dateien-Übersicht

### Neu zu erstellen:
```
netscan/
├── settings.py             # Settings-Management
├── tui_settings.py         # Settings-Panel UI
├── widgets.py              # Input-Widgets
├── tui_export.py           # Export-Dialog
├── tui_profile.py          # Profile-Menu
├── tui_history.py          # History-Browser
├── tui_menu.py             # Main-Menu
├── tui_help.py             # Help-Overlay
├── themes.py               # Theme-System
└── config_manager.py       # Config-File-Handler

~/.netscan/
├── config.yaml             # User-Settings
├── themes/                 # Custom-Themes
│   └── custom.yaml
└── profiles/               # Custom-Profiles
    ├── quick.yaml
    └── custom.yaml
```

### Zu ändern:
```
netscan/
├── tui.py                  # Hotkey-Integration, Overlay-System
└── cli.py                  # Settings-Respekt
```

---

## 🎯 Implementierungs-Reihenfolge

### Woche 1: Framework
1. Settings-System (`settings.py`, `config_manager.py`)
2. Widget-System (`widgets.py`)
3. Settings-Panel-UI (`tui_settings.py`)
4. Basic Hotkey-Integration

### Woche 2: Feature-Integration
5. Export-Dialog (`tui_export.py`)
6. Profile-Menu (`tui_profile.py`)
7. Main-Menu (`tui_menu.py`)
8. Help-Overlay (`tui_help.py`)

### Woche 3: Advanced Features
9. History-Browser (nach Task 9)
10. Rate-Limit-Control
11. Theme-System (optional)
12. Polish & Testing

---

## ✅ Akzeptanzkriterien

- [ ] Alle Features über TUI zugänglich
- [ ] Settings persistent gespeichert
- [ ] Alle Hotkeys dokumentiert und funktional
- [ ] Intuitive Navigation
- [ ] Keine Abstürze bei fehlerhaften Inputs
- [ ] Settings validiert vor dem Speichern
- [ ] Help-System vollständig
- [ ] Responsive UI bei allen Terminal-Größen

---

## 🧪 Test-Plan

### Unit-Tests:
- Settings-Validierung
- Config-File-Parsing
- Widget-Funktionalität

### Integration-Tests:
- Settings ↔ Scanner
- Profile ↔ Scan-Optionen
- Export ↔ Aktueller-State

### UI-Tests:
- Alle Hotkeys funktionieren
- Navigation flüssig
- Overlays korrekt gerendert
- Keine Memory-Leaks bei vielen Overlays

### User-Acceptance-Tests:
- Kann Benutzer ohne Doku navigieren?
- Settings intuitiv?
- Help hilfreich?

---

## 📝 Notizen

### Technische Entscheidungen:
- **Config-Format**: YAML (lesbar, kommentierbar)
- **Settings-Speicher**: `~/.netscan/config.yaml`
- **Widget-Framework**: Custom (kein external lib)
- **Overlay-System**: Curses-Windows-Stack

### Zu beachten:
- Settings-Änderungen sollten live anwendbar sein (kein Neustart)
- Validation wichtig (falsche Settings = Crash)
- Defaults müssen sinnvoll sein
- Hotkeys dürfen sich nicht überschneiden

---

**Erstellt**: 6. Oktober 2025  
**Priorität**: P0 (vor Phase 2)  
**Abhängigkeiten**: Keine (kann parallel zu anderen Tasks)
