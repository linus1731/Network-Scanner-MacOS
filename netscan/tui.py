from __future__ import annotations

import curses
import time
import threading
import textwrap
import socket
import json
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from .netinfo import get_default_interface, get_local_network_cidr
from .traffic import get_bytes_counters
from .scanner import scan_cidr, port_scan, expand_targets
from .resolve import resolve_ptrs
from .arp import get_arp_table
from .export import export_to_csv, export_to_markdown, export_to_html
from .ratelimit import get_global_limiter
from .profiles import (
    get_profile,
    list_profiles,
    ScanProfile,
    PREDEFINED_PROFILES,
    get_ports_from_range
)
from .tui_views import ViewManager
from .dashboard_views import DashboardView, HostListView, DetailView
from .activity import ActivityFeed


class TuiApp:
    def __init__(self) -> None:
        self.iface = get_default_interface() or "en0"
        self.cidr = get_local_network_cidr() or "192.168.1.0/24"
        self.stop = False
        self.rx_prev = None
        self.tx_prev = None
        self.rx_rate = 0.0
        self.tx_rate = 0.0
        self.rate_lock = threading.Lock()
        self.scan_results: List[dict] = []
        self.scan_lock = threading.Lock()
        self.scanning = False
        self.last_scan_ts: Optional[float] = None
        # UI state
        self.only_up = False  # Changed to False to show all hosts by default
        self.sel = 0
        self.rx_hist: List[float] = []
        self.tx_hist: List[float] = []
        # sorting state
        self.sort_by = "ip"  # one of: ip, status, latency, hostname, mac
        self.sort_desc = False
        # port scan panel
        self.portscan_target: Optional[str] = None
        self.portscan_open: List[int] = []
        self.portscan_running = False
        # Persistent cache with TTL: ip -> (ports, timestamp)
        self.portscan_cache: Dict[str, Tuple[List[int], float]] = {}
        self.portscan_current_port: Optional[int] = None  # Current port being scanned
        self.cache_ttl = 3600  # Cache TTL in seconds (1 hour default)
        self.cache_file = Path.home() / ".netscan_cache.json"
        # details overlay
        self.detail_active = False
        self.detail_ip: Optional[str] = None
        # auto scan on first launch
        self.auto_scan_started = False
        # map ip -> index in scan_results for fast merge
        self._ip_index: dict[str, int] = {}
        # export state
        self.export_message: Optional[str] = None
        self.export_message_time: Optional[float] = None
        self.export_message_color: int = 1  # 1=green, 2=red
        # scan progress
        self.scan_current_host: Optional[str] = None  # Currently scanning host
        # scan profile
        self.active_profile: ScanProfile = PREDEFINED_PROFILES['normal']  # Default to normal profile
        
        # rate limiting
        self.rate_limiter = get_global_limiter()
        self.rate_limit_enabled = False  # Start with no limit
        
        # View system and activity feed
        self.view_manager = ViewManager()
        self.activity_feed = ActivityFeed()
        
        # Register views (hosts first so it's the default)
        self.view_manager.register_view(HostListView())
        self.view_manager.register_view(DashboardView())
        self.view_manager.register_view(DetailView())
        
        # Load persistent cache
        self._load_cache()

    def _load_cache(self) -> None:
        """Load port scan cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Filter expired entries
                    now = time.time()
                    self.portscan_cache = {
                        ip: (ports, ts)
                        for ip, (ports, ts) in data.items()
                        if now - ts < self.cache_ttl
                    }
        except Exception:
            self.portscan_cache = {}
    
    def _save_cache(self) -> None:
        """Save port scan cache to disk."""
        try:
            # Only save non-expired entries
            now = time.time()
            data = {
                ip: (ports, ts)
                for ip, (ports, ts) in self.portscan_cache.items()
                if now - ts < self.cache_ttl
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass
    
    def _clear_cache(self) -> None:
        """Clear all cache entries."""
        self.portscan_cache = {}
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception:
            pass
    
    def _clear_expired_cache(self) -> None:
        """Remove expired cache entries."""
        now = time.time()
        expired = [
            ip for ip, (_, ts) in self.portscan_cache.items()
            if now - ts >= self.cache_ttl
        ]
        for ip in expired:
            del self.portscan_cache[ip]

    def _update_rates(self) -> None:
        while not self.stop:
            counters = get_bytes_counters(self.iface)
            if counters is not None:
                rx, tx = counters
                if self.rx_prev is not None and self.tx_prev is not None:
                    dt = max(0.001, 1.0)
                    with self.rate_lock:
                        self.rx_rate = max(0.0, (rx - self.rx_prev) / dt)
                        self.tx_rate = max(0.0, (tx - self.tx_prev) / dt)
                        # history
                        self.rx_hist.append(self.rx_rate)
                        self.tx_hist.append(self.tx_rate)
                        # cap history
                        max_len = 600
                        if len(self.rx_hist) > max_len:
                            self.rx_hist = self.rx_hist[-max_len:]
                        if len(self.tx_hist) > max_len:
                            self.tx_hist = self.tx_hist[-max_len:]
                self.rx_prev, self.tx_prev = rx, tx
            time.sleep(1.0)

    def _scan(self) -> None:
        # Start a scan and enrich results incrementally
        self.scanning = True
        self.scan_current_host = None
        
        # Add activity event for scan start
        self.activity_feed.add(
            event_type="scan",
            message=f"Scan started: {self.cidr} (profile: {self.active_profile.name})",
            severity="info"
        )
        
        with self.scan_lock:
            # Pre-fill all hosts in the CIDR so every IP is visible immediately
            ips_all = expand_targets(self.cidr)
            self.scan_results = [
                {"ip": ip, "up": False, "latency_ms": None, "hostname": None, "mac": None}
                for ip in ips_all
            ]
            self._ip_index = {ip: i for i, ip in enumerate(ips_all)}
        
        # Use profile settings for scan
        concurrency = self.active_profile.concurrency
        timeout = self.active_profile.timeout
        
        # Single scan pass with batched enrichment
        batch: List[dict] = []
        for r in scan_cidr(self.cidr, concurrency=concurrency, timeout=timeout, count=1, tcp_fallback=True):
            self.scan_current_host = r.get('ip')  # Update current host
            batch.append(r)
            if len(batch) >= 32:
                self._enrich_and_store(batch)
                batch = []
        if batch:
            self._enrich_and_store(batch)
        self.scan_current_host = None  # Clear after scan complete
        self.last_scan_ts = time.time()
        self.scanning = False
        
        # Add activity event for scan complete
        with self.scan_lock:
            total = len(self.scan_results)
            up = sum(1 for r in self.scan_results if r.get('up'))
        self.activity_feed.add(
            event_type="scan",
            message=f"Scan complete: {up}/{total} hosts up",
            severity="success"
        )

    def _portscan_worker(self, ip: str) -> None:
        # Check cache first (with TTL validation)
        if ip in self.portscan_cache:
            ports, ts = self.portscan_cache[ip]
            age = time.time() - ts
            if age < self.cache_ttl:
                # Cache is still valid
                self.portscan_open = ports
                self.portscan_running = False
                return
            else:
                # Cache expired, remove it
                del self.portscan_cache[ip]
        
        # Get ports from active profile
        ports = get_ports_from_range(self.active_profile.port_range)
        self.portscan_current_port = 0
        try:
            # Use the fast concurrent port_scan function
            openp = port_scan(ip, ports, concurrency=256, timeout=0.5)
            # Simulate progress by updating current_port during scan
            # (The actual scan is too fast to show individual ports, but we track total)
        except Exception:
            openp = []
        
        self.portscan_open = openp
        self.portscan_cache[ip] = (openp, time.time())  # Cache results with timestamp
        self._save_cache()  # Persist to disk
        self.portscan_current_port = None
        self.portscan_running = False

    def _show_export_dialog(self, stdscr) -> None:
        """Show export dialog and handle exports in multiple formats."""
        h, w = stdscr.getmaxyx()
        
        # Dialog dimensions
        dialog_h = 18
        dialog_w = min(75, w - 10)
        start_y = (h - dialog_h) // 2
        start_x = (w - dialog_w) // 2
        
        # Create dialog window
        try:
            dialog = curses.newwin(dialog_h, dialog_w, start_y, start_x)
        except curses.error:
            self.export_message = "❌ Screen too small for export dialog"
            self.export_message_color = 2
            self.export_message_time = time.time()
            return
        
        dialog.box()
        
        # Dialog state
        formats = ["CSV", "Markdown", "HTML"]
        selected_format = 0
        include_down = False
        filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cursor_pos = len(filename) - 4  # Position before extension
        
        def update_extension():
            nonlocal filename, cursor_pos
            base = filename.rsplit('.', 1)[0]
            ext = {0: 'csv', 1: 'md', 2: 'html'}[selected_format]
            filename = f"{base}.{ext}"
            cursor_pos = min(cursor_pos, len(filename) - len(ext) - 1)
        
        def refresh_dialog():
            dialog.erase()
            dialog.box()
            
            # Title
            title = " Export Scan Results "
            try:
                dialog.addstr(0, (dialog_w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))
            except curses.error:
                pass
            
            # Instructions
            try:
                dialog.addstr(2, 2, "Format:", curses.A_BOLD)
                # Show format options
                for i, fmt in enumerate(formats):
                    marker = "●" if i == selected_format else "○"
                    attr = curses.A_BOLD | curses.color_pair(4) if i == selected_format else curses.A_NORMAL
                    dialog.addstr(3, 4 + i * 15, f"{marker} {fmt}", attr)
                
                dialog.addstr(5, 2, "Filename:", curses.A_BOLD)
                dialog.addstr(6, 2, f" {filename}", curses.A_NORMAL)
                # Show cursor
                try:
                    dialog.addstr(6, 3 + cursor_pos, "", curses.A_REVERSE)
                except curses.error:
                    pass
                
                dialog.addstr(8, 2, "Options:", curses.A_BOLD)
                check = "[X]" if include_down else "[ ]"
                dialog.addstr(9, 2, f" {check} Include DOWN hosts")
                
                # Stats
                with self.scan_lock:
                    total = len(self.scan_results)
                    up_count = sum(1 for r in self.scan_results if r.get('up'))
                    down_count = total - up_count
                
                dialog.addstr(11, 2, "Preview:", curses.A_BOLD)
                if include_down:
                    dialog.addstr(12, 2, f" → Exporting {total} hosts ({up_count} UP, {down_count} DOWN)")
                else:
                    dialog.addstr(12, 2, f" → Exporting {up_count} hosts (UP only)")
                
                # Controls
                dialog.addstr(14, 2, "Controls:", curses.A_DIM)
                dialog.addstr(15, 2, " [Tab] Switch format  [Enter] Export  [Space] Options", curses.A_DIM)
                dialog.addstr(16, 2, " [Esc] Cancel", curses.A_DIM)
                
            except curses.error:
                pass
            
            dialog.refresh()
        
        # Dialog loop
        curses.curs_set(1)  # Show cursor
        dialog.nodelay(False)  # Blocking mode
        dialog.keypad(True)
        
        while True:
            refresh_dialog()
            
            try:
                ch = dialog.getch()
            except Exception:
                break
            
            if ch == 27:  # Esc
                break
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter - Export
                # Perform export
                try:
                    with self.scan_lock:
                        results = self.scan_results[:]
                    
                    # Convert to export format
                    hosts_dict = []
                    for r in results:
                        hosts_dict.append({
                            'ip': r.get('ip', ''),
                            'status': 'UP' if r.get('up') else 'DOWN',
                            'latency': r.get('latency_ms'),
                            'hostname': r.get('hostname'),
                            'mac': r.get('mac'),
                            'vendor': r.get('vendor'),
                            'ports': self.portscan_open if r.get('ip') == self.portscan_target else []
                        })
                    
                    # Export based on selected format
                    if selected_format == 0:  # CSV
                        output_path = export_to_csv(hosts_dict, filename, include_down=include_down)
                    elif selected_format == 1:  # Markdown
                        output_path = export_to_markdown(hosts_dict, filename, include_down=include_down, use_emoji=True)
                    else:  # HTML
                        output_path = export_to_html(hosts_dict, filename, include_down=include_down)
                    
                    format_name = formats[selected_format]
                    self.export_message = f"✅ {format_name} exported to: {output_path}"
                    self.export_message_color = 1
                    
                    # Add activity event for successful export
                    export_count = up_count if not include_down else total
                    self.activity_feed.add(
                        event_type="export",
                        message=f"Exported {export_count} hosts to {format_name}: {output_path}",
                        severity="success"
                    )
                    
                except Exception as e:
                    self.export_message = f"❌ Export failed: {str(e)[:40]}"
                    self.export_message_color = 2
                    
                    # Add activity event for failed export
                    self.activity_feed.add(
                        event_type="export",
                        message=f"Export failed: {str(e)[:50]}",
                        severity="error"
                    )
                
                self.export_message_time = time.time()
                break
            
            elif ch == 9:  # Tab - Switch format
                selected_format = (selected_format + 1) % len(formats)
                update_extension()
                
            elif ch == ord(' '):  # Space - Toggle include_down
                include_down = not include_down
                
            elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 8:
                if cursor_pos > 0:
                    filename = filename[:cursor_pos-1] + filename[cursor_pos:]
                    cursor_pos -= 1
                    
            elif ch == curses.KEY_DC:  # Delete
                if cursor_pos < len(filename):
                    filename = filename[:cursor_pos] + filename[cursor_pos+1:]
                    
            elif ch == curses.KEY_LEFT:
                if cursor_pos > 0:
                    cursor_pos -= 1
                    
            elif ch == curses.KEY_RIGHT:
                if cursor_pos < len(filename):
                    cursor_pos += 1
                    
            elif ch == curses.KEY_HOME:
                cursor_pos = 0
                
            elif ch == curses.KEY_END:
                cursor_pos = len(filename)
                
            elif 32 <= ch <= 126:  # Printable characters
                char = chr(ch)
                filename = filename[:cursor_pos] + char + filename[cursor_pos:]
                cursor_pos += 1
        
        curses.curs_set(0)  # Hide cursor again
        stdscr.nodelay(True)  # Back to non-blocking
    
    def _show_profile_dialog(self, stdscr) -> None:
        """Show profile selection dialog."""
        h, w = stdscr.getmaxyx()
        
        # Get all available profiles
        all_profiles = list_profiles()
        profile_list = []
        
        # Add predefined profiles first
        for name in ['quick', 'normal', 'thorough', 'stealth']:
            if name in all_profiles:
                profile_list.append((name, all_profiles[name], 'predefined'))
        
        # Add custom profiles
        for name, profile in all_profiles.items():
            if name not in PREDEFINED_PROFILES:
                profile_list.append((name, profile, 'custom'))
        
        # Find currently selected profile
        selected_idx = 0
        for i, (name, profile, ptype) in enumerate(profile_list):
            if name == self.active_profile.name:
                selected_idx = i
                break
        
        # Dialog dimensions
        dialog_h = min(20, h - 4)
        dialog_w = min(80, w - 10)
        start_y = (h - dialog_h) // 2
        start_x = (w - dialog_w) // 2
        
        # Create dialog window
        try:
            dialog = curses.newwin(dialog_h, dialog_w, start_y, start_x)
        except curses.error:
            self.export_message = "❌ Screen too small for profile dialog"
            self.export_message_color = 2
            self.export_message_time = time.time()
            return
        
        dialog.box()
        dialog.keypad(True)
        
        def refresh_dialog():
            dialog.erase()
            dialog.box()
            
            # Title
            title = " Select Scan Profile "
            try:
                dialog.addstr(0, (dialog_w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))
            except curses.error:
                pass
            
            # Instructions
            try:
                dialog.addstr(2, 2, "Available Profiles:", curses.A_BOLD)
                
                # List profiles (with scrolling if needed)
                max_visible = dialog_h - 8
                start_idx = max(0, min(selected_idx - max_visible // 2, len(profile_list) - max_visible))
                end_idx = min(len(profile_list), start_idx + max_visible)
                
                for i in range(start_idx, end_idx):
                    name, profile, ptype = profile_list[i]
                    y = 3 + (i - start_idx)
                    
                    # Selection marker
                    marker = "●" if i == selected_idx else "○"
                    
                    # Color based on type and selection
                    if i == selected_idx:
                        attr = curses.A_BOLD | curses.color_pair(4)
                    elif ptype == 'predefined':
                        attr = curses.color_pair(2) if name == 'quick' else curses.color_pair(1)
                    else:
                        attr = curses.color_pair(3)
                    
                    # Profile line
                    profile_line = f"{marker} {name:<12} - {profile.description[:40]}"
                    dialog.addstr(y, 2, profile_line[:dialog_w-4], attr)
                
                # Selected profile details
                if profile_list:
                    _, selected_profile, _ = profile_list[selected_idx]
                    details_y = dialog_h - 5
                    
                    dialog.addstr(details_y, 2, "Details:", curses.A_DIM)
                    dialog.addstr(details_y + 1, 2, f" Concurrency: {selected_profile.concurrency}  Timeout: {selected_profile.timeout}s  Ports: {selected_profile.port_range}", curses.A_DIM)
                    if selected_profile.rate_limit:
                        dialog.addstr(details_y + 2, 2, f" Rate Limit: {selected_profile.rate_limit} pkts/s  Random Delay: {selected_profile.min_delay}-{selected_profile.max_delay}s", curses.A_DIM)
                
                # Controls
                dialog.addstr(dialog_h - 2, 2, "[↑↓] Navigate  [Enter] Select  [Esc] Cancel", curses.A_DIM)
                
            except curses.error:
                pass
            
            dialog.refresh()
        
        # Dialog loop
        dialog.nodelay(False)  # Blocking mode
        
        while True:
            refresh_dialog()
            
            try:
                ch = dialog.getch()
            except Exception:
                break
            
            if ch == 27:  # Esc
                break
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter - Select profile
                if profile_list:
                    name, profile, _ = profile_list[selected_idx]
                    self.active_profile = profile
                    self.export_message = f"✅ Profile changed to: {name}"
                    self.export_message_color = 1
                    self.export_message_time = time.time()
                    
                    # Add activity event for profile change
                    self.activity_feed.add(
                        event_type="profile",
                        message=f"Profile changed to: {name}",
                        severity="info"
                    )
                break
            elif ch == curses.KEY_UP:
                if selected_idx > 0:
                    selected_idx -= 1
            elif ch == curses.KEY_DOWN:
                if selected_idx < len(profile_list) - 1:
                    selected_idx += 1
            elif ch == curses.KEY_HOME:
                selected_idx = 0
            elif ch == curses.KEY_END:
                selected_idx = len(profile_list) - 1
        
        stdscr.nodelay(True)  # Back to non-blocking

    def _open_detail_for_selected(self) -> None:
        with self.scan_lock:
            rows = self.scan_results[:]
        if self.only_up:
            rows = [r for r in rows if r.get('up')]
        if not rows:
            return
        idx = max(0, min(self.sel, len(rows) - 1))
        target_ip = rows[idx]['ip']
        self.detail_active = True
        self.detail_ip = target_ip
        # kick off a port scan automatically
        self.portscan_target = target_ip
        self.portscan_open = []
        self.portscan_running = True
        threading.Thread(target=self._portscan_worker, args=(target_ip,), daemon=True).start()

    def _enrich_and_store(self, batch: List[dict]) -> None:
        ips = [r["ip"] for r in batch]
        ptr = resolve_ptrs(ips)
        arp_map = get_arp_table()
        for r in batch:
            r["hostname"] = ptr.get(r["ip"]) or None
            r["mac"] = arp_map.get(r["ip"]) or None
        # Merge into pre-filled list by IP
        with self.scan_lock:
            for r in batch:
                ip = r["ip"]
                idx = self._ip_index.get(ip)
                if idx is not None and 0 <= idx < len(self.scan_results):
                    # update fields
                    self.scan_results[idx].update(r)
                else:
                    # if not pre-filled (range change), append
                    self._ip_index[ip] = len(self.scan_results)
                    self.scan_results.append(r)

    def draw(self, stdscr) -> None:
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(250)

        # Launch background rate updater
        t = threading.Thread(target=self._update_rates, daemon=True)
        t.start()

        # Colors
        use_colors = False
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Pair indices
            curses.init_pair(1, curses.COLOR_GREEN, -1)  # up
            curses.init_pair(2, curses.COLOR_RED, -1)    # down
            curses.init_pair(3, curses.COLOR_CYAN, -1)   # ip
            curses.init_pair(4, curses.COLOR_YELLOW, -1) # header/help
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)# graph RX
            curses.init_pair(7, curses.COLOR_BLUE, -1)   # graph TX
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # selection highlight
            use_colors = True

        def cpair(n):
            return curses.color_pair(n) if use_colors else 0

        def smooth(series: List[float], window: int = 4) -> List[float]:
            if window <= 1 or len(series) <= 2:
                return series[-width:] if 'width' in locals() else series
            # simple moving average
            w = min(window, len(series))
            out: List[float] = []
            acc = 0.0
            q: List[float] = []
            for v in series:
                q.append(v)
                acc += v
                if len(q) > w:
                    acc -= q.pop(0)
                out.append(acc / len(q))
            return out

        def sparkline(series: List[float], width: int, smooth_window: int = 4) -> str:
            # Simple 8-level sparkline using unicode blocks
            if width <= 0:
                return ""
            if not series:
                return " " * width
            # Take last 'width' samples and normalize
            data_src = series[-max(width, 20):]  # take a bit more for smoothing
            data = smooth(data_src, smooth_window)[-width:]
            maxv = max(data) or 1.0
            blocks = "▁▂▃▄▅▆▇█"
            out = []
            for v in data[-width:]:
                lvl = int(round((len(blocks) - 1) * (v / maxv)))
                out.append(blocks[min(len(blocks) - 1, max(0, lvl))])
            return "".join(out).ljust(width)

        while not self.stop:
            h, w = stdscr.getmaxyx()
            stdscr.erase()

            # Auto-start a scan once on first launch
            if not self.scanning and not self.auto_scan_started:
                self.auto_scan_started = True
                threading.Thread(target=self._scan, daemon=True).start()

            # Top: Traffic
            with self.rate_lock:
                rx = self.rx_rate
                tx = self.tx_rate
            def fmt(bps: float) -> str:
                units = ["B/s", "KB/s", "MB/s", "GB/s"]
                i = 0
                while bps >= 1024 and i < len(units)-1:
                    bps /= 1024.0
                    i += 1
                return f"{bps:6.1f} {units[i]}"

            # Get rate limit info
            rate_info = ""
            if self.rate_limit_enabled:
                stats = self.rate_limiter.get_stats()
                rate = stats.get('rate', 0)
                if rate and rate > 0:
                    throttle_pct = stats.get('throttle_percentage', 0)
                    throttle_indicator = "🔥" if throttle_pct > 10 else "⚡" if throttle_pct > 0 else "✓"
                    rate_info = f"  rate={rate}/s {throttle_indicator}"
                else:
                    rate_info = "  rate=∞"
            
            title = f"netscan-tui  iface={self.iface}  net={self.cidr}  profile={self.active_profile.name}{rate_info}  rx={fmt(rx)}  tx={fmt(tx)}  filter={'UP' if self.only_up else 'ALL'}  sort={self.sort_by}{'↓' if self.sort_desc else '↑'}  cache={len(self.portscan_cache)}"
            stdscr.addstr(0, 0, title[: max(0, w - 1)], curses.A_BOLD | cpair(4))

            # Help line
            help_line = "[s]can  [r]efresh  [P]rofile  [+/-] rate  [a]ctive-only  [e]xport  [C]lear cache  [1-5] sort  [o]cycle  [O]asc/desc  [p]orts  ↑/↓ select  [q]uit"
            stdscr.addstr(1, 0, help_line[: max(0, w - 1)], curses.A_DIM | cpair(4))

            # View tabs (F1-F3)
            tab_bar = self.view_manager.get_view_tabs()
            stdscr.addstr(2, 0, tab_bar[: max(0, w - 1)], cpair(3) | curses.A_BOLD)

            # Check if we're in dashboard view - if so, delegate to view manager
            current_view = self.view_manager.get_current_view()
            if current_view and current_view.name in ['dashboard', 'details']:
                # These views handle their own drawing entirely
                self.view_manager.draw(stdscr, self)
                # Skip the rest of the traditional drawing
                stdscr.refresh()
                ch = stdscr.getch()
                
                # Handle view switching first
                if ch == curses.KEY_F1 or ch == 265:  # F1 - Dashboard
                    self.view_manager.switch_to('dashboard', self)
                    continue
                elif ch == curses.KEY_F2 or ch == 266:  # F2 - Host List
                    self.view_manager.switch_to('hosts', self)
                    continue
                elif ch == curses.KEY_F3 or ch == 267:  # F3 - Details
                    self.view_manager.switch_to('details', self)
                    continue
                elif ch == 9:  # Tab - cycle next
                    self.view_manager.cycle_next(self)
                    continue
                elif ch == 353:  # Shift+Tab - cycle prev (KEY_BTAB)
                    self.view_manager.cycle_prev(self)
                    continue
                
                # Let view handle other input
                if current_view.handle_input(ch, self):
                    continue
                
                # Fall through to global handlers
                if ch == ord('q'):
                    break
                continue

            # For 'hosts' view, render using legacy table code
            # Graph lines: RX and TX sparklines
            # Build prettier graphs: labels + current + spark + max scale
            # determine dynamic widths based on window
            rx_label = f"RX {fmt(rx)}  "
            tx_label = f"TX {fmt(tx)}  "
            with self.rate_lock:
                rx_max = max(self.rx_hist[-300:] or [0.0])
                tx_max = max(self.tx_hist[-300:] or [0.0])
            rx_right = f"  max {fmt(rx_max)}"
            tx_right = f"  max {fmt(tx_max)}"
            # compute spark width
            rx_prefix_len = len(rx_label)
            tx_prefix_len = len(tx_label)
            rx_suffix_len = len(rx_right)
            tx_suffix_len = len(tx_right)
            rx_w = max(10, w - rx_prefix_len - rx_suffix_len - 1)
            tx_w = max(10, w - tx_prefix_len - tx_suffix_len - 1)
            with self.rate_lock:
                rx_line = sparkline(self.rx_hist, rx_w)
                tx_line = sparkline(self.tx_hist, tx_w)
            # RX line in magenta, TX in blue
            stdscr.addstr(2, 0, (rx_label + rx_line + rx_right)[: max(0, w - 1)], cpair(5))
            stdscr.addstr(3, 0, (tx_label + tx_line + tx_right)[: max(0, w - 1)], cpair(7))

            # Determine LEFT-side details panel geometry (always visible)
            panel_active = True
            # Calculate panel width: minimum 45, maximum 70, about 1/3 of screen
            panel_w = max(45, min(70, w // 3))
            # Ensure enough space for the table (minimum 50 columns)
            if w - panel_w - 2 < 50:
                panel_w = max(40, w - 52)
            # Never make it negative or too small
            if panel_w < 40:
                panel_w = 40
            # If screen is too narrow, use half
            if w < 100:
                panel_w = max(35, w // 2)

            # Scan area header (for right side)
            header_y = 5
            table_x = panel_w + 1  # Start table after panel
            with self.scan_lock:
                progress = len(self.scan_results)
                up_count = sum(1 for r in self.scan_results if r.get('up'))
            
            # Show scan status with current host
            if self.scanning and self.scan_current_host:
                state = f'scanning {self.scan_current_host}'
            elif self.scanning:
                state = 'running'
            else:
                state = 'idle'
            
            stdscr.addstr(header_y, table_x, f"Scan results ({state})  hosts={progress}", curses.A_BOLD)
            # Header with sort indicators at fixed columns (relative to table_x)
            col_ip = table_x
            col_status = table_x + 17
            col_latency = table_x + 26
            col_host = table_x + 37
            def col_title(name: str, key: str) -> str:
                if self.sort_by == key:
                    return f"{name} {'↓' if self.sort_desc else '↑'}"
                return name
            header_line = (
                f"{col_title('IP', 'ip'):<15}  "
                f"{col_title('Status', 'status'):<6}  "
                f"{col_title('Latency', 'latency'):<8}  "
                f"{col_title('Hostname', 'hostname'):<20}  "
            )
            stdscr.addstr(header_y + 1, table_x, header_line[: max(0, w - table_x - 1)], curses.A_UNDERLINE)

            # Print results
            with self.scan_lock:
                rows = self.scan_results[:]
            # filter
            if self.only_up:
                rows = [r for r in rows if r.get("up")]
            # sorting
            def ip_key(ip: str) -> tuple:
                try:
                    return tuple(int(p) for p in ip.split("."))
                except Exception:
                    return (999, 999, 999, 999)
            def sort_key(r: dict):
                k = self.sort_by
                if k == "ip":
                    return ip_key(r.get("ip", "255.255.255.255"))
                if k == "status":
                    # up first when descending=False => invert bool accordingly
                    return (0 if r.get("up") else 1)
                if k == "latency":
                    lat = r.get("latency_ms")
                    return (float("inf") if lat is None else lat)
                if k == "hostname":
                    return (r.get("hostname") or "").lower()
                if k == "mac":
                    return (r.get("mac") or "zz:zz:zz:zz:zz:zz").lower()
                return ip_key(r.get("ip", "255.255.255.255"))
            rows.sort(key=sort_key, reverse=self.sort_desc)
            # ensure selection bounds
            if rows:
                self.sel = max(0, min(self.sel, len(rows) - 1))
            else:
                self.sel = 0

            # Selected IP for right panel and auto-follow port scan when idle
            selected_ip: Optional[str] = rows[self.sel]['ip'] if rows else None
            if selected_ip and selected_ip != self.portscan_target and not self.portscan_running:
                self.portscan_target = selected_ip
                self.portscan_open = []
                self.portscan_running = True
                threading.Thread(target=self._portscan_worker, args=(selected_ip,), daemon=True).start()

            start_y = header_y + 2
            max_rows = max(0, h - start_y - 2)
            # basic scrolling when selection moves beyond viewport
            top_index = 0
            if self.sel >= max_rows:
                top_index = self.sel - max_rows + 1

            for i, r in enumerate(rows[top_index : top_index + max_rows]):
                y = start_y + i
                status_up = bool(r.get("up"))
                status = "UP" if status_up else "DOWN"
                lat = r.get("latency_ms")
                lat_s = f"{lat:.2f} ms" if lat is not None else "-"
                host = (r.get("hostname") or "-")[:20]
                line = f"{r['ip']:<15}  {status:<6}  {lat_s:<8}  {host:<20}"
                attrs = 0
                # colorize ip/status
                ip_col = cpair(3)
                st_col = cpair(1) if status_up else cpair(2)
                # selection highlight
                if top_index + i == self.sel:
                    attrs |= curses.A_REVERSE | cpair(6)
                # print with simple segmentation to colorize parts
                try:
                    stdscr.addstr(y, table_x, f"{r['ip']:<15}", ip_col | attrs)
                    stdscr.addstr(y, table_x + 17, f"{status:<6}", st_col | attrs)
                    stdscr.addstr(y, table_x + 26, f"{lat_s:<8}", attrs)
                    stdscr.addstr(y, table_x + 37, f"{host:<20}", attrs)
                except curses.error:
                    # If window too small, fallback to single write
                    content_w = max(0, w - table_x - 1)
                    stdscr.addstr(y, table_x, line[: content_w], attrs)

            # Portscan status is shown in the left panel; no bottom panel

            # LEFT-side details panel - ALWAYS SHOW IT
            if panel_active:
                panel_h = max(10, h - header_y)
                x0 = 0
                y0 = header_y
                # Safety clamp
                if panel_h > h - y0:
                    panel_h = h - y0
                if panel_h < 5:
                    panel_h = 5
                
                # Draw vertical separator
                try:
                    vch = getattr(curses, 'ACS_VLINE', ord('|'))
                    stdscr.vline(y0, panel_w, vch, min(panel_h, h - y0))
                except curses.error:
                    pass
                
                # Create and draw the panel window
                try:
                    win = curses.newwin(panel_h, panel_w, y0, x0)
                    win.box()
                    inner_w = max(10, panel_w - 2)
                    row = 1
                    
                    def put(line: str, attr: int = 0):
                        nonlocal row
                        if row >= panel_h - 1:
                            return
                        try:
                            display_line = line[:inner_w] if len(line) > inner_w else line
                            win.addstr(row, 1, display_line.ljust(inner_w), attr)
                        except curses.error:
                            pass
                        row += 1
                except Exception as e:
                    # If panel creation fails, show error on main screen
                    try:
                        err_msg = f"Panel ERR: {type(e).__name__} {str(e)[:20]}"
                        stdscr.addstr(header_y + 1, 0, err_msg, curses.A_DIM)
                    except:
                        pass
                else:

                    # Title
                    title = " ═══ HOST DETAILS ═══ "
                    try:
                        win.addstr(0, max(1, (panel_w - len(title)) // 2), title, curses.A_BOLD | cpair(4))
                    except curses.error:
                        pass

                    # Info for selected IP
                    info = None
                    target_ip = selected_ip
                    with self.scan_lock:
                        for r in self.scan_results:
                            if r.get('ip') == target_ip:
                                info = r
                                break
                    if info:
                        status_up = bool(info.get('up'))
                        status = "UP" if status_up else "DOWN"
                        status_col = cpair(1) if status_up else cpair(2)
                        lat = info.get('latency_ms')
                        lat_s = f"{lat:.2f} ms" if lat is not None else "-"
                        
                        # Format like in the screenshot - with nice spacing
                        put("")
                        put("┌─ Network Information", curses.A_BOLD | cpair(4))
                        put("│")
                        put(f"│ IP Address:", curses.A_BOLD)
                        put(f"│   {info.get('ip')}", cpair(3) | curses.A_BOLD)
                        put("│")
                        put(f"│ Hostname:", curses.A_BOLD)
                        hostname = info.get('hostname') or 'Not resolved'
                        put(f"│   {hostname}")
                        put("│")
                        put(f"│ MAC Address:", curses.A_BOLD)
                        mac = info.get('mac') or 'Unknown'
                        put(f"│   {mac}")
                        put("│")
                        put(f"│ Status:", curses.A_BOLD)
                        put(f"│   {status}", status_col | curses.A_BOLD)
                        put("│")
                        put(f"│ Latency:", curses.A_BOLD)
                        put(f"│   {lat_s}")
                        put("│")
                        put("└" + "─" * (inner_w - 1))
                        put("")
                        put("┌─ Open TCP Ports", curses.A_BOLD | cpair(4))
                        put("┌─ Open TCP Ports", curses.A_BOLD | cpair(4))
                    else:
                        put("")
                        put("┌─ Network Information", curses.A_BOLD | cpair(4))
                        put("│")
                        put(f"│ IP Address:", curses.A_BOLD)
                        put(f"│   {target_ip or '-'}", cpair(3))
                        put("│")
                        put(f"│ Hostname:", curses.A_BOLD)
                        put("│   Not scanned")
                        put("│")
                        put(f"│ MAC Address:", curses.A_BOLD)
                        put("│   Unknown")
                        put("│")
                        put(f"│ Status:", curses.A_BOLD)
                        put("│   Unknown", curses.A_DIM)
                        put("│")
                        put("└" + "─" * (inner_w - 1))
                        put("")
                        put("Press 's' to start network scan", curses.A_DIM)
                        put("")
                        put("┌─ Open TCP Ports", curses.A_BOLD | cpair(4))

                    # Show port scan results with service names
                    put("│")
                    if self.portscan_running:
                        if self.portscan_current_port:
                            put(f"│ ⟳ Scanning port {self.portscan_current_port}/10000...", curses.A_DIM | cpair(4))
                        else:
                            put("│ ⟳ Scanning ports...", curses.A_DIM | cpair(4))
                    elif self.portscan_target in self.portscan_cache:
                        # Show cache age
                        _, ts = self.portscan_cache[self.portscan_target]
                        age = time.time() - ts
                        if age < 60:
                            age_str = f"{int(age)}s ago"
                        elif age < 3600:
                            age_str = f"{int(age/60)}m ago"
                        else:
                            age_str = f"{int(age/3600)}h ago"
                        put(f"│ ✓ Cached ({age_str})", curses.A_DIM | cpair(1))
                    else:
                        def svc(p: int) -> str:
                            try:
                                return socket.getservbyport(p, 'tcp')
                            except Exception:
                                # common fallbacks
                                common = {
                                    21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
                                    53: 'domain', 80: 'http', 110: 'pop3', 143: 'imap',
                                    443: 'https', 445: 'smb', 3306: 'mysql', 3389: 'rdp',
                                    5432: 'postgresql', 5900: 'vnc', 6379: 'redis',
                                    8080: 'http-proxy', 8443: 'https-alt', 27017: 'mongodb'
                                }
                                return common.get(p, 'unknown')
                        shown = 0
                        if self.portscan_open:
                            for p in self.portscan_open:
                                service = svc(p)
                                put(f"│ • {p:>5}/tcp  →  {service}", cpair(1))
                                shown += 1
                                if row >= panel_h - 3:
                                    remaining = max(0, len(self.portscan_open) - shown)
                                    if remaining:
                                        put(f"│ ... and {remaining} more ports")
                                    break
                        else:
                            put("│ No open ports found", curses.A_DIM)
                    put("│")
                    put("└" + "─" * (inner_w - 1))
                    put("")
                    put("╔═══ CONTROLS ═══", curses.A_BOLD | cpair(4))
                    put("║")
                    put("║ [↑/↓]    Navigate hosts", curses.A_DIM)
                    put("║ [Enter]  Rescan ports", curses.A_DIM)
                    put("║ [s]      Scan network", curses.A_DIM)
                    put("║ [e]      Export to CSV", curses.A_DIM)
                    put("║ [a]      Toggle filter (ALL/UP)", curses.A_DIM)
                    put("║ [1-5]    Sort by column", curses.A_DIM)
                    put("║ [o]      Cycle sort", curses.A_DIM)
                    put("║ [q]      Quit", curses.A_DIM)
                    put("╚" + "═" * (inner_w - 1))
                    # Don't refresh panel yet - wait until after stdscr

            # Footer with export message or last scan time
            if self.export_message and self.export_message_time:
                # Show export message for 5 seconds
                if time.time() - self.export_message_time < 5.0:
                    try:
                        msg_color = cpair(self.export_message_color)
                        stdscr.addstr(h - 1, 0, self.export_message[:w-1], msg_color | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    self.export_message = None
            elif self.last_scan_ts:
                stdscr.addstr(h - 1, 0, time.strftime("Last scan: %Y-%m-%d %H:%M:%S", time.localtime(self.last_scan_ts)), curses.A_DIM)

            # Batch refresh: stdscr first, then panel on top
            stdscr.noutrefresh()
            if panel_active and 'win' in locals():
                try:
                    win.noutrefresh()
                except:
                    pass
            try:
                curses.doupdate()
            except Exception:
                stdscr.refresh()

            # Handle keys
            try:
                ch = stdscr.getch()
            except Exception:
                ch = -1

            # View switching (F1-F3, Tab)
            if ch == curses.KEY_F1 or ch == 265:  # F1 - Dashboard
                self.view_manager.switch_to('dashboard', self)
                continue
            elif ch == curses.KEY_F2 or ch == 266:  # F2 - Host List
                self.view_manager.switch_to('hosts', self)
                continue
            elif ch == curses.KEY_F3 or ch == 267:  # F3 - Details
                self.view_manager.switch_to('details', self)
                continue
            elif ch == 9:  # Tab - cycle next
                self.view_manager.cycle_next(self)
                continue
            elif ch == 353:  # Shift+Tab - cycle prev (KEY_BTAB)
                self.view_manager.cycle_prev(self)
                continue

            if ch == ord('q'):
                self.stop = True
                # Save cache before quitting
                self._save_cache()
                break
            elif ch == ord('s') and not self.scanning:
                threading.Thread(target=self._scan, daemon=True).start()
            elif ch == ord('e'):
                # Show export dialog
                self._show_export_dialog(stdscr)
            elif ch == ord('P'):
                # Show profile selection dialog (Shift+P)
                self._show_profile_dialog(stdscr)
            elif ch == ord('C'):
                # Clear cache (Shift+C)
                cache_count = len(self.portscan_cache)
                self._clear_cache()
                self.export_message = f"✓ Cleared {cache_count} cached entries"
                self.export_message_color = 1
                self.export_message_time = time.time()
            elif ch == ord('r'):
                # refresh detection
                self.iface = get_default_interface() or self.iface
                self.cidr = get_local_network_cidr() or self.cidr
                # Also clear expired cache entries
                self._clear_expired_cache()
            elif ch == ord('a'):
                self.only_up = not self.only_up
                self.sel = 0
            elif ch == ord('+') or ch == ord('='):
                # Increase rate limit
                stats = self.rate_limiter.get_stats()
                current_rate = stats.get('rate', 0)
                
                if not self.rate_limit_enabled or current_rate == 0:
                    # Start with 10 req/s
                    new_rate = 10
                    self.rate_limit_enabled = True
                elif current_rate < 10:
                    new_rate = current_rate + 1
                elif current_rate < 50:
                    new_rate = current_rate + 5
                else:
                    new_rate = current_rate + 10
                
                self.rate_limiter.set_rate(new_rate, int(new_rate * 2))
                self.export_message = f"Rate limit: {new_rate} req/s"
                self.export_message_color = 1
                self.export_message_time = time.time()
            elif ch == ord('-') or ch == ord('_'):
                # Decrease rate limit
                stats = self.rate_limiter.get_stats()
                current_rate = stats.get('rate', 0)
                
                if not self.rate_limit_enabled or current_rate == 0:
                    # Do nothing
                    pass
                elif current_rate <= 2:
                    # Disable rate limiting
                    self.rate_limit_enabled = False
                    self.rate_limiter.set_rate(0, 1)
                    self.export_message = "Rate limit: disabled"
                    self.export_message_color = 1
                    self.export_message_time = time.time()
                elif current_rate <= 10:
                    new_rate = current_rate - 1
                    self.rate_limiter.set_rate(new_rate, int(new_rate * 2))
                    self.export_message = f"Rate limit: {new_rate} req/s"
                    self.export_message_color = 1
                    self.export_message_time = time.time()
                elif current_rate <= 50:
                    new_rate = current_rate - 5
                    self.rate_limiter.set_rate(new_rate, int(new_rate * 2))
                    self.export_message = f"Rate limit: {new_rate} req/s"
                    self.export_message_color = 1
                    self.export_message_time = time.time()
                else:
                    new_rate = current_rate - 10
                    self.rate_limiter.set_rate(new_rate, int(new_rate * 2))
                    self.export_message = f"Rate limit: {new_rate} req/s"
                    self.export_message_color = 1
                    self.export_message_time = time.time()
            elif ch == ord('o'):
                # cycle sort column
                order = ["ip", "status", "latency", "hostname", "mac"]
                try:
                    idx = (order.index(self.sort_by) + 1) % len(order)
                except ValueError:
                    idx = 0
                self.sort_by = order[idx]
            elif ch == ord('O'):
                self.sort_desc = not self.sort_desc
            elif ch in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5')):
                mapping = {
                    ord('1'): "ip",
                    ord('2'): "status",
                    ord('3'): "latency",
                    ord('4'): "hostname",
                    ord('5'): "mac",
                }
                self.sort_by = mapping.get(ch, self.sort_by)
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter re-scans ports for selected
                if rows:
                    target_ip = rows[self.sel]['ip']
                    if target_ip:
                        self.portscan_target = target_ip
                        self.portscan_open = []
                        self.portscan_running = True
                        threading.Thread(target=self._portscan_worker, args=(target_ip,), daemon=True).start()
            elif ch == ord('p'):
                # scan top 1000 ports for selected host
                with self.scan_lock:
                    rows = self.scan_results[:]
                if self.only_up:
                    rows = [r for r in rows if r.get('up')]
                if not rows:
                    continue
                idx = max(0, min(self.sel, len(rows) - 1))
                target_ip = rows[idx]['ip']
                if target_ip:
                    self.portscan_target = target_ip
                    self.portscan_open = []
                    self.portscan_running = True
                    threading.Thread(target=self._portscan_worker, args=(target_ip,), daemon=True).start()

            elif ch in (curses.KEY_UP, ord('k')):
                if self.sel > 0:
                    self.sel -= 1
                    # auto-trigger scan for new selection if idle
                    if not self.portscan_running and rows:
                        new_ip = rows[self.sel]['ip']
                        if new_ip and new_ip != self.portscan_target:
                            self.portscan_target = new_ip
                            self.portscan_open = []
                            self.portscan_running = True
                            threading.Thread(target=self._portscan_worker, args=(new_ip,), daemon=True).start()
            elif ch in (curses.KEY_DOWN, ord('j')):
                with self.scan_lock:
                    n = len([r for r in self.scan_results if (r.get('up') if self.only_up else True)])
                if self.sel < max(0, n - 1):
                    self.sel += 1
                    # auto-trigger scan for new selection if idle
                    if not self.portscan_running and rows:
                        new_ip = rows[self.sel]['ip']
                        if new_ip and new_ip != self.portscan_target:
                            self.portscan_target = new_ip
                            self.portscan_open = []
                            self.portscan_running = True
                            threading.Thread(target=self._portscan_worker, args=(new_ip,), daemon=True).start()

        # end loop


def main() -> int:
    app = TuiApp()
    curses.wrapper(app.draw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
