# Quick Task Reference

## 🚦 Current Status
- **Version**: 0.1.1
- **Branch**: v0.1.1
- **Active Tasks**: 0
- **Completed**: v0.1.1 Release (Split-Panel TUI + 10K Ports)

## ⚡ Next Up (Phase 1)

### 🎯 PRIORITY 0: TUI Settings & Feature-Integration (Task 10)
**Warum zuerst?** Macht alle Features nutzbar und legt Framework für Settings fest!

```bash
# Week 1: Settings-Framework
- Settings-System (settings.py, config_manager.py)
- Widget-System (widgets.py)
- Settings-Panel-UI (tui_settings.py)
- Basic Hotkey-Integration

# Week 2: Feature-Integration
- Export-Dialog (tui_export.py)
- Profile-Menu (tui_profile.py)
- Main-Menu (tui_menu.py)
- Help-Overlay (tui_help.py)

# Steps:
1. Create netscan/settings.py (Settings-Klasse)
2. Create netscan/config_manager.py (YAML-Handler)
3. Create netscan/widgets.py (Input-Widgets)
4. Create netscan/tui_settings.py (Settings-Panel)
5. Integrate Hotkeys in tui.py (F1-F10)
```

### PRIORITY 1: CSV Export (Task 1.1)
```bash
# Files to create:
- netscan/export.py
- tests/test_export.py

# Files to modify:
- netscan/cli.py (add --output-csv)

# Steps:
1. Create Exporter base class
2. Implement CSVExporter
3. Add CLI option
4. Write tests
```

### PRIORITY 2: Markdown Export (Task 1.2)
```bash
# After CSV is done
# Similar structure, Markdown table format
```

### PRIORITY 3: HTML Export (Task 1.3)
```bash
# After Markdown
# With interactive sorting
```

## � Milestone-Übersicht

| Version | Features | Status | Deadline |
|---------|----------|--------|----------|
| v0.2.0 | TUI-Settings, Export, Profile, Rate-Limits | ⬜ Geplant | ~3 Wochen |
| v0.3.0 | Banner-Grabbing, OUI-DB | ⬜ Geplant | ~1.5 Monate |
| v1.0.0 | IPv6, mDNS, History | ⬜ Geplant | ~2-3 Monate |

## 📂 File Structure Reference

```
netscan/
├── __init__.py
├── __main__.py
├── arp.py
├── cli.py
├── colors.py
├── netinfo.py
├── resolve.py
├── scanner.py
├── traffic.py
├── tui.py
└── vendor.py

# To be created:
├── export.py          (Task 1)
├── ratelimit.py       (Task 2)
├── profiles.py        (Task 3)
├── banners.py         (Task 4)
├── oui_updater.py     (Task 5)
├── mdns.py            (Task 7)
├── discovery.py       (Task 8)
├── history.py         (Task 9)
├── database.py        (Task 9)
└── diff.py            (Task 9)
```

## 🔧 Commands

```bash
# Start new feature
git checkout -b feature/csv-export

# Run tests
python -m pytest tests/

# Update task status
# Edit .tasks/TASKS.md

# Create release
git tag v0.2.0
git push origin v0.2.0
```

## 📖 Documentation

- Full details: `.tasks/TASKS.md`
- Roadmap: `PROJECT_ROADMAP.md`
- Release notes: `RELEASE_NOTES.md`

---
Last updated: 2025-10-06 18:45
