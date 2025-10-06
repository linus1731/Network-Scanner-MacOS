# Task 10 Quick Start Guide 🚀

## Warum Task 10 zuerst?

**Task 10 ist das FUNDAMENT für alles Weitere!**

Ohne Task 10:
- ❌ Features nur über CLI nutzbar
- ❌ Jede neue Funktion braucht CLI-Option
- ❌ Keine persistenten Einstellungen
- ❌ Keine intuitive Bedienung

Mit Task 10:
- ✅ Alle Features über TUI erreichbar (F1-F10 Hotkeys)
- ✅ Settings persistent in `~/.netscan/config.yaml`
- ✅ Export-Dialog mit Live-Vorschau
- ✅ Profile-Manager direkt in TUI
- ✅ Rate-Limits on-the-fly änderbar
- ✅ Vollständige Dokumentation via Help-Overlay
- ✅ **Kein Terminal-Wissen mehr nötig!**

---

## 🗓️ Implementierungs-Plan (2 Wochen)

### Woche 1: Settings-Framework ⚙️

#### Tag 1-2: Config & Settings
```bash
# 1. Settings-Datenmodell
touch netscan/settings.py
```

**`netscan/settings.py`**:
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ScanSettings:
    concurrency: int = 128
    timeout: float = 1.0
    retry_count: int = 1
    tcp_fallback: bool = True

@dataclass
class PortScanSettings:
    enabled: bool = True
    port_range_start: int = 1
    port_range_end: int = 10000
    concurrency: int = 256
    timeout: float = 0.5
    auto_scan_on_select: bool = True
    grab_banners: bool = False

@dataclass
class DisplaySettings:
    show_down_hosts: bool = True
    color_scheme: str = "default"
    panel_width_percent: int = 35
    auto_scroll_to_new: bool = True

@dataclass
class Settings:
    scan: ScanSettings = field(default_factory=ScanSettings)
    port_scan: PortScanSettings = field(default_factory=PortScanSettings)
    display: DisplaySettings = field(default_factory=DisplaySettings)
    
    @classmethod
    def load(cls, path: str = "~/.netscan/config.yaml") -> "Settings":
        """Load settings from YAML file"""
        pass  # TODO: Implement
    
    def save(self, path: str = "~/.netscan/config.yaml") -> None:
        """Save settings to YAML file"""
        pass  # TODO: Implement
```

```bash
# 2. Config-Manager
touch netscan/config_manager.py
```

**Test**:
```bash
python3 -c "from netscan.settings import Settings; s = Settings(); print(s)"
```

---

#### Tag 3-4: Widget-System
```bash
touch netscan/widgets.py
```

**`netscan/widgets.py`** - Wichtigste Widgets:

```python
import curses

class Widget:
    """Base widget class"""
    def __init__(self, y: int, x: int, width: int):
        self.y = y
        self.x = x
        self.width = width
        self.focused = False
    
    def render(self, win) -> None:
        raise NotImplementedError
    
    def handle_key(self, key: int) -> bool:
        """Return True if key was handled"""
        raise NotImplementedError

class Toggle(Widget):
    """ON/OFF Toggle Switch"""
    def __init__(self, y: int, x: int, label: str, value: bool = False):
        super().__init__(y, x, 40)
        self.label = label
        self.value = value
    
    def render(self, win) -> None:
        status = "ON " if self.value else "OFF"
        color = curses.color_pair(2 if self.value else 1)
        win.addstr(self.y, self.x, f"{self.label}: ", curses.A_BOLD if self.focused else 0)
        win.addstr(f"[{status}]", color)
    
    def handle_key(self, key: int) -> bool:
        if key in (ord(' '), ord('\n'), curses.KEY_ENTER):
            self.value = not self.value
            return True
        return False

class NumberInput(Widget):
    """Number input with +/- buttons"""
    def __init__(self, y: int, x: int, label: str, value: int, min_val: int, max_val: int):
        super().__init__(y, x, 50)
        self.label = label
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
    
    def render(self, win) -> None:
        win.addstr(self.y, self.x, f"{self.label}: ", curses.A_BOLD if self.focused else 0)
        win.addstr(f"[-] {self.value:4d} [+]")
    
    def handle_key(self, key: int) -> bool:
        if key in (ord('-'), curses.KEY_LEFT):
            self.value = max(self.min_val, self.value - 1)
            return True
        elif key in (ord('+'), ord('='), curses.KEY_RIGHT):
            self.value = min(self.max_val, self.value + 1)
            return True
        return False

class Dropdown(Widget):
    """Dropdown menu"""
    def __init__(self, y: int, x: int, label: str, options: list, selected: int = 0):
        super().__init__(y, x, 50)
        self.label = label
        self.options = options
        self.selected = selected
        self.expanded = False
    
    def render(self, win) -> None:
        win.addstr(self.y, self.x, f"{self.label}: ", curses.A_BOLD if self.focused else 0)
        win.addstr(f"[{self.options[self.selected]}] ▼")
        
        if self.expanded:
            for i, opt in enumerate(self.options):
                style = curses.A_REVERSE if i == self.selected else 0
                win.addstr(self.y + 1 + i, self.x + len(self.label) + 2, f"  {opt}", style)
    
    def handle_key(self, key: int) -> bool:
        if key in (ord('\n'), curses.KEY_ENTER, ord(' ')):
            self.expanded = not self.expanded
            return True
        elif self.expanded:
            if key in (curses.KEY_UP, ord('k')):
                self.selected = (self.selected - 1) % len(self.options)
                return True
            elif key in (curses.KEY_DOWN, ord('j')):
                self.selected = (self.selected + 1) % len(self.options)
                return True
        return False
```

**Test**:
```bash
# Create test script
cat > test_widgets.py << 'EOF'
import curses
from netscan.widgets import Toggle, NumberInput, Dropdown

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    
    widgets = [
        Toggle(2, 5, "Auto Refresh", True),
        NumberInput(4, 5, "Concurrency", 128, 1, 512),
        Dropdown(6, 5, "Theme", ["dark", "light", "solarized"], 0)
    ]
    
    current = 0
    widgets[current].focused = True
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 5, "Widget Test (q to quit, Tab to switch)", curses.A_BOLD)
        
        for w in widgets:
            w.render(stdscr)
        
        stdscr.refresh()
        key = stdscr.getch()
        
        if key == ord('q'):
            break
        elif key == ord('\t'):
            widgets[current].focused = False
            current = (current + 1) % len(widgets)
            widgets[current].focused = True
        else:
            widgets[current].handle_key(key)

curses.wrapper(main)
EOF

python3 test_widgets.py
```

---

#### Tag 5-7: Settings-Panel
```bash
touch netscan/tui_settings.py
```

**`netscan/tui_settings.py`** - Settings-Overlay:

```python
import curses
from typing import List
from netscan.widgets import Widget, Toggle, NumberInput, Dropdown
from netscan.settings import Settings

class SettingsPanel:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.categories = [
            "General",
            "Scanning",
            "Port Scanning",
            "Network",
            "Display",
            "Export",
            "Advanced"
        ]
        self.current_category = 0
        self.widgets: List[Widget] = []
        self.current_widget = 0
        self._build_widgets()
    
    def _build_widgets(self) -> None:
        """Build widgets for current category"""
        self.widgets = []
        cat = self.categories[self.current_category]
        
        if cat == "Scanning":
            self.widgets = [
                NumberInput(5, 10, "Concurrency", self.settings.scan.concurrency, 1, 512),
                NumberInput(7, 10, "Timeout (sec)", int(self.settings.scan.timeout), 1, 10),
                NumberInput(9, 10, "Retry Count", self.settings.scan.retry_count, 0, 5),
                Toggle(11, 10, "TCP Fallback", self.settings.scan.tcp_fallback),
            ]
        elif cat == "Port Scanning":
            self.widgets = [
                Toggle(5, 10, "Enable Port Scanning", self.settings.port_scan.enabled),
                NumberInput(7, 10, "Port Range Start", self.settings.port_scan.port_range_start, 1, 65535),
                NumberInput(9, 10, "Port Range End", self.settings.port_scan.port_range_end, 1, 65535),
                NumberInput(11, 10, "Concurrency", self.settings.port_scan.concurrency, 1, 1024),
                Toggle(13, 10, "Auto-scan on select", self.settings.port_scan.auto_scan_on_select),
            ]
        # ... mehr Kategorien
        
        if self.widgets:
            self.widgets[0].focused = True
    
    def render(self, stdscr) -> None:
        """Render settings panel as overlay"""
        h, w = stdscr.getmaxyx()
        
        # Create overlay window (80% of screen)
        overlay_h = int(h * 0.8)
        overlay_w = int(w * 0.8)
        start_y = (h - overlay_h) // 2
        start_x = (w - overlay_w) // 2
        
        win = curses.newwin(overlay_h, overlay_w, start_y, start_x)
        win.box()
        
        # Title
        win.addstr(1, 2, "⚙ SETTINGS", curses.A_BOLD | curses.color_pair(3))
        win.addstr(2, 2, "─" * (overlay_w - 4))
        
        # Categories (left)
        cat_x = 3
        for i, cat in enumerate(self.categories):
            style = curses.A_REVERSE if i == self.current_category else 0
            win.addstr(4 + i * 2, cat_x, f" {cat} ", style)
        
        # Settings (right)
        win.addstr(3, 25, self.categories[self.current_category], curses.A_BOLD)
        for widget in self.widgets:
            widget.render(win)
        
        # Help
        help_y = overlay_h - 2
        win.addstr(help_y, 2, "Tab: Next | ←→: Change Category | Ctrl+S: Save | Esc: Cancel")
        
        win.noutrefresh()
        curses.doupdate()
    
    def handle_key(self, key: int) -> str:
        """Handle keyboard input. Returns action: 'save', 'cancel', or 'continue'"""
        if key == 27:  # Esc
            return 'cancel'
        elif key == 19:  # Ctrl+S
            self._apply_settings()
            return 'save'
        elif key == ord('\t'):  # Tab
            if self.widgets:
                self.widgets[self.current_widget].focused = False
                self.current_widget = (self.current_widget + 1) % len(self.widgets)
                self.widgets[self.current_widget].focused = True
        elif key in (curses.KEY_LEFT, ord('h')):
            self.current_category = (self.current_category - 1) % len(self.categories)
            self.current_widget = 0
            self._build_widgets()
        elif key in (curses.KEY_RIGHT, ord('l')):
            self.current_category = (self.current_category + 1) % len(self.categories)
            self.current_widget = 0
            self._build_widgets()
        elif self.widgets:
            self.widgets[self.current_widget].handle_key(key)
        
        return 'continue'
    
    def _apply_settings(self) -> None:
        """Apply widget values back to settings"""
        # TODO: Map widget values back to settings object
        pass
```

**Test**:
```bash
python3 -c "from netscan.tui_settings import SettingsPanel; print('Settings panel imports OK')"
```

---

### Woche 2: Feature-Integration 🔌

#### Tag 8-9: Export-Dialog
```bash
touch netscan/tui_export.py
```

**Integration in `netscan/tui.py`**:
```python
# In TUI class:
def _handle_export_menu(self) -> None:
    """Show export dialog (Hotkey: e)"""
    # TODO: Implement overlay with format selection
    pass

# In main loop:
elif key == ord('e'):
    self._handle_export_menu()
```

---

#### Tag 10-11: Main Menu & Hotkeys
```bash
touch netscan/tui_menu.py
touch netscan/tui_help.py
```

**`netscan/tui_menu.py`**:
```python
def show_main_menu(stdscr) -> str:
    """Show main menu overlay. Returns selected action."""
    menu_items = [
        ("s", "Start New Scan", "start_scan"),
        ("e", "Export Results", "export"),
        ("p", "Change Profile", "profile"),
        ("h", "View History", "history"),
        ("i", "Select Interface", "interface"),
        ("", "Settings (Ctrl+S)", "settings"),
        ("?", "Help", "help"),
        ("q", "Quit", "quit"),
    ]
    # ... render menu
```

**Integration in `tui.py`**:
```python
# Global hotkeys
HOTKEYS = {
    curses.KEY_F1: 'help',
    curses.KEY_F2: 'settings',
    curses.KEY_F3: 'export',
    curses.KEY_F4: 'profile',
    curses.KEY_F5: 'refresh',
    curses.KEY_F10: 'quit',
    ord('?'): 'help',
    19: 'settings',  # Ctrl+S
    ord('e'): 'export',
    ord('p'): 'profile',
    ord('h'): 'history',
    ord('i'): 'interface',
    ord('m'): 'mdns',
    12: 'rate_limit',  # Ctrl+L
    14: 'new_scan',  # Ctrl+N
}

# In main loop:
if key in HOTKEYS:
    action = HOTKEYS[key]
    self._dispatch_action(action)
```

---

#### Tag 12-14: Polish & Testing
- Help-Overlay fertigstellen
- Profile-Menu implementieren
- Alle Hotkeys testen
- Edge-Cases behandeln
- User-Testing

---

## 🎨 UI-Design-Beispiele

### Settings-Panel
```
┌─ SETTINGS ──────────────────────────────────────────────────────────┐
│                                                                      │
│  General             │  SCANNING                                    │
│ [Scanning]           │                                              │
│  Port Scanning       │  Concurrency:  [-] 128  [+]                 │
│  Network             │  Timeout (sec): [-]   1  [+]                 │
│  Display             │  Retry Count:   [-]   1  [+]                 │
│  Export              │  TCP Fallback:  [ON ]                        │
│  Advanced            │                                              │
│                      │                                              │
│                      │                                              │
│                      │                                              │
│ Tab: Next | ←→: Change Category | Ctrl+S: Save | Esc: Cancel       │
└──────────────────────────────────────────────────────────────────────┘
```

### Main Menu
```
┌─ NETSCAN MAIN MENU ─────────────┐
│                                  │
│  [S] Start New Scan              │
│  [E] Export Results              │
│  [P] Change Profile              │
│  [H] View History                │
│  [I] Select Interface            │
│  [M] mDNS Discovery              │
│  [L] Rate Limit Settings         │
│  [⚙] Settings (Ctrl+S)          │
│  [?] Help                        │
│  [Q] Quit                        │
│                                  │
└──────────────────────────────────┘
```

### Export Dialog
```
┌─ EXPORT RESULTS ────────────────────────────────────────────────────┐
│                                                                      │
│  Format:     ( ) CSV                                                │
│              ( ) JSON                                               │
│              (•) Markdown                                           │
│              ( ) HTML                                               │
│                                                                      │
│  Filename:   [scan_20251006_143022.md____________]                 │
│                                                                      │
│  Include:    [✓] IP Addresses                                       │
│              [✓] Hostnames                                          │
│              [✓] Open Ports                                         │
│              [✓] Service Names                                      │
│              [ ] Down Hosts                                         │
│                                                                      │
│  Preview:    │ # Network Scan Results                              │
│              │ | IP           | Status | Hostname | Ports |        │
│              │ |--------------|--------|----------|-------|        │
│              │ | 192.168.1.1  | UP     | router   | 80... |        │
│                                                                      │
│                                    [Cancel]  [Export]               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Akzeptanzkriterien (Definition of Done)

Nach 2 Wochen muss Folgendes funktionieren:

1. **Settings-System**
   - [ ] Settings werden in `~/.netscan/config.yaml` gespeichert
   - [ ] Settings beim Start automatisch geladen
   - [ ] Alle 7 Kategorien implementiert
   - [ ] Mindestens 20 konfigurierbare Parameter

2. **Hotkeys**
   - [ ] F1: Help funktioniert
   - [ ] F2/Ctrl+S: Settings-Panel öffnet
   - [ ] F3/e: Export-Dialog öffnet
   - [ ] F4/p: Profile-Menu öffnet
   - [ ] Alle globalen Hotkeys dokumentiert

3. **UI-Komponenten**
   - [ ] Settings-Panel rendert korrekt
   - [ ] Widgets reagieren auf Input
   - [ ] Main-Menu funktioniert
   - [ ] Help-Overlay zeigt alle Hotkeys

4. **Integration**
   - [ ] TUI respektiert Settings
   - [ ] Export funktioniert über Dialog
   - [ ] Profile-Wechsel möglich
   - [ ] Keine Abstürze bei fehlerhaften Inputs

5. **User Experience**
   - [ ] Navigation intuitiv (keine Doku nötig)
   - [ ] Visual Feedback bei allen Actions
   - [ ] Error-Messages hilfreich
   - [ ] Performance: Keine Lags beim Overlay-Wechsel

---

## 🚀 Los geht's!

```bash
# Starte mit dem Framework:
cd ~/Documents/Coding/Network-Scanner-MacOS
git checkout -b feature/tui-settings

# Create first files:
touch netscan/settings.py
touch netscan/config_manager.py
touch netscan/widgets.py

# Start coding! 🎉
code .
```

**Viel Erfolg! 💪**
