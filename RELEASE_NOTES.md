# Release Notes - Network Scanner

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
