# Task F: TUI Dashboard - Implementation Plan

**Priority**: P1 (Selected!) | **Complexity**: Medium-High | **Estimated Time**: 3-4 days

---

## Overview

Transform the TUI from a simple host list into a **professional network monitoring dashboard** with multiple views, statistics, and quick actions.

---

## Design Goals

1. **Dashboard as Main Screen**: Overview of network health
2. **Multiple Views**: Dashboard, Host List, Details
3. **Visual Statistics**: Charts, graphs, health scores
4. **Quick Actions**: F1-F10 function keys
5. **Smooth Transitions**: Tab-based navigation
6. **Professional Look**: Modern UI with boxes and colors

---

## Architecture

### View System
```
┌─────────────────────────────────────────────────────────┐
│ [F1] Dashboard  [F2] Hosts  [F3] Details  [F4] Scan... │
└─────────────────────────────────────────────────────────┘
         ↓              ↓            ↓
    Dashboard View   Host List   Detail View
```

### Dashboard Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Network Scanner Dashboard          [Last scan: 2m ago]      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──── Network Health ────┐  ┌──── Device Breakdown ─────┐ │
│  │                         │  │                           │ │
│  │  ████████████░░ 85%     │  │  Computers:    12  ████  │ │
│  │                         │  │  Phones:        5  ██    │ │
│  │  UP:   42  DOWN:  8     │  │  IoT:           8  ███   │ │
│  │  Ports: 1,247 open      │  │  Servers:       3  █     │ │
│  │                         │  │  Unknown:      14  █████  │ │
│  └─────────────────────────┘  └───────────────────────────┘ │
│                                                              │
│  ┌──── Top Services ───────┐  ┌──── Recent Activity ─────┐ │
│  │                         │  │                           │ │
│  │  HTTP/HTTPS:  28  ████  │  │ • 192.168.1.50 UP   2m   │ │
│  │  SSH:         15  ███   │  │ • 192.168.1.23 DOWN 5m   │ │
│  │  MySQL:        5  █     │  │ • New host detected! 8m  │ │
│  │  RDP:          3  █     │  │ • Port scan complete 12m │ │
│  │  PostgreSQL:   2  █     │  │ • Cache cleared      15m │ │
│  └─────────────────────────┘  └───────────────────────────┘ │
│                                                              │
│  ┌──── Network Traffic ────────────────────────────────────┐ │
│  │ RX: ▁▂▃▅▇█▆▄▃▂  124.3 KB/s  (max: 2.1 MB/s)            │ │
│  │ TX: ▁▁▂▃▄▅▄▃▂▁   45.2 KB/s  (max: 890 KB/s)            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  Quick Actions: [F5] Rescan  [F6] Export  [F7] Profile     │
│                 [F8] Rates   [F9] Clear    [F10] Quit       │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Phase 1: View System Framework (Day 1)

#### 1.1 View Architecture
```python
class View:
    """Base class for all views"""
    def draw(self, stdscr, app_state) -> None
    def handle_input(self, ch, app_state) -> bool
    def on_enter(self, app_state) -> None
    def on_exit(self, app_state) -> None

class DashboardView(View):
    """Main dashboard overview"""
    
class HostListView(View):
    """Current host list view"""
    
class DetailView(View):
    """Detailed host information"""
```

#### 1.2 View Manager
```python
class ViewManager:
    def __init__(self):
        self.views = {
            'dashboard': DashboardView(),
            'hosts': HostListView(),
            'detail': DetailView(),
        }
        self.current_view = 'dashboard'
    
    def switch_to(self, view_name: str)
    def draw(self, stdscr, app_state)
    def handle_input(self, ch, app_state)
```

#### 1.3 Tab Navigation
- F1: Dashboard
- F2: Host List
- F3: Detail View
- F4: Scan Dialog (future)
- Tab: Cycle through views
- Shift+Tab: Reverse cycle

**Files**: `netscan/tui_views.py` (new), modify `netscan/tui.py`

---

### Phase 2: Dashboard Components (Day 2)

#### 2.1 Network Health Widget
```python
class NetworkHealthWidget:
    def calculate_health_score(self, hosts) -> float:
        """
        Calculate 0-100 health score based on:
        - UP/DOWN ratio (40%)
        - Response times (30%)
        - Open ports security (20%)
        - Network diversity (10%)
        """
    
    def draw_health_bar(self, stdscr, y, x, score)
    def draw_stats(self, stdscr, y, x, hosts)
```

**Visual**: Progress bar with color gradient (red→yellow→green)

#### 2.2 Device Breakdown Widget
```python
class DeviceBreakdownWidget:
    def categorize_devices(self, hosts) -> dict:
        """
        Categorize by:
        - MAC vendor (Apple → phone/computer)
        - Open ports (22,80,443 → server)
        - mDNS services (→ specific device types)
        - Hostname patterns
        """
    
    def draw_chart(self, stdscr, y, x, categories)
```

**Visual**: Horizontal bar chart with counts

#### 2.3 Top Services Widget
```python
class TopServicesWidget:
    def aggregate_services(self, hosts) -> dict
    def draw_chart(self, stdscr, y, x, services)
```

**Visual**: Horizontal bar chart of most common services

#### 2.4 Recent Activity Feed
```python
class ActivityFeed:
    def __init__(self):
        self.events: List[Event] = []
        self.max_events = 50
    
    def add_event(self, type, message, ip=None)
    def get_recent(self, n=5) -> List[Event]
    def draw(self, stdscr, y, x, width, height)
```

**Events**:
- Host UP/DOWN changes
- New hosts discovered
- Port scan completion
- Profile changes
- Export completion
- Cache operations

**Files**: `netscan/tui_widgets.py` (new)

---

### Phase 3: Dashboard Layout (Day 2-3)

#### 3.1 Responsive Grid System
```python
class GridLayout:
    """Responsive grid for dashboard widgets"""
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = {}
    
    def add_widget(self, widget, row, col, rowspan=1, colspan=1)
    def calculate_geometry(self, width, height) -> dict
    def draw_all(self, stdscr, app_state)
```

#### 3.2 Box Drawing
```python
def draw_box(stdscr, y, x, height, width, title="", color=0):
    """Draw a bordered box with optional title"""
    # Uses Unicode box-drawing characters
    # ┌─┬─┐
    # │ │ │
    # ├─┼─┤
    # │ │ │
    # └─┴─┘
```

#### 3.3 Dashboard Layout
```python
# Grid: 4 rows × 2 cols
grid = GridLayout(4, 2)
grid.add_widget(NetworkHealthWidget(), row=0, col=0)
grid.add_widget(DeviceBreakdownWidget(), row=0, col=1)
grid.add_widget(TopServicesWidget(), row=1, col=0)
grid.add_widget(ActivityFeedWidget(), row=1, col=1)
grid.add_widget(NetworkTrafficWidget(), row=2, col=0, colspan=2)
grid.add_widget(QuickActionsWidget(), row=3, col=0, colspan=2)
```

**Files**: `netscan/tui_layout.py` (new)

---

### Phase 4: Quick Actions & Function Keys (Day 3)

#### 4.1 Function Key Mapping
```python
F1_KEY = 265   # Dashboard view
F2_KEY = 266   # Host list view
F3_KEY = 267   # Detail view
F4_KEY = 268   # (Reserved: Scan dialog)
F5_KEY = 269   # Quick rescan
F6_KEY = 270   # Quick export
F7_KEY = 271   # Profile selector
F8_KEY = 272   # Rate limit dialog
F9_KEY = 273   # Clear cache
F10_KEY = 274  # Quit
```

#### 4.2 Quick Action Bar
```python
class QuickActionsBar:
    def draw(self, stdscr, y, x, width):
        """
        [F5] Rescan  [F6] Export  [F7] Profile  [F8] Rate  [F9] Clear  [F10] Quit
        """
```

#### 4.3 Action Handlers
```python
def handle_quick_action(key: int, app_state):
    if key == F5_KEY:
        trigger_scan(app_state)
    elif key == F6_KEY:
        open_export_dialog(app_state)
    # ... etc
```

**Files**: Modify `netscan/tui.py`, add handlers

---

### Phase 5: Statistics & Calculations (Day 3)

#### 5.1 Network Statistics
```python
class NetworkStats:
    @staticmethod
    def calculate_health_score(hosts) -> float
    @staticmethod
    def get_device_breakdown(hosts) -> dict
    @staticmethod
    def get_service_distribution(hosts) -> dict
    @staticmethod
    def get_response_time_stats(hosts) -> dict
```

#### 5.2 Device Categorization
```python
class DeviceCategorizer:
    MAC_VENDORS = {
        'apple': 'phone',
        'samsung': 'phone',
        'intel': 'computer',
        'dell': 'computer',
        # ... more
    }
    
    @staticmethod
    def categorize(host) -> str:
        """Returns: computer, phone, iot, server, unknown"""
```

**Files**: `netscan/stats.py` (new)

---

### Phase 6: Integration & Polish (Day 4)

#### 6.1 State Management
```python
class AppState:
    """Centralized application state"""
    def __init__(self):
        self.view_manager = ViewManager()
        self.activity_feed = ActivityFeed()
        self.scan_results = []
        self.network_stats = NetworkStats()
        # ... existing state
    
    def update_stats(self)
    def add_activity(self, type, message)
```

#### 6.2 Smooth Transitions
- Fade effects when switching views (if terminal supports)
- Loading spinners during operations
- Toast notifications for quick actions

#### 6.3 Color Schemes
```python
# Dashboard-specific colors
HEALTH_GOOD = curses.COLOR_GREEN
HEALTH_WARNING = curses.COLOR_YELLOW
HEALTH_CRITICAL = curses.COLOR_RED
WIDGET_BORDER = curses.COLOR_CYAN
WIDGET_TITLE = curses.COLOR_YELLOW
```

#### 6.4 Hotkey Help
- `?` - Show comprehensive help overlay
- Shows all hotkeys by view
- Dashboard shortcuts
- Navigation keys

**Files**: Modify `netscan/tui.py`, polish all components

---

## Testing Plan

### Unit Tests
```python
# tests/test_tui_widgets.py
def test_health_score_calculation()
def test_device_categorization()
def test_activity_feed()

# tests/test_tui_views.py
def test_view_switching()
def test_dashboard_layout()

# tests/test_stats.py
def test_network_statistics()
def test_service_aggregation()
```

### Manual Testing
- [ ] Test on different terminal sizes (80×24 to 200×50)
- [ ] Verify all function keys work
- [ ] Test view switching performance
- [ ] Verify statistics calculations
- [ ] Test with 0, 10, 100, 254 hosts
- [ ] Test activity feed overflow
- [ ] Test responsive layout

---

## User Experience Improvements

### Before (Current)
```
User launches TUI → Sees host list → Manually triggers scan
Must navigate to see details
Export requires Shift+E
Profile change requires Shift+P
Rate limit requires +/-
```

### After (Dashboard)
```
User launches TUI → Sees Dashboard with network overview
Quick scan with F5
Quick export with F6
Quick profile with F7
Quick rate adjust with F8
Switch to host list with F2
Everything at fingertips!
```

---

## Success Metrics

### Visual Appeal
- ✅ Professional-looking dashboard
- ✅ Clear visual hierarchy
- ✅ Color-coded information
- ✅ Intuitive navigation

### Functionality
- ✅ Health score accurately reflects network state
- ✅ Device categorization works for common types
- ✅ Activity feed shows relevant events
- ✅ Quick actions reduce clicks

### Performance
- ✅ Dashboard renders in <100ms
- ✅ View switching is instant
- ✅ No lag with 254 hosts
- ✅ Statistics update in real-time

---

## Documentation Updates

### README.md
- Add dashboard screenshots (ASCII art)
- Document function keys
- Show new views
- Update feature list

### RELEASE_NOTES.md
- v0.2.0 announcement
- Dashboard features list
- Migration guide (if needed)

---

## Future Enhancements (Post-v0.2.0)

### Dashboard Customization
- User-configurable widget layout
- Show/hide widgets
- Custom color schemes
- Save/load layouts

### Advanced Widgets
- Network topology map (ASCII art)
- Latency distribution histogram
- Port scan progress visualization
- Historical trend graphs

### Smart Alerts
- Notification when new host appears
- Alert when host goes down
- Warning for suspicious ports
- Performance degradation alerts

---

## Files to Create/Modify

### New Files
```
netscan/tui_views.py      (~400 lines) - View system
netscan/tui_widgets.py    (~500 lines) - Dashboard widgets
netscan/tui_layout.py     (~200 lines) - Grid layout system
netscan/stats.py          (~300 lines) - Statistics calculations
tests/test_tui_views.py   (~200 lines) - View tests
tests/test_tui_widgets.py (~250 lines) - Widget tests
tests/test_stats.py       (~150 lines) - Stats tests
```

### Modified Files
```
netscan/tui.py            - Integrate view manager
netscan/__init__.py       - Export new classes
README.md                 - Dashboard documentation
RELEASE_NOTES.md          - v0.2.0 announcement
.tasks/TASKS.md           - Mark Task F complete
```

**Total**: ~2,500 new lines + 600 modified lines

---

## Timeline

### Day 1: Foundation
- Morning: View system architecture
- Afternoon: View manager implementation
- Evening: Basic view switching

### Day 2: Widgets
- Morning: Health & breakdown widgets
- Afternoon: Services & activity feed
- Evening: Traffic visualization

### Day 3: Dashboard Assembly
- Morning: Grid layout system
- Afternoon: Dashboard integration
- Evening: Quick actions & F-keys

### Day 4: Polish
- Morning: Color schemes & styling
- Afternoon: Testing & bug fixes
- Evening: Documentation & commit

---

## Let's Get Started!

Ready to build an **amazing dashboard**? 🎨

This will make your network scanner look **professional** and feel **powerful**!

**Next step**: Shall I start with Phase 1 (View System Framework)?
