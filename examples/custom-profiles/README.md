# Custom Scan Profile Examples

This directory contains example custom scan profiles that can be copied to `~/.netscan/profiles/`.

## Installation

Copy any profile to your netscan profiles directory:

```bash
cp examples/custom-profiles/production-safe.yaml ~/.netscan/profiles/
```

Then use it with:

```bash
netscan --profile production-safe
```

Or in the TUI: Press `Shift+P` to select the profile.

## Available Example Profiles

### 1. production-safe.yaml
Conservative profile for scanning production networks without causing disruption.

### 2. home-network.yaml
Optimized for home network scanning with good balance of speed and detail.

### 3. pentest-deep.yaml
Comprehensive profile for security testing and penetration testing.

### 4. iot-discovery.yaml
Designed for discovering IoT devices with specific port ranges and timing.

## Profile Parameters

Each profile can configure:

- **concurrency**: Number of concurrent scans (higher = faster, but more network load)
- **timeout**: Timeout per host in seconds (lower = faster, but may miss slow hosts)
- **port_range**: Ports to scan
  - `"top100"` - Top 100 most common ports (fastest)
  - `"top1000"` - Top 1000 common ports (balanced)
  - `"1-1000"` - Scan ports 1-1000
  - `"1-10000"` - Deep scan (slowest but most thorough)
- **rate_limit**: Packets per second (null = unlimited)
- **random_delay**: Add random delays between scans (useful for stealth)
- **min_delay/max_delay**: Random delay range in seconds

## Creating Your Own Profile

1. **Using CLI**:
```bash
# Create profile from current settings
netscan --save-profile my-profile -c 100 -t 1.5
```

2. **Manual YAML**:
```yaml
name: my-custom-profile
description: My custom scan profile
concurrency: 128
timeout: 1.0
port_range: top1000
rate_limit: null
random_delay: false
min_delay: 0.0
max_delay: 0.0
```

Save to `~/.netscan/profiles/my-custom-profile.yaml`.

## Use Cases

### Quick Health Check
Use `quick` profile for rapid network health checks:
```bash
netscan --profile quick
```

### Security Audit
Use `thorough` or custom `pentest-deep` for comprehensive audits:
```bash
netscan --profile thorough --output-html security-audit.html
```

### Stealth Scanning
Use `stealth` profile to avoid detection:
```bash
netscan --profile stealth
```

### Production Monitoring
Use `production-safe` to monitor without disrupting services:
```bash
netscan --profile production-safe --output-csv monitoring.csv
```
