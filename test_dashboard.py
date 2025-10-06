#!/usr/bin/env python3
"""Quick test to verify dashboard integration."""

from netscan.tui_views import ViewManager
from netscan.dashboard_views import DashboardView, HostListView, DetailView
from netscan.activity import ActivityFeed
from netscan.stats import NetworkStats

# Test view system
view_manager = ViewManager()
view_manager.register_view(HostListView())
view_manager.register_view(DashboardView())
view_manager.register_view(DetailView())

print("✅ Views registered successfully")
print(f"   Current view: {view_manager.current_view}")
print(f"   Available views: {list(view_manager.views.keys())}")

# Test tab bar generation
tab_bar = view_manager.get_view_tabs()
print(f"\n✅ Tab bar: {tab_bar}")

# Test activity feed
activity = ActivityFeed()
activity.add("test", "Test info event", severity="info")
activity.add("test", "Test success event", severity="success")
activity.add("test", "Test warning event", severity="warning")
activity.add("test", "Test error event", severity="error")

events = activity.get_recent(10)
print(f"\n✅ Activity feed: {len(events)} events")
for event in events:
    print(f"   [{event.severity}] {event.message}")

# Test network stats
test_hosts = [
    {'ip': '192.168.1.1', 'up': True, 'latency_ms': 5.0, 'mac': 'aa:bb:cc:dd:ee:ff'},
    {'ip': '192.168.1.2', 'up': True, 'latency_ms': 10.0, 'mac': '11:22:33:44:55:66'},
    {'ip': '192.168.1.3', 'up': False, 'latency_ms': None, 'mac': None},
]

health = NetworkStats.calculate_health_score(test_hosts)
devices = NetworkStats.get_device_breakdown(test_hosts)
up_count = sum(1 for h in test_hosts if h.get('up'))
latencies = [h.get('latency_ms') for h in test_hosts if h.get('up') and h.get('latency_ms')]
avg_latency = sum(latencies) / len(latencies) if latencies else 0

print(f"\n✅ Network health: {health:.1f}/100")
print(f"   UP: {up_count}/{len(test_hosts)}")
print(f"   Avg latency: {avg_latency:.2f}ms")
print(f"   Device types: {devices}")

print("\n🎉 All dashboard components working!")
