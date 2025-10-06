"""
Unit tests for scan profiles.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from netscan.profiles import (
    ScanProfile,
    PREDEFINED_PROFILES,
    get_profile,
    list_profiles,
    save_custom_profile,
    load_custom_profile,
    load_all_custom_profiles,
    delete_custom_profile,
    get_ports_from_range,
    get_profile_directory,
    TOP_100_PORTS
)


class TestScanProfile(unittest.TestCase):
    """Test ScanProfile dataclass."""
    
    def test_create_profile(self):
        """Test creating a scan profile."""
        profile = ScanProfile(
            name='test',
            description='Test profile',
            concurrency=100,
            timeout=1.0,
            port_range='1-1000'
        )
        
        self.assertEqual(profile.name, 'test')
        self.assertEqual(profile.description, 'Test profile')
        self.assertEqual(profile.concurrency, 100)
        self.assertEqual(profile.timeout, 1.0)
        self.assertEqual(profile.port_range, '1-1000')
        self.assertIsNone(profile.rate_limit)
        self.assertFalse(profile.random_delay)
    
    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = ScanProfile(
            name='test',
            description='Test profile',
            concurrency=100,
            timeout=1.0,
            port_range='1-1000'
        )
        
        data = profile.to_dict()
        
        self.assertEqual(data['name'], 'test')
        self.assertEqual(data['description'], 'Test profile')
        self.assertEqual(data['concurrency'], 100)
    
    def test_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            'name': 'test',
            'description': 'Test profile',
            'concurrency': 100,
            'timeout': 1.0,
            'port_range': '1-1000',
            'rate_limit': None,
            'random_delay': False,
            'min_delay': 0.0,
            'max_delay': 0.0
        }
        
        profile = ScanProfile.from_dict(data)
        
        self.assertEqual(profile.name, 'test')
        self.assertEqual(profile.concurrency, 100)


class TestPredefinedProfiles(unittest.TestCase):
    """Test predefined profiles."""
    
    def test_quick_profile(self):
        """Test quick profile."""
        profile = PREDEFINED_PROFILES['quick']
        
        self.assertEqual(profile.name, 'quick')
        self.assertEqual(profile.concurrency, 256)
        self.assertEqual(profile.timeout, 0.5)
        self.assertEqual(profile.port_range, 'top100')
        self.assertFalse(profile.random_delay)
    
    def test_normal_profile(self):
        """Test normal profile."""
        profile = PREDEFINED_PROFILES['normal']
        
        self.assertEqual(profile.name, 'normal')
        self.assertEqual(profile.concurrency, 128)
        self.assertEqual(profile.timeout, 1.0)
        self.assertEqual(profile.port_range, 'top1000')
    
    def test_thorough_profile(self):
        """Test thorough profile."""
        profile = PREDEFINED_PROFILES['thorough']
        
        self.assertEqual(profile.name, 'thorough')
        self.assertEqual(profile.concurrency, 64)
        self.assertEqual(profile.timeout, 2.0)
        self.assertEqual(profile.port_range, '1-10000')
    
    def test_stealth_profile(self):
        """Test stealth profile."""
        profile = PREDEFINED_PROFILES['stealth']
        
        self.assertEqual(profile.name, 'stealth')
        self.assertEqual(profile.concurrency, 10)
        self.assertEqual(profile.timeout, 3.0)
        self.assertTrue(profile.random_delay)
        self.assertEqual(profile.rate_limit, 50)
        self.assertEqual(profile.min_delay, 0.1)
        self.assertEqual(profile.max_delay, 0.5)


class TestGetProfile(unittest.TestCase):
    """Test get_profile function."""
    
    def test_get_predefined_profile(self):
        """Test getting a predefined profile."""
        profile = get_profile('quick')
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, 'quick')
    
    def test_get_nonexistent_profile(self):
        """Test getting a non-existent profile."""
        profile = get_profile('nonexistent')
        
        self.assertIsNone(profile)
    
    def test_case_insensitive(self):
        """Test that profile lookup is case-insensitive."""
        profile = get_profile('QUICK')
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, 'quick')


class TestCustomProfiles(unittest.TestCase):
    """Test custom profile management."""
    
    def setUp(self):
        """Set up temporary profile directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.orig_home = Path.home()
        
        # Mock get_profile_directory to use temp dir
        import netscan.profiles as profiles_module
        self.orig_get_profile_directory = profiles_module.get_profile_directory
        profiles_module.get_profile_directory = lambda: Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary profile directory."""
        import netscan.profiles as profiles_module
        profiles_module.get_profile_directory = self.orig_get_profile_directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_custom_profile(self):
        """Test saving a custom profile."""
        profile = ScanProfile(
            name='custom',
            description='Custom profile',
            concurrency=50,
            timeout=1.5,
            port_range='1-500'
        )
        
        result = save_custom_profile(profile)
        
        self.assertTrue(result)
        
        # Check file exists
        profile_file = Path(self.temp_dir) / 'custom.yaml'
        self.assertTrue(profile_file.exists())
    
    def test_load_custom_profile(self):
        """Test loading a custom profile."""
        profile = ScanProfile(
            name='custom',
            description='Custom profile',
            concurrency=50,
            timeout=1.5,
            port_range='1-500'
        )
        
        save_custom_profile(profile)
        loaded_profile = load_custom_profile('custom')
        
        self.assertIsNotNone(loaded_profile)
        self.assertEqual(loaded_profile.name, 'custom')
        self.assertEqual(loaded_profile.concurrency, 50)
        self.assertEqual(loaded_profile.timeout, 1.5)
    
    def test_load_nonexistent_custom_profile(self):
        """Test loading a non-existent custom profile."""
        profile = load_custom_profile('nonexistent')
        
        self.assertIsNone(profile)
    
    def test_load_all_custom_profiles(self):
        """Test loading all custom profiles."""
        # Create multiple custom profiles
        profile1 = ScanProfile(
            name='custom1',
            description='Custom profile 1',
            concurrency=50,
            timeout=1.5,
            port_range='1-500'
        )
        profile2 = ScanProfile(
            name='custom2',
            description='Custom profile 2',
            concurrency=75,
            timeout=2.0,
            port_range='1-1000'
        )
        
        save_custom_profile(profile1)
        save_custom_profile(profile2)
        
        profiles = load_all_custom_profiles()
        
        self.assertEqual(len(profiles), 2)
        self.assertIn('custom1', profiles)
        self.assertIn('custom2', profiles)
    
    def test_delete_custom_profile(self):
        """Test deleting a custom profile."""
        profile = ScanProfile(
            name='custom',
            description='Custom profile',
            concurrency=50,
            timeout=1.5,
            port_range='1-500'
        )
        
        save_custom_profile(profile)
        result = delete_custom_profile('custom')
        
        self.assertTrue(result)
        
        # Check file is deleted
        profile_file = Path(self.temp_dir) / 'custom.yaml'
        self.assertFalse(profile_file.exists())
    
    def test_delete_nonexistent_profile(self):
        """Test deleting a non-existent profile."""
        result = delete_custom_profile('nonexistent')
        
        self.assertFalse(result)


class TestListProfiles(unittest.TestCase):
    """Test list_profiles function."""
    
    def test_list_profiles(self):
        """Test listing all profiles."""
        profiles = list_profiles()
        
        # Should include all predefined profiles
        self.assertIn('quick', profiles)
        self.assertIn('normal', profiles)
        self.assertIn('thorough', profiles)
        self.assertIn('stealth', profiles)
        
        # Check count (4 predefined profiles minimum)
        self.assertGreaterEqual(len(profiles), 4)


class TestPortRange(unittest.TestCase):
    """Test port range parsing."""
    
    def test_top100(self):
        """Test top100 port range."""
        ports = get_ports_from_range('top100')
        
        self.assertEqual(ports, TOP_100_PORTS)
        self.assertEqual(len(ports), 100)
    
    def test_top1000(self):
        """Test top1000 port range."""
        ports = get_ports_from_range('top1000')
        
        self.assertEqual(len(ports), 1000)
        self.assertEqual(ports[0], 1)
        self.assertEqual(ports[-1], 1000)
    
    def test_numeric_range(self):
        """Test numeric port range."""
        ports = get_ports_from_range('1-100')
        
        self.assertEqual(len(ports), 100)
        self.assertEqual(ports[0], 1)
        self.assertEqual(ports[-1], 100)
    
    def test_single_port(self):
        """Test single port."""
        ports = get_ports_from_range('80')
        
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0], 80)
    
    def test_invalid_range(self):
        """Test invalid port range (should default to top1000)."""
        ports = get_ports_from_range('invalid')
        
        # Should default to top1000
        self.assertEqual(len(ports), 1000)


if __name__ == '__main__':
    unittest.main()
