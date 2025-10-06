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
