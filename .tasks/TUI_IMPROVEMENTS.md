# TUI Improvements Documentation

## ✨ Neue Features (Oktober 2025)

### 1. Auto-Start beim TUI-Start
**Was:** Der Netzwerk-Scan startet automatisch beim Start des TUI, ohne dass der Benutzer 's' drücken muss.

**Vorteil:** 
- Sofortiger Start der Analyse
- Keine zusätzliche Interaktion nötig
- Bessere User Experience

**Technische Details:**
- Implementiert in `draw()` Methode
- Flag `auto_scan_started` verhindert mehrfache Starts
- Threading für non-blocking Scan

---

### 2. Host-Fortschrittsanzeige
**Was:** Zeigt den aktuell gescannten Host in Echtzeit an.

**Anzeige:**
```
Scan results (scanning 192.168.1.42)  hosts=254
```

**Vorteil:**
- Transparenz über Scan-Fortschritt
- Sichtbarkeit welcher Host gerade analysiert wird
- Besseres Gefühl für Scan-Geschwindigkeit

**Technische Details:**
- Variable `scan_current_host` speichert aktuellen Host
- Wird in `_scan()` für jedes Scan-Ergebnis aktualisiert
- Status-Zeile zeigt Host dynamisch an

---

### 3. Port-Scan-Fortschritt
**Was:** Zeigt aktuellen Port während des Port-Scans an.

**Anzeige im Details-Panel:**
```
│ ⟳ Scanning port 5432/10000...
```

**Vorteil:**
- Sichtbarkeit über Port-Scan-Fortschritt
- Indikator dass Scan noch läuft (nicht eingefroren)
- Schätzung wie lange Scan noch dauert

**Technische Details:**
- Variable `portscan_current_port` speichert aktuellen Port
- Wird in `_portscan_worker()` aktualisiert
- Details-Panel zeigt Port-Nummer dynamisch

---

### 4. Port-Caching ⭐ **Wichtigste Verbesserung**
**Was:** Port-Scan-Ergebnisse werden pro IP gecacht und nicht neu gescannt.

**Anzeige:**
```
│ ✓ Cached results
```

**Vorteil:**
- **Massive Zeitersparnis** - kein erneuter 10.000-Port-Scan
- Sofortige Anzeige beim Zurückkehren zu einem Host
- Reduzierte Netzwerk-Last
- Bessere Performance und UX

**Technische Details:**
```python
self.portscan_cache: dict[str, List[int]] = {}

# In _portscan_worker():
if ip in self.portscan_cache:
    self.portscan_open = self.portscan_cache[ip]
    return  # Skip scan, use cache

# Nach erfolgreichem Scan:
self.portscan_cache[ip] = openp
```

**Cache-Verhalten:**
- Cache bleibt während der gesamten TUI-Session aktiv
- Cache wird beim Neustart geleert (nicht persistent)
- Kann mit 'p' oder Enter explizit neu gescannt werden

---

## 🎯 Verwendung

### Automatischer Start
1. TUI starten: `python3 -m netscan.tui`
2. Scan startet **automatisch** - keine Aktion nötig!
3. Fortschritt wird live angezeigt

### Host-Navigation mit Cache
1. Host mit ↑/↓ auswählen
2. Port-Scan startet automatisch (nur beim **ersten Mal**)
3. Zu anderem Host navigieren
4. Zurück zum ersten Host → **Ports sofort verfügbar!** ✓

### Manueller Neu-Scan (Cache überschreiben)
- **'p' Taste**: Port-Scan für aktuellen Host neu starten
- **Enter**: Port-Scan neu starten
- Beide überschreiben Cache mit neuen Ergebnissen

---

## 📊 Performance-Vergleich

### Ohne Caching (vorher):
```
Host A auswählen → 10-30s Port-Scan
Host B auswählen → 10-30s Port-Scan
Host A wieder    → 10-30s Port-Scan (erneut!)
```
**Total: 30-90 Sekunden für 3 Interaktionen**

### Mit Caching (jetzt):
```
Host A auswählen → 10-30s Port-Scan (erstmalig)
Host B auswählen → 10-30s Port-Scan (erstmalig)
Host A wieder    → <100ms (aus Cache!) ✨
```
**Total: 20-60 Sekunden + instant bei Re-Select**

---

## 🔧 Code-Änderungen

### Neue Variablen in `__init__`:
```python
self.portscan_cache: dict[str, List[int]] = {}
self.portscan_current_port: Optional[int] = None
self.scan_current_host: Optional[str] = None
```

### Geänderte Methoden:
1. **`_scan()`** - Update `scan_current_host` für Fortschrittsanzeige
2. **`_portscan_worker()`** - Cache-Check vor Scan, Cache-Speichern nach Scan
3. **`draw()`** - Status-Zeilen für Fortschrittsanzeigen erweitert

### Zeilen-Änderungen:
- `netscan/tui.py`: +36 Zeilen, -3 Zeilen
- Keine Breaking Changes
- Vollständig rückwärtskompatibel

---

## 💡 Zukünftige Erweiterungen

### Mögliche Verbesserungen:
1. **Persistenter Cache** - Cache in Datei speichern zwischen Sessions
2. **Cache-TTL** - Automatisches Verfallen nach X Minuten
3. **Cache-Management** - UI zum Leeren des Caches ('C' Taste?)
4. **Cache-Statistiken** - Anzeige wie viele Hosts gecacht sind
5. **Selective Re-Scan** - Nur bestimmte Port-Ranges neu scannen

---

## 🐛 Bekannte Limitationen

1. **Cache nicht persistent** - Wird beim TUI-Neustart geleert
2. **Keine TTL** - Cache veraltet nie automatisch
3. **Kein Memory-Limit** - Bei sehr großen Netzwerken (>1000 Hosts) könnte Cache groß werden
4. **Port-Fortschritt zu schnell** - Bei fast concurrent scan (256 threads) ist Fortschritt schwer zu sehen

---

## 📝 Changelog

**2025-10-06** - Phase 2: Persistent Cache & Management ✨
- ✅ Persistent cache storage (~/.netscan_cache.json)
- ✅ Cache TTL (1 hour default, configurable)
- ✅ Cache age display (5s, 3m, 2h ago)
- ✅ Cache management UI (Shift+C to clear)
- ✅ Cache statistics in title bar (cache=15)
- ✅ Automatic expired cache cleanup on refresh
- ✅ Save cache on quit

**2025-10-06** - Phase 1: Initial Implementation
- ✅ Auto-Start beim TUI-Start
- ✅ Host-Fortschrittsanzeige
- ✅ Port-Scan-Fortschritt
- ✅ Port-Caching System

---

## 🎯 Phase 2 Details: Persistent Cache

### Cache File Location
```
~/.netscan_cache.json
```

### Cache Format
```json
{
  "192.168.1.1": [[22, 80, 443], 1696615200.0],
  "192.168.1.2": [[22, 3389], 1696615300.0]
}
```
- Format: `ip -> [ports_list, unix_timestamp]`
- Human-readable JSON
- Easy to inspect/edit manually

### TTL Configuration
Default: **1 hour (3600 seconds)**

Customize in `netscan/tui.py`:
```python
self.cache_ttl = 3600  # Change this value
```

Common values:
- `300` = 5 minutes (testing)
- `1800` = 30 minutes
- `3600` = 1 hour (default)
- `86400` = 24 hours

### Cache Lifecycle
1. **On Start**: Load from disk, filter expired
2. **On Scan**: Check cache, scan if expired/missing
3. **On Quit**: Save all non-expired entries
4. **On Refresh ('r')**: Clear expired entries
5. **On Clear ('C')**: Delete all entries

### New UI Elements

**Title Bar:**
```
cache=15  ← Shows cached IP count
```

**Cache Age:**
```
│ ✓ Cached (5s ago)
│ ✓ Cached (3m ago)
│ ✓ Cached (2h ago)
```

**Clear Message:**
```
✓ Cleared 15 cached entries
```

### New Hotkeys
- **Shift+C**: Clear entire cache
- **r**: Refresh + cleanup expired
- **q**: Auto-save before quit

