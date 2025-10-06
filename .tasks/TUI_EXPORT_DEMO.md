# TUI Export Feature - Demo Guide

## ✨ Overview

The TUI now has a fully interactive CSV export dialog accessible with the `e` key!

## 🎯 How to Use

### 1. Start the TUI
```bash
python3 -m netscan.tui
```

### 2. Perform a Scan
- Press `s` to start a network scan
- Wait for hosts to be discovered
- Navigate hosts with `↑`/`↓`

### 3. Export Results
- Press `e` to open the export dialog

### 4. Export Dialog

```
┌──────────────────────────────────────────────────────────────────┐
│                        Export to CSV                             │
│                                                                  │
│ Filename:                                                        │
│  scan_20251006_143022.csv                                       │
│                                                                  │
│ Options:                                                         │
│  [ ] Include DOWN hosts                                          │
│                                                                  │
│ Preview:                                                         │
│  → Exporting 5 hosts (UP only)                                  │
│                                                                  │
│ Controls:                                                        │
│  [Enter] Export  [Space] Toggle option  [Esc] Cancel            │
└──────────────────────────────────────────────────────────────────┘
```

## 🎮 Dialog Controls

| Key | Action |
|-----|--------|
| `Enter` | Export to CSV file |
| `Space` | Toggle "Include DOWN hosts" |
| `←` `→` | Move cursor in filename |
| `Backspace` | Delete character before cursor |
| `Delete` | Delete character at cursor |
| `Home` | Jump to start of filename |
| `End` | Jump to end of filename |
| Any char | Insert character at cursor |
| `Esc` | Cancel and return to main view |

## 📝 Filename Editing

The filename is **fully editable** with cursor support:

```
Before:  scan_20251006_143022.csv
         ^cursor here
         
After editing:
         my_network_scan.csv
         ^cursor here
```

## 📊 Export Options

### Include DOWN Hosts
- **[ ]** (unchecked): Export only UP hosts (default)
- **[X]** (checked): Export all hosts including DOWN

**Preview updates in real-time:**
```
[ ] Include DOWN hosts
 → Exporting 5 hosts (UP only)

[X] Include DOWN hosts
 → Exporting 12 hosts (5 UP, 7 DOWN)
```

## ✅ Success Feedback

After export, a success message appears in the footer for 5 seconds:

```
✅ Exported to: /path/to/scan_20251006_143022.csv
```

Or in case of error:

```
❌ Export failed: Permission denied
```

## 🎨 Features

### Smart Defaults
- **Auto-generated filename** with timestamp: `scan_YYYYMMDD_HHMMSS.csv`
- **Current directory** as export location
- **UP-only export** by default (common use case)

### Real-time Preview
- Shows exact number of hosts that will be exported
- Displays UP/DOWN breakdown when "Include DOWN hosts" is checked
- Updates instantly when toggling options

### Cursor Navigation
- Full cursor support with visual indicator (blinking cursor)
- Navigate and edit anywhere in the filename
- Supports all standard editing keys

### Error Handling
- Screen too small? Shows error message instead of broken dialog
- Invalid filename? Export fails gracefully with error message
- All exceptions caught and displayed to user

## 💡 Tips

1. **Quick Export**: Press `e`, then immediately `Enter` to export with defaults
2. **Custom Names**: Use descriptive names like `office_network.csv` or `home_scan_weekend.csv`
3. **Include DOWN**: Useful for tracking which IPs are allocated but not responsive
4. **Timestamp**: Default filenames include timestamp to avoid overwriting previous scans

## 🔧 Technical Details

### CSV Format
Exported CSV includes all scan data:
```csv
IP Address,Status,Latency (ms),Hostname,MAC Address,Vendor,Open Ports
192.168.1.1,UP,1.23,router.local,AA:BB:CC:DD:EE:FF,TP-Link,"22, 80, 443"
192.168.1.10,UP,2.45,server.local,11:22:33:44:55:66,Dell Inc.,"22-25, 80, 443, 3306"
```

### Port Data
- Includes open ports from the currently selected host's port scan
- Ports are formatted as ranges when possible: `22-25, 80, 443`
- Only includes port data if a port scan has been performed

### File Location
- Exports to current working directory by default
- Can specify absolute path: `/Users/me/Documents/scan.csv`
- Supports relative paths: `../exports/scan.csv`

## 🚀 Future Enhancements

Planned improvements (from roadmap):

- **Multiple Formats**: JSON, Markdown, HTML (Tasks 1.2, 1.3)
- **Format Selection**: Radio buttons in dialog
- **Path Browser**: Visual file picker
- **Auto-Export**: Automatic export after each scan
- **Export Templates**: Predefined formats and filters

## 📖 Related Documentation

- **Task 1.1**: CSV Export Implementation
- **Task 1.4**: TUI Export Integration (this feature)
- **PROJECT_ROADMAP.md**: Full feature roadmap
- **TASKS.md**: Detailed task tracking

---

**Status**: ✅ Complete  
**Version**: v0.1.1  
**Date**: October 6, 2025
