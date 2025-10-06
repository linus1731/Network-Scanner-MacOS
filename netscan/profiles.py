"""
Scan profiles for Network Scanner.

Provides predefined and custom scan profiles with different
performance/stealth characteristics.
"""

import os
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class ScanProfile:
    """Configuration for a scan profile."""
    
    name: str
    description: str
    concurrency: int
    timeout: float
    port_range: str  # e.g., "1-100", "top100", "top1000", "1-10000"
    rate_limit: Optional[int] = None  # packets/second, None = unlimited
    random_delay: bool = False  # Add random delays for stealth
    min_delay: float = 0.0  # Minimum delay between scans (seconds)
    max_delay: float = 0.0  # Maximum delay between scans (seconds)
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanProfile':
        """Create profile from dictionary."""
        return cls(**data)


# Predefined profiles
PREDEFINED_PROFILES = {
    'quick': ScanProfile(
        name='quick',
        description='Fast scan with top 100 ports (< 1 minute)',
        concurrency=256,
        timeout=0.5,
        port_range='top100',
        rate_limit=None,
        random_delay=False,
        min_delay=0.0,
        max_delay=0.0
    ),
    
    'normal': ScanProfile(
        name='normal',
        description='Balanced scan with top 1000 ports (2-3 minutes)',
        concurrency=128,
        timeout=1.0,
        port_range='top1000',
        rate_limit=None,
        random_delay=False,
        min_delay=0.0,
        max_delay=0.0
    ),
    
    'thorough': ScanProfile(
        name='thorough',
        description='Deep scan of all 10,000 ports (5-10 minutes)',
        concurrency=64,
        timeout=2.0,
        port_range='1-10000',
        rate_limit=None,
        random_delay=False,
        min_delay=0.0,
        max_delay=0.0
    ),
    
    'stealth': ScanProfile(
        name='stealth',
        description='Slow, low-profile scan (10-15 minutes)',
        concurrency=10,
        timeout=3.0,
        port_range='top1000',
        rate_limit=50,  # 50 packets/second
        random_delay=True,
        min_delay=0.1,
        max_delay=0.5
    ),
}

# Top ports lists
TOP_100_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080,
    20, 69, 137, 138, 161, 162, 389, 636, 1433, 1521,
    2049, 3268, 3269, 5060, 5061, 5432, 5666, 5900, 6379, 8000,
    8008, 8443, 8888, 9090, 9200, 9300, 10000, 27017, 50000, 50070,
    # Additional common ports
    119, 194, 543, 544, 631, 873, 902, 1080, 1194, 1352,
    1433, 1434, 1521, 1720, 2082, 2083, 2181, 2222, 2375, 2376,
    3000, 3128, 3690, 4443, 4444, 4567, 5000, 5001, 5222, 5269,
    5357, 5800, 5985, 5986, 6000, 6001, 6379, 7001, 7002, 7070,
    8001, 8009, 8081, 8082, 8180, 8888, 9000, 9001, 9080, 9090,
]

TOP_1000_PORTS = list(range(1, 1001))  # Simplified for now


def get_profile(name: str) -> Optional[ScanProfile]:
    """
    Get a scan profile by name.
    
    Args:
        name: Profile name (e.g., 'quick', 'normal', 'thorough', 'stealth')
        
    Returns:
        ScanProfile if found, None otherwise
    """
    # Check predefined profiles
    if name.lower() in PREDEFINED_PROFILES:
        return PREDEFINED_PROFILES[name.lower()]
    
    # Check custom profiles
    custom_profile = load_custom_profile(name)
    if custom_profile:
        return custom_profile
    
    return None


def list_profiles() -> Dict[str, ScanProfile]:
    """
    List all available profiles (predefined + custom).
    
    Returns:
        Dictionary mapping profile names to ScanProfile objects
    """
    profiles = PREDEFINED_PROFILES.copy()
    
    # Add custom profiles
    custom_profiles = load_all_custom_profiles()
    profiles.update(custom_profiles)
    
    return profiles


def save_custom_profile(profile: ScanProfile) -> bool:
    """
    Save a custom profile to disk.
    
    Args:
        profile: ScanProfile to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        profile_dir = get_profile_directory()
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profile_dir / f"{profile.name}.yaml"
        
        with open(profile_file, 'w') as f:
            yaml.dump(profile.to_dict(), f, default_flow_style=False)
        
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False


def load_custom_profile(name: str) -> Optional[ScanProfile]:
    """
    Load a custom profile from disk.
    
    Args:
        name: Profile name
        
    Returns:
        ScanProfile if found, None otherwise
    """
    try:
        profile_dir = get_profile_directory()
        profile_file = profile_dir / f"{name}.yaml"
        
        if not profile_file.exists():
            return None
        
        with open(profile_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return ScanProfile.from_dict(data)
    except Exception as e:
        print(f"Error loading profile '{name}': {e}")
        return None


def load_all_custom_profiles() -> Dict[str, ScanProfile]:
    """
    Load all custom profiles from disk.
    
    Returns:
        Dictionary mapping profile names to ScanProfile objects
    """
    profiles = {}
    
    try:
        profile_dir = get_profile_directory()
        
        if not profile_dir.exists():
            return profiles
        
        for profile_file in profile_dir.glob("*.yaml"):
            try:
                with open(profile_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                profile = ScanProfile.from_dict(data)
                profiles[profile.name] = profile
            except Exception as e:
                print(f"Error loading profile from {profile_file}: {e}")
                continue
    
    except Exception as e:
        print(f"Error loading custom profiles: {e}")
    
    return profiles


def delete_custom_profile(name: str) -> bool:
    """
    Delete a custom profile.
    
    Args:
        name: Profile name
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        profile_dir = get_profile_directory()
        profile_file = profile_dir / f"{name}.yaml"
        
        if profile_file.exists():
            profile_file.unlink()
            return True
        
        return False
    except Exception as e:
        print(f"Error deleting profile '{name}': {e}")
        return False


def get_profile_directory() -> Path:
    """
    Get the directory for custom profiles.
    
    Returns:
        Path to profile directory
    """
    return Path.home() / '.netscan' / 'profiles'


def get_ports_from_range(port_range: str) -> List[int]:
    """
    Convert port range string to list of ports.
    
    Args:
        port_range: Port range string (e.g., "1-100", "top100", "top1000")
        
    Returns:
        List of port numbers
    """
    if port_range == 'top100':
        return TOP_100_PORTS
    elif port_range == 'top1000':
        return TOP_1000_PORTS
    elif '-' in port_range:
        # Parse range like "1-100"
        try:
            start, end = port_range.split('-')
            return list(range(int(start), int(end) + 1))
        except ValueError:
            print(f"Invalid port range: {port_range}")
            return list(range(1, 1001))  # Default to top 1000
    else:
        # Single port
        try:
            return [int(port_range)]
        except ValueError:
            print(f"Invalid port specification: {port_range}")
            return list(range(1, 1001))  # Default to top 1000
