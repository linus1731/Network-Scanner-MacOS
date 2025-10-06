# 🎮 TUI Dashboard - Testing Guide

**Branch**: `feature/tui-dashboard`  
**Status**: Ready for manual testing  
**Date**: October 7, 2025

---

## 🚀 Quick Start

```bash
# Checkout the feature branch
git checkout feature/tui-dashboard

# Run the TUI
python3 -m netscan.tui
```

---

## ⌨️ Keyboard Shortcuts

### View Navigation
- **F1** - Switch to Dashboard view (network overview)
- **F2** - Switch to Host List view (traditional table) [DEFAULT]
- **F3** - Switch to Details view (deep dive)
- **Tab** - Cycle to next view
- **Shift+Tab** - Cycle to previous view

### Existing Shortcuts (still work)
- **s** - Start scan
- **r** - Refresh network detection
- **P** - Profile selection (Shift+P)
- **+/-** - Adjust rate limit
- **a** - Toggle active-only filter
- **e** - Export dialog
- **C** - Clear cache (Shift+C)
- **1-5** - Sort by column
- **o** - Cycle sort column
- **O** - Toggle asc/desc (Shift+O)
- **p** - Port scan selected host
- **↑/↓** - Navigate host list
- **Enter** - View host details
- **q** - Quit

---

## 🎯 Testing Checklist

### View Switching
- [ ] Press F1 → Dashboard view appears
- [ ] Press F2 → Host list appears (default view)
- [ ] Press F3 → Details view appears
- [ ] Press Tab → Cycles through views
- [ ] Check tab bar shows active view (● vs ○)

### Dashboard View (F1)
- [ ] Network health score displays (0-100)
- [ ] Health progress bar shows with gradient color
- [ ] Device breakdown chart displays
- [ ] Device icons render correctly (💻📱🏠🖥️🌐)
- [ ] Top services widget shows open ports
- [ ] Activity feed displays recent events
- [ ] Traffic graphs render (RX/TX sparklines)
- [ ] Quick actions bar shows at bottom

### Activity Feed
- [ ] Scan start event appears when pressing 's'
- [ ] Scan complete event shows with host count
- [ ] Export events appear after exporting (press 'e')
- [ ] Profile change events appear (press 'P')
- [ ] Events are color-coded by severity
- [ ] Timestamps show "2s ago" format

### Host List View (F2)
- [ ] Traditional table view works as before
- [ ] All sorting works (1-5, o, O)
- [ ] Selection works (↑/↓)
- [ ] Port scanning works (p)
- [ ] Host details panel shows on left
- [ ] Traffic graphs show at top

### Details View (F3)
- [ ] Detailed host information displays
- [ ] Network information section complete
- [ ] Port list displays if scanned
- [ ] Vendor information shows if available

### Responsive Layout
- [ ] Resize terminal smaller → widgets adjust
- [ ] Resize terminal larger → widgets expand
- [ ] Very small terminal → graceful degradation
- [ ] Tab bar always visible on line 2

### Statistics Accuracy
- [ ] Health score updates after scan
- [ ] Device counts match actual hosts
- [ ] Service distribution accurate
- [ ] Activity feed shows all events

---

## 🐛 Known Issues

None currently - if you find any, document them here!

---

## 📊 Performance Testing

1. **Large Network Scan** (192.168.1.0/24):
   - [ ] Dashboard renders smoothly
   - [ ] No lag when switching views
   - [ ] Activity feed handles many events
   - [ ] Health calculation completes quickly

2. **Rapid View Switching**:
   - [ ] Press F1-F2-F3 rapidly
   - [ ] No crashes or visual glitches
   - [ ] Tab bar updates correctly

3. **During Active Scan**:
   - [ ] Dashboard updates in real-time
   - [ ] Activity feed shows progress
   - [ ] View switching works while scanning

---

## 🎨 Visual Verification

### Dashboard Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Network Health: ████████░░ 85/100 (Excellent)              │
├─────────────────────────────────────────────────────────────┤
│ Device Breakdown: 💻██████ 60% | 📱███ 30% | 🏠█ 10%       │
├─────────────────────────────────────────────────────────────┤
│ Top Services: http ████ 12 | ssh ███ 8 | https ██ 5        │
├─────────────────────────────────────────────────────────────┤
│ Activity Feed:                                              │
│   [SUCCESS] Scan complete: 45/254 hosts up (2s ago)        │
│   [INFO] Scan started: 192.168.1.0/24 (5s ago)             │
├─────────────────────────────────────────────────────────────┤
│ Traffic: RX ▂▃▄█▆▃  TX ▁▂▃▄▃▂                               │
├─────────────────────────────────────────────────────────────┤
│ [F5] Scan [F6] Export [F7] Profile [F8] Refresh            │
└─────────────────────────────────────────────────────────────┘
```

### Color Verification
- Green (healthy): Health 85+
- Yellow (warning): Health 50-84
- Red (critical): Health 0-49
- Blue (info): Activity info events
- Green (success): Activity success events

---

## 🔍 Component Tests

Already verified:
```bash
python3 test_dashboard.py
```

Output should show:
- ✅ Views registered successfully
- ✅ Tab bar generation working
- ✅ Activity feed tracking events
- ✅ Network health calculation

---

## 📸 Screenshot Locations

After testing, capture screenshots:
1. Dashboard view with full network scan
2. Host list view (traditional)
3. Details view with port scan
4. Activity feed with multiple events
5. Small terminal size handling

Save to: `.tasks/screenshots/dashboard/`

---

## 🔄 Integration Testing

### Workflow 1: First Launch
1. Start TUI → Should show Host List (F2)
2. Press 's' → Scan starts, activity event logged
3. Wait for completion → Activity event logged
4. Press F1 → Dashboard shows statistics
5. Verify health score calculated

### Workflow 2: Export
1. Complete a scan
2. Press F1 → View dashboard
3. Press 'e' → Export dialog
4. Complete export → Activity event appears
5. Return to dashboard → Event visible in feed

### Workflow 3: Profile Switch
1. Press F1 → Dashboard view
2. Press 'P' → Profile selection
3. Select different profile
4. Return to dashboard
5. Verify activity event logged

---

## 🎉 Success Criteria

Dashboard integration is successful if:
- ✅ All 3 views render without crashes
- ✅ F1-F3 + Tab navigation works smoothly
- ✅ Activity feed captures all event types
- ✅ Health calculation accurate and fast
- ✅ Layout responsive to terminal size
- ✅ No performance degradation
- ✅ All existing functionality preserved

---

## 📝 Test Results

**Tester**: _________________  
**Date**: _________________  
**Terminal**: _________________  
**OS Version**: _________________  

**Overall Result**: ⬜ PASS  ⬜ FAIL  ⬜ NEEDS WORK

**Notes**:
```
[Write notes here]
```

---

## 🚨 Report Issues

If you find bugs, document:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Terminal size
5. Python version
6. Error messages (if any)

Create issue on GitHub with label `dashboard` and `bug`.

---

**Happy Testing! 🎮**
