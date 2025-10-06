# Scan Profiles Feature Documentation

> **Completed**: October 6, 2025  
> **Task**: Task 3 - Scan Profiles  
> **Status**: ✅ Complete

---

## 📋 Overview

The Scan Profiles system allows users to quickly switch between predefined scanning configurations or create custom profiles tailored to specific use cases. This dramatically improves workflow efficiency and makes the scanner more accessible to users with different needs.

## ✨ Features Implemented

### 1. Core Profile System (`netscan/profiles.py`)
- **ScanProfile dataclass** with configurable parameters:
  - `concurrency`: Number of concurrent scans
  - `timeout`: Timeout per host (seconds)
  - `port_range`: Ports to scan (e.g., "top100", "1-10000")
  - `rate_limit`: Optional packets/second limit
  - `random_delay`: Enable/disable random delays
  - `min_delay`/`max_delay`: Random delay ranges
  
- **Profile Management**:
  - Load/save profiles to YAML files
  - Persistent storage in `~/.netscan/profiles/`
  - Profile discovery and listing
  - Custom profile creation

### 2. Predefined Profiles

#### Quick Profile 🚀
- **Use Case**: Fast network health checks
- **Settings**: Concurrency=256, Timeout=0.5s, Ports=top100
- **Duration**: < 1 minute
- **Best For**: Quick overview, ping sweeps, availability checks

#### Normal Profile ⚖️
- **Use Case**: Balanced scanning (default)
- **Settings**: Concurrency=128, Timeout=1.0s, Ports=top1000
- **Duration**: 2-3 minutes
- **Best For**: General network scanning, daily monitoring

#### Thorough Profile 🔍
- **Use Case**: Deep comprehensive scans
- **Settings**: Concurrency=64, Timeout=2.0s, Ports=1-10000
- **Duration**: 5-10 minutes
- **Best For**: Security audits, complete network inventory

#### Stealth Profile 🥷
- **Use Case**: Low-profile scanning
- **Settings**: Concurrency=10, Timeout=3.0s, Rate=50pkt/s, Random delays
- **Duration**: 10-15 minutes
- **Best For**: Avoiding detection, production networks

### 3. CLI Integration

```bash
# List all available profiles
netscan --list-profiles

# Use a specific profile
netscan --profile quick
netscan --profile thorough --output-html audit.html

# Create custom profile from current settings
netscan --save-profile my-profile -c 100 -t 1.5

# Profile with export
netscan --profile stealth --output-csv stealth-scan.csv
```

### 4. TUI Integration

- **Hotkey**: Press `Shift+P` to open profile selection dialog
- **Active Profile Display**: Shown in header bar
- **Visual Profile Selection**: 
  - Navigate with ↑/↓ arrows
  - Preview profile details before selecting
  - Color-coded profiles (predefined vs custom)
- **Profile Persistence**: Active profile remembered between scans

### 5. Example Custom Profiles

Created 4 production-ready example profiles in `examples/custom-profiles/`:

1. **production-safe.yaml**
   - Conservative settings for live production systems
   - Low concurrency, rate-limited, random delays
   - Minimal network impact

2. **home-network.yaml**
   - Optimized for home/small office networks
   - High concurrency, no rate limits
   - Fast and thorough

3. **pentest-deep.yaml**
   - Comprehensive security assessment profile
   - All 10,000 ports scanned
   - No rate limits for speed

4. **iot-discovery.yaml**
   - Patient scanning for IoT devices
   - Gentle rate limiting
   - Extended timeouts for slow devices

## 📊 Test Coverage

**22 comprehensive unit tests** in `tests/test_profiles.py`:

- ✅ Profile creation and validation
- ✅ Predefined profile verification
- ✅ Custom profile save/load
- ✅ Profile directory management
- ✅ Port range parsing (top100, top1000, ranges)
- ✅ YAML serialization/deserialization
- ✅ Profile listing and discovery

**All 57 tests passing** (35 export + 22 profiles)

## 🎯 Use Cases

### 1. Quick Health Check
```bash
netscan --profile quick
```
Perfect for: Morning network checks, quick availability verification

### 2. Security Audit
```bash
netscan --profile thorough --output-html security-audit-$(date +%Y%m%d).html
```
Perfect for: Comprehensive security assessments, compliance audits

### 3. Stealth Reconnaissance
```bash
netscan --profile stealth --output-csv stealth-scan.csv
```
Perfect for: Avoiding IDS/IPS detection, production scanning

### 4. IoT Device Discovery
```bash
netscan --profile iot-discovery
```
Perfect for: Smart home setup, IoT inventory, device troubleshooting

### 5. Custom Workflow
```bash
# Create profile once
netscan --save-profile my-workflow -c 150 -t 1.2

# Reuse anytime
netscan --profile my-workflow
```

## 🔧 Technical Implementation

### Architecture
```
netscan/
├── profiles.py         # Core profile system
├── cli.py              # CLI integration (--profile, --list-profiles, --save-profile)
├── tui.py              # TUI integration (Shift+P dialog)
└── scanner.py          # Uses profile settings (concurrency, timeout)

~/.netscan/
└── profiles/           # User custom profiles
    └── *.yaml          # YAML profile files

examples/
└── custom-profiles/    # Example profiles
    ├── README.md       # Documentation
    └── *.yaml          # 4 example profiles
```

### Profile Data Structure (YAML)
```yaml
name: my-profile
description: Custom scan profile
concurrency: 128
timeout: 1.0
port_range: top1000
rate_limit: null
random_delay: false
min_delay: 0.0
max_delay: 0.0
```

### Port Range Parsing
- `"top100"` → Top 100 most common ports
- `"top1000"` → Ports 1-1000
- `"1-10000"` → Custom range (ports 1 to 10000)
- `"80"` → Single port

## 📈 Performance Impact

| Profile | Hosts/Network | Est. Time | Network Load | Use Case |
|---------|---------------|-----------|--------------|----------|
| Quick | 254 hosts | <1 min | Very High | Health checks |
| Normal | 254 hosts | 2-3 min | High | Daily scanning |
| Thorough | 254 hosts | 5-10 min | Medium | Security audits |
| Stealth | 254 hosts | 10-15 min | Very Low | Stealth ops |

## 🚀 Future Enhancements

Potential improvements for future versions:

1. **Profile Templates**: Web-based profile generator
2. **Profile Scheduling**: Automatic profile switching by time of day
3. **Profile Analytics**: Track which profiles are most used
4. **Profile Validation**: Pre-flight checks for profile settings
5. **Profile Sharing**: Export/import profile bundles

## 📝 Documentation Updates

- ✅ CLI help text updated with profile options
- ✅ TUI help line updated with `[P]rofile` hotkey
- ✅ Example profiles with detailed comments
- ✅ README with profile comparison table
- ✅ Use case documentation

## 🎉 Success Metrics

- ✅ **14/14 subtasks completed** (100%)
- ✅ **57 tests passing** (35 export + 22 profiles)
- ✅ **4 example profiles** ready for production use
- ✅ **CLI + TUI integration** fully functional
- ✅ **Zero breaking changes** to existing functionality
- ✅ **Backward compatible** (default profile maintains current behavior)

---

## 📌 Key Commits

1. **95aa98b**: Add scan profiles system (Task 3.1-3.4)
   - Core profile system
   - Predefined profiles
   - CLI integration
   - TUI integration
   - 22 unit tests

2. **73bccb8**: Add custom profile examples and documentation (Task 3.5)
   - 4 example profiles
   - Comprehensive README
   - Task tracking updates

---

**Task Status**: ✅ **COMPLETE**  
**Quality**: Production-ready  
**Documentation**: Comprehensive  
**Tests**: 100% passing
