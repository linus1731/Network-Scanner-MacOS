"""
Tests for export module.
"""

import unittest
import tempfile
import csv
from pathlib import Path

from netscan.export import CSVExporter, MarkdownExporter, HTMLExporter, HostData, export_to_csv, export_to_markdown, export_to_html


class TestHostData(unittest.TestCase):
    """Test HostData dataclass."""
    
    def test_basic_host(self):
        """Test basic host creation."""
        host = HostData(ip="192.168.1.1", status="UP")
        self.assertEqual(host.ip, "192.168.1.1")
        self.assertEqual(host.status, "UP")
        self.assertIsNone(host.latency)
        self.assertIsNone(host.hostname)
        self.assertEqual(host.ports, [])
    
    def test_full_host(self):
        """Test host with all fields."""
        host = HostData(
            ip="192.168.1.1",
            status="UP",
            latency=1.23,
            hostname="router.local",
            mac="AA:BB:CC:DD:EE:FF",
            vendor="TP-Link",
            ports=[22, 80, 443]
        )
        self.assertEqual(host.ip, "192.168.1.1")
        self.assertEqual(host.latency, 1.23)
        self.assertEqual(len(host.ports), 3)


class TestCSVExporter(unittest.TestCase):
    """Test CSV export functionality."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_export_empty(self):
        """Test export with no hosts."""
        output = Path(self.temp_dir) / "empty.csv"
        exporter = CSVExporter(str(output))
        exporter.export([])
        
        self.assertTrue(output.exists())
        with open(output, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)  # Only header
            self.assertIn("IP Address", lines[0])
    
    def test_export_single_host(self):
        """Test export with single host."""
        output = Path(self.temp_dir) / "single.csv"
        exporter = CSVExporter(str(output))
        
        hosts = [
            HostData(
                ip="192.168.1.1",
                status="UP",
                latency=1.23,
                hostname="test.local",
                mac="AA:BB:CC:DD:EE:FF",
                vendor="Test Vendor",
                ports=[22, 80]
            )
        ]
        exporter.export(hosts)
        
        self.assertTrue(output.exists())
        with open(output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['IP Address'], "192.168.1.1")
            self.assertEqual(rows[0]['Status'], "UP")
            self.assertEqual(rows[0]['Latency (ms)'], "1.23")
            self.assertEqual(rows[0]['Hostname'], "test.local")
            self.assertEqual(rows[0]['Open Ports'], "22, 80")
    
    def test_filter_down_hosts(self):
        """Test that DOWN hosts are filtered by default."""
        output = Path(self.temp_dir) / "filtered.csv"
        exporter = CSVExporter(str(output), include_down=False)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
            HostData(ip="192.168.1.3", status="UP", latency=2.0),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)  # Only UP hosts
            self.assertEqual(rows[0]['IP Address'], "192.168.1.1")
            self.assertEqual(rows[1]['IP Address'], "192.168.1.3")
    
    def test_include_down_hosts(self):
        """Test including DOWN hosts."""
        output = Path(self.temp_dir) / "with_down.csv"
        exporter = CSVExporter(str(output), include_down=True)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)  # Both hosts
    
    def test_format_ports_simple(self):
        """Test simple port list formatting."""
        exporter = CSVExporter("dummy.csv")
        result = exporter._format_ports([22, 80, 443])
        self.assertEqual(result, "22, 80, 443")
    
    def test_format_ports_ranges(self):
        """Test port range formatting."""
        exporter = CSVExporter("dummy.csv")
        # Many ports should use ranges
        ports = [22, 23, 24, 25, 80, 443, 8000, 8001, 8002]
        result = exporter._format_ports(ports)
        self.assertIn("22-25", result)
        self.assertIn("8000-8002", result)
    
    def test_format_ports_empty(self):
        """Test empty port list."""
        exporter = CSVExporter("dummy.csv")
        self.assertEqual(exporter._format_ports([]), "")
        self.assertEqual(exporter._format_ports(None), "")
    
    def test_escape_vendor_with_comma(self):
        """Test vendor name with comma."""
        output = Path(self.temp_dir) / "vendor_comma.csv"
        exporter = CSVExporter(str(output))
        
        hosts = [
            HostData(
                ip="192.168.1.1",
                status="UP",
                vendor="Company, Inc."
            )
        ]
        exporter.export(hosts)
        
        # CSV should handle the comma properly
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("Company, Inc.", content)
    
    def test_convenience_function(self):
        """Test export_to_csv convenience function."""
        output = Path(self.temp_dir) / "convenience.csv"
        
        hosts_dict = [
            {
                'ip': '192.168.1.1',
                'status': 'UP',
                'latency': 1.5,
                'hostname': 'test.local',
                'mac': 'AA:BB:CC:DD:EE:FF',
                'vendor': 'Test',
                'ports': [22, 80]
            }
        ]
        
        result_path = export_to_csv(hosts_dict, str(output))
        
        self.assertTrue(Path(result_path).exists())
        with open(result_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['IP Address'], '192.168.1.1')


class TestPortRangeFormatting(unittest.TestCase):
    """Test port range formatting logic."""
    
    def setUp(self):
        self.exporter = CSVExporter("dummy.csv")
    
    def test_single_port(self):
        """Test single port."""
        result = self.exporter._format_port_ranges([80])
        self.assertEqual(result, "80")
    
    def test_two_consecutive_ports(self):
        """Test two consecutive ports."""
        result = self.exporter._format_port_ranges([80, 81])
        self.assertEqual(result, "80, 81")
    
    def test_three_consecutive_ports(self):
        """Test three consecutive ports forming a range."""
        result = self.exporter._format_port_ranges([80, 81, 82])
        self.assertEqual(result, "80-82")
    
    def test_mixed_ranges(self):
        """Test mixed single ports and ranges."""
        result = self.exporter._format_port_ranges([22, 23, 24, 80, 443, 444, 445])
        self.assertEqual(result, "22-24, 80, 443-445")
    
    def test_complex_pattern(self):
        """Test complex pattern."""
        result = self.exporter._format_port_ranges([1, 2, 3, 10, 20, 21, 22, 30])
        self.assertEqual(result, "1-3, 10, 20-22, 30")


class TestMarkdownExporter(unittest.TestCase):
    """Test Markdown export functionality."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_export_empty(self):
        """Test export with no hosts."""
        output = Path(self.temp_dir) / "empty.md"
        exporter = MarkdownExporter(str(output))
        exporter.export([])
        
        self.assertTrue(output.exists())
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("# Network Scan Results", content)
            self.assertIn("**Total Hosts**: 0", content)
    
    def test_export_with_emoji(self):
        """Test export with emoji status."""
        output = Path(self.temp_dir) / "emoji.md"
        exporter = MarkdownExporter(str(output), use_emoji=True, include_down=True)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.23),
            HostData(ip="192.168.1.2", status="DOWN")
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("✅ UP", content)
            self.assertIn("❌ DOWN", content)
    
    def test_export_without_emoji(self):
        """Test export without emoji."""
        output = Path(self.temp_dir) / "no_emoji.md"
        exporter = MarkdownExporter(str(output), use_emoji=False)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.23)
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("| UP |", content)
            self.assertNotIn("✅", content)
    
    def test_filter_down_hosts(self):
        """Test that DOWN hosts are filtered by default."""
        output = Path(self.temp_dir) / "filtered.md"
        exporter = MarkdownExporter(str(output), include_down=False)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
            HostData(ip="192.168.1.3", status="UP", latency=2.0),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("192.168.1.1", content)
            self.assertNotIn("192.168.1.2", content)
            self.assertIn("192.168.1.3", content)
            self.assertIn("**Total Hosts**: 2 (UP only)", content)
    
    def test_include_down_hosts(self):
        """Test including DOWN hosts."""
        output = Path(self.temp_dir) / "with_down.md"
        exporter = MarkdownExporter(str(output), include_down=True)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("192.168.1.1", content)
            self.assertIn("192.168.1.2", content)
            self.assertIn("(1 UP, 1 DOWN)", content)
    
    def test_port_formatting(self):
        """Test port formatting in Markdown."""
        output = Path(self.temp_dir) / "ports.md"
        exporter = MarkdownExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", ports=[22, 80, 443])
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            # Ports should be in code backticks
            self.assertIn("`22, 80, 443`", content)
    
    def test_port_ranges(self):
        """Test port range formatting."""
        output = Path(self.temp_dir) / "port_ranges.md"
        exporter = MarkdownExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", ports=[22, 23, 24, 25, 80, 443])
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("`22-25, 80, 443`", content)
    
    def test_escape_markdown(self):
        """Test Markdown special character escaping."""
        output = Path(self.temp_dir) / "escape.md"
        exporter = MarkdownExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", vendor="Company | Inc.")
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            # Pipe should be escaped
            self.assertIn("Company \\| Inc.", content)
    
    def test_table_structure(self):
        """Test that Markdown table structure is valid."""
        output = Path(self.temp_dir) / "table.md"
        exporter = MarkdownExporter(str(output))
        
        hosts = [
            HostData(
                ip="192.168.1.1",
                status="UP",
                latency=1.23,
                hostname="test.local",
                mac="AA:BB:CC:DD:EE:FF",
                vendor="Test Vendor",
                ports=[22, 80]
            )
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            lines = f.readlines()
            # Find table header
            header_found = False
            separator_found = False
            for i, line in enumerate(lines):
                if "| IP Address |" in line:
                    header_found = True
                    # Next line should be separator
                    if i + 1 < len(lines) and "|---" in lines[i + 1]:
                        separator_found = True
            
            self.assertTrue(header_found, "Table header not found")
            self.assertTrue(separator_found, "Table separator not found")
    
    def test_convenience_function(self):
        """Test export_to_markdown convenience function."""
        output = Path(self.temp_dir) / "convenience.md"
        
        hosts_dict = [
            {
                'ip': '192.168.1.1',
                'status': 'UP',
                'latency': 1.5,
                'hostname': 'test.local',
                'mac': 'AA:BB:CC:DD:EE:FF',
                'vendor': 'Test',
                'ports': [22, 80]
            }
        ]
        
        result_path = export_to_markdown(hosts_dict, str(output))
        
        self.assertTrue(Path(result_path).exists())
        with open(result_path, 'r') as f:
            content = f.read()
            self.assertIn('192.168.1.1', content)
            self.assertIn('test.local', content)


class TestHTMLExporter(unittest.TestCase):
    """Test HTML export functionality."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_export_empty(self):
        """Test export with no hosts."""
        output = Path(self.temp_dir) / "empty.html"
        exporter = HTMLExporter(str(output))
        exporter.export([])
        
        self.assertTrue(output.exists())
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Network Scan Results", content)
            self.assertIn("<span id=\"resultCount\">0</span> hosts displayed", content)
    
    def test_export_with_hosts(self):
        """Test export with hosts."""
        output = Path(self.temp_dir) / "hosts.html"
        exporter = HTMLExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.23),
            HostData(ip="192.168.1.2", status="DOWN")
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("192.168.1.1", content)
            self.assertIn("✅ UP", content)
            self.assertIn("1.23 ms", content)
    
    def test_html_structure(self):
        """Test that HTML structure is valid."""
        output = Path(self.temp_dir) / "structure.html"
        exporter = HTMLExporter(str(output))
        
        hosts = [HostData(ip="192.168.1.1", status="UP")]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            # Check for essential HTML elements
            self.assertIn("<html", content)
            self.assertIn("</html>", content)
            self.assertIn("<head>", content)
            self.assertIn("</head>", content)
            self.assertIn("<body>", content)
            self.assertIn("</body>", content)
            self.assertIn("<table", content)
            self.assertIn("</table>", content)
            self.assertIn("<script>", content)
            self.assertIn("</script>", content)
            self.assertIn("<style>", content)
            self.assertIn("</style>", content)
    
    def test_filter_down_hosts(self):
        """Test that DOWN hosts are filtered by default."""
        output = Path(self.temp_dir) / "filtered.html"
        exporter = HTMLExporter(str(output), include_down=False)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
            HostData(ip="192.168.1.3", status="UP", latency=2.0),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("192.168.1.1", content)
            self.assertNotIn("192.168.1.2", content)
            self.assertIn("192.168.1.3", content)
            self.assertIn("<span id=\"resultCount\">2</span> hosts displayed", content)
    
    def test_include_down_hosts(self):
        """Test including DOWN hosts."""
        output = Path(self.temp_dir) / "with_down.html"
        exporter = HTMLExporter(str(output), include_down=True)
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", latency=1.0),
            HostData(ip="192.168.1.2", status="DOWN"),
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("192.168.1.1", content)
            self.assertIn("192.168.1.2", content)
            self.assertIn("✅ UP", content)
            self.assertIn("❌ DOWN", content)
    
    def test_port_formatting(self):
        """Test port formatting in HTML."""
        output = Path(self.temp_dir) / "ports.html"
        exporter = HTMLExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", ports=[22, 80, 443])
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("22, 80, 443", content)
    
    def test_port_ranges(self):
        """Test port range formatting."""
        output = Path(self.temp_dir) / "port_ranges.html"
        exporter = HTMLExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", ports=[22, 23, 24, 25, 80, 443])
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn("22-25", content)
            self.assertIn("80", content)
            self.assertIn("443", content)
    
    def test_html_escaping(self):
        """Test HTML special character escaping."""
        output = Path(self.temp_dir) / "escape.html"
        exporter = HTMLExporter(str(output))
        
        hosts = [
            HostData(ip="192.168.1.1", status="UP", vendor="Company <script>alert('xss')</script>")
        ]
        exporter.export(hosts)
        
        with open(output, 'r') as f:
            content = f.read()
            # Should be escaped
            self.assertIn("&lt;script&gt;", content)
            self.assertNotIn("<script>alert", content)
    
    def test_convenience_function(self):
        """Test export_to_html convenience function."""
        output = Path(self.temp_dir) / "convenience.html"
        
        hosts_dict = [
            {
                'ip': '192.168.1.1',
                'status': 'UP',
                'latency': 1.5,
                'hostname': 'test.local',
                'mac': 'AA:BB:CC:DD:EE:FF',
                'vendor': 'Test',
                'ports': [22, 80]
            }
        ]
        
        result_path = export_to_html(hosts_dict, str(output))
        
        self.assertTrue(Path(result_path).exists())
        with open(result_path, 'r') as f:
            content = f.read()
            self.assertIn('192.168.1.1', content)
            self.assertIn('test.local', content)
            self.assertIn('<!DOCTYPE html>', content)


if __name__ == '__main__':
    unittest.main()
