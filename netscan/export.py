"""
Export module for network scan results.

Supports multiple output formats:
- CSV: Comma-separated values
- JSON: JavaScript Object Notation (planned)
- Markdown: GitHub-flavored markdown tables (planned)
- HTML: Interactive HTML report (planned)
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HostData:
    """Represents a scanned host with all its data."""
    ip: str
    status: str  # "UP" or "DOWN"
    latency: Optional[float] = None
    hostname: Optional[str] = None
    mac: Optional[str] = None
    vendor: Optional[str] = None
    ports: Optional[List[int]] = None
    
    def __post_init__(self):
        """Ensure ports is a list."""
        if self.ports is None:
            self.ports = []


class Exporter:
    """Base class for all exporters."""
    
    def __init__(self, filepath: str):
        """
        Initialize exporter.
        
        Args:
            filepath: Path to output file
        """
        self.filepath = Path(filepath)
        self.timestamp = datetime.now()
    
    def export(self, hosts: List[HostData]) -> None:
        """
        Export hosts data to file.
        
        Args:
            hosts: List of HostData objects to export
        """
        raise NotImplementedError("Subclasses must implement export()")
    
    def _ensure_directory(self) -> None:
        """Ensure output directory exists."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)


class CSVExporter(Exporter):
    """Export scan results to CSV format."""
    
    def __init__(self, filepath: str, include_down: bool = False):
        """
        Initialize CSV exporter.
        
        Args:
            filepath: Path to output CSV file
            include_down: Include hosts that are DOWN
        """
        super().__init__(filepath)
        self.include_down = include_down
    
    def export(self, hosts: List[HostData]) -> None:
        """
        Export hosts to CSV file.
        
        CSV Format:
        IP,Status,Latency (ms),Hostname,MAC Address,Vendor,Open Ports
        
        Args:
            hosts: List of HostData objects to export
        """
        self._ensure_directory()
        
        # Filter hosts if needed
        filtered_hosts = hosts if self.include_down else [h for h in hosts if h.status == "UP"]
        
        with open(self.filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            
            # Write header
            writer.writerow([
                'IP Address',
                'Status',
                'Latency (ms)',
                'Hostname',
                'MAC Address',
                'Vendor',
                'Open Ports'
            ])
            
            # Write data rows
            for host in filtered_hosts:
                writer.writerow([
                    host.ip,
                    host.status,
                    f"{host.latency:.2f}" if host.latency is not None else "",
                    host.hostname or "",
                    host.mac or "",
                    self._escape_vendor(host.vendor or ""),
                    self._format_ports(host.ports)
                ])
    
    def _escape_vendor(self, vendor: str) -> str:
        """
        Escape vendor string for CSV.
        
        Handles commas and quotes in vendor names.
        
        Args:
            vendor: Vendor name string
            
        Returns:
            Escaped vendor string
        """
        if not vendor:
            return ""
        # CSV writer handles escaping automatically, but we clean up
        return vendor.strip()
    
    def _format_ports(self, ports: Optional[List[int]]) -> str:
        """
        Format port list for CSV output.
        
        Args:
            ports: List of open ports
            
        Returns:
            Formatted port string (e.g., "22, 80, 443" or "22-25, 80, 443")
        """
        if not ports:
            return ""
        
        # Sort ports
        sorted_ports = sorted(ports)
        
        # Always use ranges if there are 3+ consecutive ports
        return self._format_port_ranges(sorted_ports)
    
    def _format_port_ranges(self, ports: List[int]) -> str:
        """
        Format ports with ranges for compact display.
        
        Example: [22, 23, 24, 25, 80, 443] -> "22-25, 80, 443"
        
        Args:
            ports: Sorted list of port numbers
            
        Returns:
            Formatted string with ranges
        """
        if not ports:
            return ""
        
        ranges = []
        start = ports[0]
        end = ports[0]
        
        for port in ports[1:]:
            if port == end + 1:
                end = port
            else:
                # Add completed range
                if start == end:
                    ranges.append(str(start))
                elif end == start + 1:
                    ranges.append(f"{start}, {end}")
                else:
                    ranges.append(f"{start}-{end}")
                start = end = port
        
        # Add final range
        if start == end:
            ranges.append(str(start))
        elif end == start + 1:
            ranges.append(f"{start}, {end}")
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)


def export_to_csv(hosts: List[Dict[str, Any]], filepath: str, include_down: bool = False) -> None:
    """
    Convenience function to export hosts to CSV.
    
    Args:
        hosts: List of host dictionaries (from scanner)
        filepath: Output file path
        include_down: Include DOWN hosts
    """
    # Convert dict format to HostData
    host_data = []
    for h in hosts:
        host_data.append(HostData(
            ip=h.get('ip', ''),
            status=h.get('status', 'DOWN'),
            latency=h.get('latency'),
            hostname=h.get('hostname'),
            mac=h.get('mac'),
            vendor=h.get('vendor'),
            ports=h.get('ports', [])
        ))
    
    exporter = CSVExporter(filepath, include_down=include_down)
    exporter.export(host_data)
    
    return str(exporter.filepath)


class MarkdownExporter(Exporter):
    """Export scan results to Markdown format with tables."""
    
    def __init__(self, filepath: str, include_down: bool = False, use_emoji: bool = True):
        """
        Initialize Markdown exporter.
        
        Args:
            filepath: Path to output Markdown file
            include_down: Include hosts that are DOWN
            use_emoji: Use emoji for status (✅/❌) instead of UP/DOWN
        """
        super().__init__(filepath)
        self.include_down = include_down
        self.use_emoji = use_emoji
    
    def export(self, hosts: List[HostData]) -> None:
        """
        Export hosts to Markdown file with GitHub-flavored tables.
        
        Markdown Format:
        # Network Scan Results
        
        | IP Address | Status | Latency | Hostname | MAC | Vendor | Ports |
        |------------|--------|---------|----------|-----|--------|-------|
        | 192.168.1.1 | ✅ UP | 1.23 ms | router | AA:BB... | TP-Link | 22, 80 |
        
        Args:
            hosts: List of HostData objects to export
        """
        self._ensure_directory()
        
        # Filter hosts if needed
        filtered_hosts = hosts if self.include_down else [h for h in hosts if h.status == "UP"]
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            # Title
            f.write("# Network Scan Results\n\n")
            
            # Metadata
            f.write(f"**Scan Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            up_count = sum(1 for h in filtered_hosts if h.status == "UP")
            down_count = len(filtered_hosts) - up_count
            f.write(f"**Total Hosts**: {len(filtered_hosts)}")
            if self.include_down:
                f.write(f" ({up_count} UP, {down_count} DOWN)\n\n")
            else:
                f.write(" (UP only)\n\n")
            
            # Table
            f.write("## Host Details\n\n")
            
            # Header
            f.write("| IP Address | Status | Latency | Hostname | MAC Address | Vendor | Open Ports |\n")
            f.write("|------------|--------|---------|----------|-------------|--------|------------|\n")
            
            # Rows
            for host in filtered_hosts:
                ip = host.ip
                
                # Status with optional emoji
                if self.use_emoji:
                    status = "✅ UP" if host.status == "UP" else "❌ DOWN"
                else:
                    status = host.status
                
                # Latency
                if host.latency is not None:
                    latency = f"{host.latency:.2f} ms"
                else:
                    latency = "-"
                
                # Hostname
                hostname = host.hostname or "-"
                
                # MAC
                mac = host.mac or "-"
                
                # Vendor
                vendor = self._escape_markdown(host.vendor or "-")
                
                # Ports
                ports = self._format_ports(host.ports)
                
                f.write(f"| {ip} | {status} | {latency} | {hostname} | {mac} | {vendor} | {ports} |\n")
            
            # Footer
            f.write("\n---\n\n")
            f.write("*Generated by netscan*\n")
    
    def _escape_markdown(self, text: str) -> str:
        """
        Escape special Markdown characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for Markdown tables
        """
        if not text:
            return ""
        # Escape pipe character (table delimiter)
        text = text.replace("|", "\\|")
        return text
    
    def _format_ports(self, ports: Optional[List[int]]) -> str:
        """
        Format port list for Markdown.
        
        Args:
            ports: List of open ports
            
        Returns:
            Formatted port string with code formatting
        """
        if not ports:
            return "-"
        
        # Sort ports
        sorted_ports = sorted(ports)
        
        # Use ranges for compactness
        port_str = self._format_port_ranges(sorted_ports)
        
        # Wrap in code backticks
        return f"`{port_str}`"
    
    def _format_port_ranges(self, ports: List[int]) -> str:
        """
        Format ports with ranges for compact display.
        
        Example: [22, 23, 24, 25, 80, 443] -> "22-25, 80, 443"
        
        Args:
            ports: Sorted list of port numbers
            
        Returns:
            Formatted string with ranges
        """
        if not ports:
            return ""
        
        ranges = []
        start = ports[0]
        end = ports[0]
        
        for port in ports[1:]:
            if port == end + 1:
                end = port
            else:
                # Add completed range
                if start == end:
                    ranges.append(str(start))
                elif end == start + 1:
                    ranges.append(f"{start}, {end}")
                else:
                    ranges.append(f"{start}-{end}")
                start = end = port
        
        # Add final range
        if start == end:
            ranges.append(str(start))
        elif end == start + 1:
            ranges.append(f"{start}, {end}")
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)


def export_to_markdown(hosts: List[Dict[str, Any]], filepath: str, 
                       include_down: bool = False, use_emoji: bool = True) -> str:
    """
    Convenience function to export hosts to Markdown.
    
    Args:
        hosts: List of host dictionaries (from scanner)
        filepath: Output file path
        include_down: Include DOWN hosts
        use_emoji: Use emoji for status
        
    Returns:
        Absolute path to exported file
    """
    # Convert dict format to HostData
    host_data = []
    for h in hosts:
        host_data.append(HostData(
            ip=h.get('ip', ''),
            status=h.get('status', 'DOWN'),
            latency=h.get('latency'),
            hostname=h.get('hostname'),
            mac=h.get('mac'),
            vendor=h.get('vendor'),
            ports=h.get('ports', [])
        ))
    
    exporter = MarkdownExporter(filepath, include_down=include_down, use_emoji=use_emoji)
    exporter.export(host_data)
    
    return str(exporter.filepath)


class HTMLExporter(Exporter):
    """Export scan results to interactive HTML format."""
    
    def __init__(self, filepath: str, include_down: bool = False):
        """
        Initialize HTML exporter.
        
        Args:
            filepath: Path to output HTML file
            include_down: Include hosts that are DOWN
        """
        super().__init__(filepath)
        self.include_down = include_down
    
    def export(self, hosts: List[HostData]) -> None:
        """
        Export hosts to interactive HTML file with embedded CSS and JavaScript.
        
        Features:
        - Sortable columns (click headers)
        - Responsive design
        - Color-coded status
        - Search/filter functionality
        
        Args:
            hosts: List of HostData objects to export
        """
        self._ensure_directory()
        
        # Filter hosts if needed
        if self.include_down:
            filtered_hosts = hosts
            filter_note = f"{len(hosts)} total hosts"
        else:
            filtered_hosts = [h for h in hosts if h.status == "UP"]
            down_count = len(hosts) - len(filtered_hosts)
            filter_note = f"{len(filtered_hosts)} UP hosts (UP only)"
        
        up_count = sum(1 for h in hosts if h.status == "UP")
        down_count = len(hosts) - up_count
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(self._generate_html(filtered_hosts, up_count, down_count, filter_note))
    
    def _generate_html(self, hosts: List[HostData], up_count: int, down_count: int, filter_note: str) -> str:
        """Generate complete HTML document."""
        
        # Generate table rows
        rows_html = "\n".join(self._generate_row(host) for host in hosts)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Scan Results - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Network Scan Results</h1>
            <div class="metadata">
                <div class="meta-item">
                    <span class="meta-label">Scan Date:</span>
                    <span class="meta-value">{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Total Hosts:</span>
                    <span class="meta-value">{up_count + down_count}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Status:</span>
                    <span class="status-up">{up_count} UP</span> / 
                    <span class="status-down">{down_count} DOWN</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Filter:</span>
                    <span class="meta-value">{filter_note}</span>
                </div>
            </div>
        </header>
        
        <div class="controls">
            <input type="text" id="searchBox" placeholder="🔎 Search IP, hostname, MAC, or vendor...">
            <div class="info">
                <span id="resultCount">{len(hosts)}</span> hosts displayed
            </div>
        </div>
        
        <div class="table-container">
            <table id="scanTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">IP Address ▼</th>
                        <th onclick="sortTable(1)">Status ▼</th>
                        <th onclick="sortTable(2)">Latency ▼</th>
                        <th onclick="sortTable(3)">Hostname ▼</th>
                        <th onclick="sortTable(4)">MAC Address ▼</th>
                        <th onclick="sortTable(5)">Vendor ▼</th>
                        <th onclick="sortTable(6)">Open Ports ▼</th>
                    </tr>
                </thead>
                <tbody>
{rows_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated by <strong>netscan</strong> • Interactive HTML Report</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
    
    def _generate_row(self, host: HostData) -> str:
        """Generate HTML table row for a host."""
        status_class = "status-up" if host.status == "UP" else "status-down"
        status_symbol = "✅" if host.status == "UP" else "❌"
        
        latency = f"{host.latency:.2f} ms" if host.latency else "-"
        hostname = self._escape_html(host.hostname or "-")
        mac = host.mac or "-"
        vendor = self._escape_html(host.vendor or "-")
        
        # Format ports
        if host.ports:
            ports_str = self._format_port_ranges(host.ports)
        else:
            ports_str = "-"
        
        return f"""                    <tr>
                        <td class="ip-cell">{host.ip}</td>
                        <td class="{status_class}">{status_symbol} {host.status}</td>
                        <td class="latency-cell">{latency}</td>
                        <td>{hostname}</td>
                        <td class="mac-cell">{mac}</td>
                        <td>{vendor}</td>
                        <td class="ports-cell">{ports_str}</td>
                    </tr>"""
    
    def _format_port_ranges(self, ports: List[int]) -> str:
        """Format port list into compact ranges (e.g., '22-25, 80, 443')."""
        if not ports:
            return ""
        
        sorted_ports = sorted(set(ports))
        ranges = []
        start = sorted_ports[0]
        end = sorted_ports[0]
        
        for port in sorted_ports[1:]:
            if port == end + 1:
                end = port
            else:
                if end == start:
                    ranges.append(str(start))
                elif end == start + 1:
                    ranges.append(f"{start}, {end}")
                else:
                    ranges.append(f"{start}-{end}")
                start = end = port
        
        # Handle last range
        if end == start:
            ranges.append(str(start))
        elif end == start + 1:
            ranges.append(f"{start}, {end}")
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    def _get_css(self) -> str:
        """Return embedded CSS stylesheet."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .meta-item {
            background: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .meta-label {
            display: block;
            font-size: 0.85em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .meta-value {
            display: block;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .status-up {
            color: #10b981;
            font-weight: bold;
        }
        
        .status-down {
            color: #ef4444;
            font-weight: bold;
        }
        
        .controls {
            padding: 20px 30px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        #searchBox {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #cbd5e1;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        #searchBox:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .info {
            color: #64748b;
            font-size: 0.9em;
        }
        
        .table-container {
            overflow-x: auto;
            padding: 20px 30px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }
        
        thead {
            background: #f1f5f9;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        th {
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #475569;
            border-bottom: 2px solid #cbd5e1;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
        }
        
        th:hover {
            background: #e2e8f0;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #f1f5f9;
        }
        
        tbody tr {
            transition: background 0.2s;
        }
        
        tbody tr:hover {
            background: #f8fafc;
        }
        
        .ip-cell {
            font-family: 'Courier New', monospace;
            color: #3b82f6;
            font-weight: 600;
        }
        
        .latency-cell {
            font-family: 'Courier New', monospace;
            color: #64748b;
        }
        
        .mac-cell {
            font-family: 'Courier New', monospace;
            color: #8b5cf6;
            font-size: 0.9em;
        }
        
        .ports-cell {
            font-family: 'Courier New', monospace;
            color: #059669;
            font-weight: 500;
        }
        
        footer {
            padding: 20px 30px;
            text-align: center;
            background: #f8fafc;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            .metadata {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.85em;
            }
            
            th, td {
                padding: 8px 6px;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Return embedded JavaScript for interactivity."""
        return """
        // Search functionality
        const searchBox = document.getElementById('searchBox');
        const table = document.getElementById('scanTable');
        const tbody = table.getElementsByTagName('tbody')[0];
        const rows = Array.from(tbody.getElementsByTagName('tr'));
        const resultCount = document.getElementById('resultCount');
        
        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            let visibleCount = 0;
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            resultCount.textContent = visibleCount;
        });
        
        // Sorting functionality
        let sortDirections = {};
        
        function sortTable(columnIndex) {
            const currentDirection = sortDirections[columnIndex] || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            sortDirections[columnIndex] = newDirection;
            
            // Update header indicators
            const headers = table.querySelectorAll('th');
            headers.forEach((th, idx) => {
                if (idx === columnIndex) {
                    th.textContent = th.textContent.split(' ')[0] + ' ' + (newDirection === 'asc' ? '▼' : '▲');
                } else {
                    th.textContent = th.textContent.split(' ')[0] + ' ▼';
                }
            });
            
            const sortedRows = rows.sort((a, b) => {
                let aVal = a.cells[columnIndex].textContent.trim();
                let bVal = b.cells[columnIndex].textContent.trim();
                
                // Handle special cases
                if (columnIndex === 0) { // IP Address
                    aVal = ipToNumber(aVal);
                    bVal = ipToNumber(bVal);
                } else if (columnIndex === 2) { // Latency
                    aVal = parseFloat(aVal) || 99999;
                    bVal = parseFloat(bVal) || 99999;
                } else if (columnIndex === 1) { // Status
                    aVal = aVal.includes('UP') ? 0 : 1;
                    bVal = bVal.includes('UP') ? 0 : 1;
                }
                
                if (aVal < bVal) return newDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return newDirection === 'asc' ? 1 : -1;
                return 0;
            });
            
            // Re-append rows in sorted order
            sortedRows.forEach(row => tbody.appendChild(row));
        }
        
        function ipToNumber(ip) {
            return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0);
        }
        
        // Initial sort by IP
        sortTable(0);
        """


def export_to_html(hosts: List[Dict[str, Any]], filepath: str, include_down: bool = False) -> str:
    """
    Convenience function to export hosts to HTML.
    
    Args:
        hosts: List of host dictionaries (from scanner)
        filepath: Output file path
        include_down: Include DOWN hosts
        
    Returns:
        Absolute path to exported file
    """
    # Convert dict format to HostData
    host_data = []
    for h in hosts:
        host_data.append(HostData(
            ip=h.get('ip', ''),
            status=h.get('status', 'DOWN'),
            latency=h.get('latency'),
            hostname=h.get('hostname'),
            mac=h.get('mac'),
            vendor=h.get('vendor'),
            ports=h.get('ports', [])
        ))
    
    exporter = HTMLExporter(filepath, include_down=include_down)
    exporter.export(host_data)
    
    return str(exporter.filepath)


if __name__ == "__main__":
    # Example usage / testing
    test_hosts = [
        HostData(
            ip="192.168.1.1",
            status="UP",
            latency=1.23,
            hostname="router.local",
            mac="AA:BB:CC:DD:EE:FF",
            vendor="TP-Link",
            ports=[22, 80, 443]
        ),
        HostData(
            ip="192.168.1.10",
            status="UP",
            latency=2.45,
            hostname="server.local",
            mac="11:22:33:44:55:66",
            vendor="Dell Inc.",
            ports=[22, 23, 24, 25, 80, 443, 3306, 5432]
        ),
        HostData(
            ip="192.168.1.100",
            status="DOWN"
        ),
    ]
    
    exporter = CSVExporter("test_export.csv", include_down=False)
    exporter.export(test_hosts)
    print(f"✅ Exported to {exporter.filepath}")
