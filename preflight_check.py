#!/usr/bin/env python3
"""
Pre-flight check for TUI dashboard.
Verifies all components work before launching the full TUI.
"""

import sys

def test_imports():
    """Test all required imports."""
    print("🔍 Testing imports...")
    try:
        from netscan.tui import TuiApp
        from netscan.tui_views import ViewManager
        from netscan.dashboard_views import DashboardView, HostListView, DetailView
        from netscan.activity import ActivityFeed
        from netscan.stats import NetworkStats, DeviceCategorizer
        from netscan.tui_widgets import (
            NetworkHealthWidget,
            DeviceBreakdownWidget,
            TopServicesWidget,
            ActivityFeedWidget,
            NetworkTrafficWidget,
            QuickActionsBar
        )
        from netscan.scanner import get_service_name
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_service_mapping():
    """Test service name mapping."""
    print("\n🔍 Testing service mapping...")
    try:
        from netscan.scanner import get_service_name
        
        tests = [
            (22, 'ssh'),
            (80, 'http'),
            (443, 'https'),
            (12345, 'port-12345')
        ]
        
        for port, expected in tests:
            result = get_service_name(port)
            assert result == expected, f"Port {port}: expected {expected}, got {result}"
            print(f"  ✅ Port {port} → {result}")
        
        return True
    except Exception as e:
        print(f"  ❌ Service mapping failed: {e}")
        return False

def test_device_categorization():
    """Test device categorization with edge cases."""
    print("\n🔍 Testing device categorization...")
    try:
        from netscan.stats import DeviceCategorizer
        
        tests = [
            ({'hostname': None, 'mac': 'aa:bb:cc:dd:ee:ff'}, 'unknown'),
            ({'hostname': '', 'mac': '11:22:33:44:55:66'}, 'unknown'),
            ({'hostname': 'macbook-pro.local', 'mac': '22:33:44:55:66:77'}, 'computer'),
            ({'hostname': 'iphone-12', 'mac': '33:44:55:66:77:88'}, 'phone'),
        ]
        
        for host, expected in tests:
            result = DeviceCategorizer.categorize(host)
            assert result == expected, f"Host {host}: expected {expected}, got {result}"
            hostname = host['hostname'] if host['hostname'] else 'None/Empty'
            print(f"  ✅ {hostname} → {result}")
        
        return True
    except Exception as e:
        print(f"  ❌ Device categorization failed: {e}")
        return False

def test_view_system():
    """Test view manager initialization."""
    print("\n🔍 Testing view system...")
    try:
        from netscan.tui_views import ViewManager
        from netscan.dashboard_views import DashboardView, HostListView, DetailView
        
        vm = ViewManager()
        vm.register_view(HostListView())
        vm.register_view(DashboardView())
        vm.register_view(DetailView())
        
        assert len(vm.views) == 3, f"Expected 3 views, got {len(vm.views)}"
        assert vm.current_view == 'hosts', f"Expected 'hosts', got {vm.current_view}"
        
        # Test view switching
        vm.switch_to('dashboard', None)
        assert vm.current_view == 'dashboard'
        
        # Test tab bar generation
        tab_bar = vm.get_view_tabs()
        assert '[F1]' in tab_bar
        assert '[F2]' in tab_bar
        assert '[F3]' in tab_bar
        
        print(f"  ✅ ViewManager initialized with {len(vm.views)} views")
        print(f"  ✅ View switching works")
        print(f"  ✅ Tab bar: {tab_bar[:50]}...")
        
        return True
    except Exception as e:
        print(f"  ❌ View system failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_activity_feed():
    """Test activity feed."""
    print("\n🔍 Testing activity feed...")
    try:
        from netscan.activity import ActivityFeed
        
        feed = ActivityFeed()
        feed.add('scan', 'Test scan started', severity='info')
        feed.add('scan', 'Test scan complete', severity='success')
        feed.add('export', 'Test export failed', severity='error')
        
        events = feed.get_recent(10)
        assert len(events) == 3, f"Expected 3 events, got {len(events)}"
        
        print(f"  ✅ ActivityFeed created and populated")
        print(f"  ✅ {len(events)} events tracked")
        
        return True
    except Exception as e:
        print(f"  ❌ Activity feed failed: {e}")
        return False

def test_network_stats():
    """Test network statistics calculation."""
    print("\n🔍 Testing network statistics...")
    try:
        from netscan.stats import NetworkStats
        
        test_hosts = [
            {'ip': '192.168.1.1', 'up': True, 'latency_ms': 5.0, 'hostname': 'router.local'},
            {'ip': '192.168.1.2', 'up': True, 'latency_ms': 10.0, 'hostname': None},
            {'ip': '192.168.1.3', 'up': False, 'latency_ms': None, 'hostname': ''},
        ]
        
        health = NetworkStats.calculate_health_score(test_hosts)
        assert 0 <= health <= 100, f"Health score {health} out of range"
        
        devices = NetworkStats.get_device_breakdown(test_hosts)
        assert isinstance(devices, dict), "Device breakdown should be a dict"
        
        print(f"  ✅ Health score: {health:.1f}/100")
        print(f"  ✅ Device breakdown: {sum(devices.values())} devices categorized")
        
        return True
    except Exception as e:
        print(f"  ❌ Network stats failed: {e}")
        return False

def test_tui_initialization():
    """Test TUI app initialization."""
    print("\n🔍 Testing TUI initialization...")
    try:
        from netscan.tui import TuiApp
        
        app = TuiApp()
        
        assert hasattr(app, 'view_manager'), "TuiApp missing view_manager"
        assert hasattr(app, 'activity_feed'), "TuiApp missing activity_feed"
        assert len(app.view_manager.views) == 3, f"Expected 3 views, got {len(app.view_manager.views)}"
        
        print(f"  ✅ TuiApp initialized successfully")
        print(f"  ✅ ViewManager: {list(app.view_manager.views.keys())}")
        print(f"  ✅ Current view: {app.view_manager.current_view}")
        print(f"  ✅ ActivityFeed ready")
        
        return True
    except Exception as e:
        print(f"  ❌ TUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all pre-flight checks."""
    print("=" * 60)
    print("TUI Dashboard Pre-Flight Check")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_service_mapping,
        test_device_categorization,
        test_view_system,
        test_activity_feed,
        test_network_stats,
        test_tui_initialization,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\n🚀 TUI is ready to launch!")
        print("\nRun: python3 -m netscan.tui")
        return 0
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total})")
        print("\n⚠️  Fix errors before running TUI")
        return 1

if __name__ == '__main__':
    sys.exit(main())
