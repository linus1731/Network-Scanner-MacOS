"""
Network Statistics - Calculate health scores and analyze network data.
"""

from typing import List, Dict, Optional, Tuple
import re


class NetworkStats:
    """Calculate various network statistics and health metrics."""
    
    @staticmethod
    def calculate_health_score(hosts: List[dict]) -> float:
        """
        Calculate overall network health score (0-100).
        
        Factors:
        - UP/DOWN ratio (40 points)
        - Response times (30 points)
        - Open ports security (20 points)
        - Network diversity (10 points)
        
        Args:
            hosts: List of host dictionaries
            
        Returns:
            Health score from 0 to 100
        """
        if not hosts:
            return 0.0
        
        score = 0.0
        
        # 1. UP/DOWN ratio (40 points)
        up_count = sum(1 for h in hosts if h.get('up'))
        up_ratio = up_count / len(hosts) if hosts else 0
        score += up_ratio * 40
        
        # 2. Response times (30 points)
        latencies = [h.get('latency_ms', 0) for h in hosts if h.get('up') and h.get('latency_ms')]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            # Good: <10ms=30pts, Fair: <50ms=20pts, Poor: <100ms=10pts, Bad: >100ms=0pts
            if avg_latency < 10:
                score += 30
            elif avg_latency < 50:
                score += 20
            elif avg_latency < 100:
                score += 10
        
        # 3. Open ports security (20 points)
        # Deduct points for risky open ports
        risky_ports = {23: 5, 3389: 3, 21: 2, 445: 2, 135: 1}  # telnet, rdp, ftp, smb, rpc
        risk_score = 0
        for host in hosts:
            ports = host.get('ports', [])
            for port in ports:
                risk_score += risky_ports.get(port, 0)
        
        # Max deduction: 20 points
        security_score = max(0, 20 - min(20, risk_score))
        score += security_score
        
        # 4. Network diversity (10 points)
        # Points for having various device types
        unique_macs = len(set(h.get('mac') for h in hosts if h.get('mac')))
        diversity_score = min(10, unique_macs / 2)  # 20+ unique MACs = full 10 points
        score += diversity_score
        
        return min(100.0, max(0.0, score))
    
    @staticmethod
    def get_health_rating(score: float) -> str:
        """Get text rating for health score."""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 30:
            return "Poor"
        else:
            return "Critical"
    
    @staticmethod
    def get_device_breakdown(hosts: List[dict]) -> Dict[str, int]:
        """
        Categorize devices by type.
        
        Returns:
            Dict mapping device type to count
        """
        categories: Dict[str, int] = {
            'computer': 0,
            'phone': 0,
            'iot': 0,
            'server': 0,
            'router': 0,
            'unknown': 0,
        }
        
        for host in hosts:
            if not host.get('up'):
                continue
            
            device_type = DeviceCategorizer.categorize(host)
            categories[device_type] = categories.get(device_type, 0) + 1
        
        return categories
    
    @staticmethod
    def get_service_distribution(hosts: List[dict]) -> Dict[str, int]:
        """
        Count common services across all hosts.
        
        Returns:
            Dict mapping service name to count
        """
        from .scanner import get_service_name
        
        services: Dict[str, int] = {}
        
        for host in hosts:
            if not host.get('up'):
                continue
            
            ports = host.get('ports', [])
            for port in ports:
                service = get_service_name(port)
                services[service] = services.get(service, 0) + 1
        
        # Sort by count and return top services
        sorted_services = dict(sorted(services.items(), key=lambda x: x[1], reverse=True))
        return sorted_services
    
    @staticmethod
    def get_response_time_stats(hosts: List[dict]) -> Dict[str, float]:
        """
        Calculate response time statistics.
        
        Returns:
            Dict with min, max, avg, median latencies
        """
        latencies = [h.get('latency_ms', 0) for h in hosts if h.get('up') and h.get('latency_ms')]
        
        if not latencies:
            return {'min': 0, 'max': 0, 'avg': 0, 'median': 0}
        
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        
        return {
            'min': sorted_lat[0],
            'max': sorted_lat[-1],
            'avg': sum(sorted_lat) / n,
            'median': sorted_lat[n // 2] if n % 2 else (sorted_lat[n//2 - 1] + sorted_lat[n//2]) / 2
        }
    
    @staticmethod
    def get_port_count(hosts: List[dict]) -> Tuple[int, int]:
        """
        Get total open ports and unique ports.
        
        Returns:
            Tuple of (total_ports, unique_ports)
        """
        all_ports = []
        for host in hosts:
            all_ports.extend(host.get('ports', []))
        
        return len(all_ports), len(set(all_ports))


class DeviceCategorizer:
    """Categorize network devices by type."""
    
    # MAC address vendor prefixes (OUI)
    MAC_VENDORS = {
        'apple': 'phone',
        'samsung': 'phone',
        'huawei': 'phone',
        'xiaomi': 'phone',
        'intel': 'computer',
        'dell': 'computer',
        'hp': 'computer',
        'lenovo': 'computer',
        'asus': 'computer',
        'microsoft': 'computer',
        'cisco': 'router',
        'netgear': 'router',
        'tp-link': 'router',
        'linksys': 'router',
        'd-link': 'router',
        'amazon': 'iot',
        'google': 'iot',
        'nest': 'iot',
        'philips': 'iot',
        'sonos': 'iot',
    }
    
    # Port patterns indicating device type
    SERVER_PORTS = {22, 80, 443, 3306, 5432, 6379, 27017, 9200, 8080, 8443}
    IOT_PORTS = {1883, 5683, 8883}  # MQTT, CoAP
    ROUTER_PORTS = {53, 67, 68}  # DNS, DHCP
    
    @staticmethod
    def categorize(host: dict) -> str:
        """
        Categorize a host by device type.
        
        Args:
            host: Host dictionary with ip, hostname, mac, ports
            
        Returns:
            Device type: computer, phone, iot, server, router, unknown
        """
        # Check by MAC vendor
        mac = host.get('mac', '').lower()
        vendor = host.get('vendor', '').lower()
        
        for keyword, device_type in DeviceCategorizer.MAC_VENDORS.items():
            if keyword in vendor or keyword in mac:
                # Special case: Apple devices could be computers too
                if keyword == 'apple':
                    hostname = host.get('hostname', '').lower()
                    if 'macbook' in hostname or 'imac' in hostname or 'mac-mini' in hostname:
                        return 'computer'
                    elif 'iphone' in hostname or 'ipad' in hostname:
                        return 'phone'
                return device_type
        
        # Check by hostname patterns
        hostname = (host.get('hostname') or '').lower()
        if any(word in hostname for word in ['iphone', 'android', 'phone', 'mobile']):
            return 'phone'
        if any(word in hostname for word in ['laptop', 'desktop', 'pc', 'macbook', 'imac']):
            return 'computer'
        if any(word in hostname for word in ['router', 'gateway', 'modem']):
            return 'router'
        if any(word in hostname for word in ['server', 'srv', 'db', 'web']):
            return 'server'
        if any(word in hostname for word in ['alexa', 'nest', 'hue', 'smart', 'iot']):
            return 'iot'
        
        # Check by open ports
        ports = set(host.get('ports', []))
        
        # Router if has DNS/DHCP
        if ports & DeviceCategorizer.ROUTER_PORTS:
            return 'router'
        
        # Server if has multiple server ports
        if len(ports & DeviceCategorizer.SERVER_PORTS) >= 2:
            return 'server'
        
        # IoT if has IoT-specific ports
        if ports & DeviceCategorizer.IOT_PORTS:
            return 'iot'
        
        # Computer if has SSH or RDP
        if 22 in ports or 3389 in ports:
            return 'computer'
        
        # Default
        return 'unknown'
    
    @staticmethod
    def get_device_icon(device_type: str) -> str:
        """Get emoji icon for device type."""
        icons = {
            'computer': '💻',
            'phone': '📱',
            'iot': '🔌',
            'server': '🖥️',
            'router': '📡',
            'unknown': '❓',
        }
        return icons.get(device_type, '❓')
