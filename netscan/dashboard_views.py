"""
Concrete View Implementations - Dashboard, Host List, and Details views.
"""

import curses
from typing import Any, List
from .tui_views import View
from .tui_widgets import (
    NetworkHealthWidget,
    DeviceBreakdownWidget,
    TopServicesWidget,
    ActivityFeedWidget,
    NetworkTrafficWidget,
    QuickActionsBar
)


class DashboardView(View):
    """Main dashboard view showing network overview and statistics."""
    
    def __init__(self):
        """Initialize dashboard view."""
        super().__init__("dashboard")
        
        # Create widgets
        self.health_widget = NetworkHealthWidget()
        self.device_widget = DeviceBreakdownWidget()
        self.services_widget = TopServicesWidget()
        self.activity_widget = ActivityFeedWidget()
        self.traffic_widget = NetworkTrafficWidget()
        self.actions_bar = QuickActionsBar()
    
    def draw(self, stdscr, app_state: Any) -> None:
        """Draw the dashboard view."""
        h, w = stdscr.getmaxyx()
        
        # Define color map
        color_map = {
            'border': curses.color_pair(3),  # cyan
            'red': curses.color_pair(2),
            'yellow': curses.color_pair(4),
            'green': curses.color_pair(1),
            'cyan': curses.color_pair(3),
            'magenta': curses.color_pair(5),
            'blue': curses.color_pair(7),
            'normal': curses.A_NORMAL,
            'dim': curses.A_DIM,
        }
        
        # Calculate layout (4 rows of widgets)
        # Row heights: title(2) + widget1(8) + widget2(8) + widget3(4) + actions(1) = 23
        widget_top = 4  # Below header
        
        # Layout configuration
        if h < 30:
            # Compact layout for small terminals
            self._draw_compact_layout(stdscr, app_state, widget_top, w, h, color_map)
        else:
            # Full layout for normal terminals
            self._draw_full_layout(stdscr, app_state, widget_top, w, h, color_map)
    
    def _draw_full_layout(self, stdscr, app_state, widget_top, w, h, color_map):
        """Draw full dashboard layout."""
        # Calculate widths
        left_width = w // 2 - 1
        right_width = w - left_width - 1
        
        # Row 1: Health (left) + Device Breakdown (right)
        row1_height = 8
        self.health_widget.draw(
            stdscr,
            widget_top,
            0,
            row1_height,
            left_width,
            app_state.scan_results,
            color_map
        )
        
        self.device_widget.draw(
            stdscr,
            widget_top,
            left_width + 1,
            row1_height,
            right_width,
            app_state.scan_results,
            color_map
        )
        
        # Row 2: Services (left) + Activity (right)
        row2_top = widget_top + row1_height
        row2_height = 8
        
        self.services_widget.draw(
            stdscr,
            row2_top,
            0,
            row2_height,
            left_width,
            app_state.scan_results,
            color_map
        )
        
        self.activity_widget.draw(
            stdscr,
            row2_top,
            left_width + 1,
            row2_height,
            right_width,
            app_state.activity_feed,
            color_map
        )
        
        # Row 3: Traffic (full width)
        row3_top = row2_top + row2_height
        row3_height = 5
        
        if row3_top + row3_height < h - 2:
            self.traffic_widget.draw(
                stdscr,
                row3_top,
                0,
                row3_height,
                w,
                app_state.rx_rate,
                app_state.tx_rate,
                app_state.rx_hist,
                app_state.tx_hist,
                color_map
            )
        
        # Row 4: Quick Actions (full width at bottom)
        actions_y = h - 2
        if actions_y > row3_top + row3_height:
            self.actions_bar.draw(stdscr, actions_y, 0, w, color_map)
    
    def _draw_compact_layout(self, stdscr, app_state, widget_top, w, h, color_map):
        """Draw compact dashboard for small terminals."""
        # Just show health and activity in compact mode
        row_height = (h - widget_top - 3) // 2
        
        self.health_widget.draw(
            stdscr,
            widget_top,
            0,
            row_height,
            w,
            app_state.scan_results,
            color_map
        )
        
        self.activity_widget.draw(
            stdscr,
            widget_top + row_height,
            0,
            row_height,
            w,
            app_state.activity_feed,
            color_map
        )
        
        # Quick actions at bottom
        self.actions_bar.draw(stdscr, h - 2, 0, w, color_map)
    
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """Handle input for dashboard view."""
        # Function keys for quick actions
        if ch == curses.KEY_F5 or ch == 265:  # F5 - Rescan
            if not app_state.scanning:
                import threading
                threading.Thread(target=app_state._scan, daemon=True).start()
                app_state.activity_feed.add('scan', 'Quick rescan started', severity='info')
            return True
        
        elif ch == curses.KEY_F6 or ch == 270:  # F6 - Export dialog
            # Trigger export dialog (handled by main TUI)
            return False
        
        elif ch == curses.KEY_F7 or ch == 271:  # F7 - Profile selector
            # Trigger profile dialog (handled by main TUI)
            return False
        
        elif ch == curses.KEY_F9 or ch == 273:  # F9 - Clear cache
            app_state._clear_cache()
            app_state.activity_feed.add('cache', 'Cache cleared', severity='success')
            return True
        
        elif ch == curses.KEY_F10 or ch == 274:  # F10 - Quit
            app_state.stop = True
            return True
        
        # 's' for scan
        elif ch == ord('s') and not app_state.scanning:
            import threading
            threading.Thread(target=app_state._scan, daemon=True).start()
            app_state.activity_feed.add('scan', 'Manual scan started', severity='info')
            return True
        
        return False
    
    def on_enter(self, app_state: Any) -> None:
        """Called when entering dashboard view."""
        super().on_enter(app_state)
        if hasattr(app_state, 'activity_feed'):
            app_state.activity_feed.add('view', 'Switched to Dashboard', severity='info')
    
    def get_title(self) -> str:
        """Get view title."""
        return "Dashboard"


class HostListView(View):
    """Enhanced host list view with better visuals."""
    
    def __init__(self):
        """Initialize host list view."""
        super().__init__("hosts")
    
    def draw(self, stdscr, app_state: Any) -> None:
        """Draw the enhanced host list view."""
        h, w = stdscr.getmaxyx()
        
        # Start drawing below the tab bar (line 3)
        start_y = 3
        
        # Get scan results
        with app_state.scan_lock:
            all_hosts = app_state.scan_results[:]
        
        # Filter if needed
        if app_state.only_up:
            hosts = [r for r in all_hosts if r.get('up')]
        else:
            hosts = all_hosts
        
        # Sort hosts
        hosts = self._sort_hosts(hosts, app_state.sort_by, app_state.sort_desc)
        
        # Statistics bar
        up_count = sum(1 for r in all_hosts if r.get('up'))
        down_count = len(all_hosts) - up_count
        
        if app_state.scanning and app_state.scan_current_host:
            status = f'⚡ Scanning {app_state.scan_current_host}'
            status_color = 3  # Yellow
        elif app_state.scanning:
            status = '⚡ Scanning...'
            status_color = 3
        else:
            status = '✓ Ready'
            status_color = 1  # Green
        
        # Draw statistics header with box drawing
        try:
            # Top border
            stdscr.addstr(start_y, 0, "┌" + "─" * (w - 2) + "┐", curses.color_pair(4))
            
            # Statistics line with icons
            stats_line = f" 🌐 Network: {app_state.cidr}  │  📊 Total: {len(all_hosts)}  │  "
            stats_line += f"🟢 UP: {up_count}  │  🔴 DOWN: {down_count}  │  {status} "
            
            # Pad to width
            stats_line = stats_line.ljust(w - 2)
            stdscr.addstr(start_y + 1, 0, "│", curses.color_pair(4))
            stdscr.addstr(start_y + 1, 1, stats_line[:w-2], curses.A_BOLD | curses.color_pair(status_color))
            stdscr.addstr(start_y + 1, w - 1, "│", curses.color_pair(4))
            
            # Bottom border
            stdscr.addstr(start_y + 2, 0, "└" + "─" * (w - 2) + "┘", curses.color_pair(4))
        except curses.error:
            pass
        
        # Table header
        table_y = start_y + 4
        
        # Column widths
        col_ip_width = 17
        col_status_width = 10
        col_latency_width = 12
        col_hostname_width = 25
        col_mac_width = 19
        col_vendor_width = max(20, w - col_ip_width - col_status_width - col_latency_width - col_hostname_width - col_mac_width - 10)
        
        # Draw table header with box
        try:
            # Header box top
            stdscr.addstr(table_y, 0, "┌" + "─" * (w - 2) + "┐", curses.color_pair(4) | curses.A_DIM)
            
            # Column headers
            header_y = table_y + 1
            col_x = 2
            
            # Sort indicators
            def get_sort_indicator(col_name):
                if app_state.sort_by == col_name:
                    return " ↓" if app_state.sort_desc else " ↑"
                return ""
            
            headers = [
                ("IP Address" + get_sort_indicator("ip"), col_ip_width, 4),
                ("Status" + get_sort_indicator("status"), col_status_width, 4),
                ("Latency" + get_sort_indicator("latency"), col_latency_width, 4),
                ("Hostname" + get_sort_indicator("hostname"), col_hostname_width, 4),
                ("MAC Address", col_mac_width, 4),
                ("Vendor", col_vendor_width, 4),
            ]
            
            stdscr.addstr(header_y, 0, "│", curses.color_pair(4) | curses.A_DIM)
            for header, width, color in headers:
                try:
                    stdscr.addstr(header_y, col_x, header[:width].ljust(width), curses.A_BOLD | curses.color_pair(color))
                    col_x += width + 1
                except curses.error:
                    pass
            stdscr.addstr(header_y, w - 1, "│", curses.color_pair(4) | curses.A_DIM)
            
            # Header separator
            stdscr.addstr(table_y + 2, 0, "├" + "─" * (w - 2) + "┤", curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass
        
        # Table content area
        content_start_y = table_y + 3
        content_height = h - content_start_y - 3  # Leave room for footer
        
        # Calculate visible range based on selection
        if app_state.sel < 0:
            app_state.sel = 0
        if app_state.sel >= len(hosts):
            app_state.sel = max(0, len(hosts) - 1)
        
        # Scrolling window
        scroll_offset = max(0, app_state.sel - content_height // 2)
        visible_hosts = hosts[scroll_offset:scroll_offset + content_height]
        
        # Draw host rows
        for idx, host in enumerate(visible_hosts):
            row_y = content_start_y + idx
            if row_y >= h - 3:
                break
            
            global_idx = scroll_offset + idx
            is_selected = (global_idx == app_state.sel)
            
            # Row styling
            if is_selected:
                row_attr = curses.A_REVERSE | curses.A_BOLD
                border_color = 3  # Yellow highlight
            else:
                row_attr = curses.A_NORMAL
                border_color = 4
            
            try:
                # Left border
                stdscr.addstr(row_y, 0, "│", curses.color_pair(border_color) | curses.A_DIM)
                
                # Row content
                col_x = 2
                
                # IP
                ip = host.get('ip', '')
                stdscr.addstr(row_y, col_x, ip[:col_ip_width].ljust(col_ip_width), row_attr | curses.color_pair(3))
                col_x += col_ip_width + 1
                
                # Status with icon
                is_up = host.get('up', False)
                if is_up:
                    status_text = "🟢 UP"
                    status_color = 1
                else:
                    status_text = "🔴 DOWN"
                    status_color = 2
                
                stdscr.addstr(row_y, col_x, status_text[:col_status_width].ljust(col_status_width), 
                            row_attr | curses.color_pair(status_color) | curses.A_BOLD)
                col_x += col_status_width + 1
                
                # Latency
                lat = host.get('latency_ms')
                if lat is not None and is_up:
                    lat_text = f"{lat:.2f} ms"
                    # Color based on latency
                    if lat < 10:
                        lat_color = 1  # Green - excellent
                    elif lat < 50:
                        lat_color = 3  # Yellow - good
                    else:
                        lat_color = 2  # Red - slow
                else:
                    lat_text = "-"
                    lat_color = 4
                
                stdscr.addstr(row_y, col_x, lat_text[:col_latency_width].ljust(col_latency_width),
                            row_attr | curses.color_pair(lat_color))
                col_x += col_latency_width + 1
                
                # Hostname
                hostname = host.get('hostname') or '-'
                stdscr.addstr(row_y, col_x, hostname[:col_hostname_width].ljust(col_hostname_width),
                            row_attr | curses.color_pair(4))
                col_x += col_hostname_width + 1
                
                # MAC
                mac = host.get('mac') or '-'
                stdscr.addstr(row_y, col_x, mac[:col_mac_width].ljust(col_mac_width),
                            row_attr | curses.color_pair(4) | curses.A_DIM)
                col_x += col_mac_width + 1
                
                # Vendor
                vendor = host.get('vendor') or '-'
                stdscr.addstr(row_y, col_x, vendor[:col_vendor_width].ljust(col_vendor_width),
                            row_attr | curses.color_pair(4))
                
                # Right border
                stdscr.addstr(row_y, w - 1, "│", curses.color_pair(border_color) | curses.A_DIM)
                
            except curses.error:
                pass
        
        # Fill empty rows
        for idx in range(len(visible_hosts), content_height):
            row_y = content_start_y + idx
            if row_y >= h - 3:
                break
            try:
                stdscr.addstr(row_y, 0, "│" + " " * (w - 2) + "│", curses.color_pair(4) | curses.A_DIM)
            except curses.error:
                pass
        
        # Table footer
        footer_y = h - 3
        try:
            stdscr.addstr(footer_y, 0, "└" + "─" * (w - 2) + "┘", curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass
        
        # Help line at bottom
        help_y = h - 2
        help_text = "⌨  [↑↓] Navigate  [Enter] Details  [p] Port Scan  [s] Scan  [e] Export  [P] Profile  [a] Filter  [1-5] Sort  [q] Quit"
        try:
            stdscr.addstr(help_y, 0, help_text[:w], curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass
        
        # Selection info line
        info_y = h - 1
        if hosts and 0 <= app_state.sel < len(hosts):
            selected_host = hosts[app_state.sel]
            info_text = f"📍 Selected: {selected_host.get('ip')} ({app_state.sel + 1}/{len(hosts)})"
            if app_state.only_up:
                info_text += "  [Filtered: UP only]"
        else:
            info_text = f"Total: {len(hosts)} hosts"
        
        try:
            stdscr.addstr(info_y, 0, info_text[:w], curses.A_BOLD | curses.color_pair(3))
        except curses.error:
            pass
    
    def _sort_hosts(self, hosts, sort_by, sort_desc):
        """Sort hosts by specified column."""
        if sort_by == 'ip':
            import ipaddress
            hosts = sorted(hosts, key=lambda h: ipaddress.ip_address(h.get('ip', '0.0.0.0')))
        elif sort_by == 'status':
            hosts = sorted(hosts, key=lambda h: (not h.get('up', False), h.get('ip', '')))
        elif sort_by == 'latency':
            hosts = sorted(hosts, key=lambda h: (h.get('latency_ms') is None, h.get('latency_ms', 999999)))
        elif sort_by == 'hostname':
            hosts = sorted(hosts, key=lambda h: (h.get('hostname') or 'zzz').lower())
        elif sort_by == 'mac':
            hosts = sorted(hosts, key=lambda h: h.get('mac') or 'zz:zz:zz:zz:zz:zz')
        
        if sort_desc:
            hosts = list(reversed(hosts))
        
        return hosts
    
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """Handle input for host list view."""
        # Get current filtered/sorted list
        with app_state.scan_lock:
            all_hosts = app_state.scan_results[:]
        
        if app_state.only_up:
            hosts = [r for r in all_hosts if r.get('up')]
        else:
            hosts = all_hosts
        
        hosts = self._sort_hosts(hosts, app_state.sort_by, app_state.sort_desc)
        
        # Navigation
        if ch == curses.KEY_UP:
            if app_state.sel > 0:
                app_state.sel -= 1
            return True
        elif ch == curses.KEY_DOWN:
            if app_state.sel < len(hosts) - 1:
                app_state.sel += 1
            return True
        elif ch == curses.KEY_HOME:
            app_state.sel = 0
            return True
        elif ch == curses.KEY_END:
            app_state.sel = max(0, len(hosts) - 1)
            return True
        elif ch == curses.KEY_PPAGE:  # Page Up
            app_state.sel = max(0, app_state.sel - 10)
            return True
        elif ch == curses.KEY_NPAGE:  # Page Down
            app_state.sel = min(len(hosts) - 1, app_state.sel + 10)
            return True
        
        # Actions
        elif ch in (10, 13, curses.KEY_ENTER):
            # Enter - switch to details view
            if hosts and 0 <= app_state.sel < len(hosts):
                app_state.view_manager.switch_to('details', app_state)
            return True
        
        elif ch == ord('p') or ch == ord('P'):
            # Port scan selected host
            if hosts and 0 <= app_state.sel < len(hosts):
                selected_host = hosts[app_state.sel]
                ip = selected_host.get('ip')
                if ip and selected_host.get('up'):
                    import threading
                    app_state.portscan_target = ip
                    app_state.portscan_running = True
                    threading.Thread(
                        target=app_state._portscan_worker,
                        args=(ip,),
                        daemon=True
                    ).start()
                    app_state.activity_feed.add(
                        'port_scan',
                        f'Port scan started for {ip}',
                        ip=ip,
                        severity='info'
                    )
            return True
        
        elif ch == ord('a'):
            # Toggle filter
            app_state.only_up = not app_state.only_up
            app_state.sel = 0
            return True
        
        elif ch in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5')):
            # Sort by column
            sort_map = {
                ord('1'): 'ip',
                ord('2'): 'status',
                ord('3'): 'latency',
                ord('4'): 'hostname',
                ord('5'): 'mac',
            }
            new_sort = sort_map.get(ch)
            if new_sort == app_state.sort_by:
                # Toggle direction
                app_state.sort_desc = not app_state.sort_desc
            else:
                app_state.sort_by = new_sort
                app_state.sort_desc = False
            return True
        
        elif ch == ord('o'):
            # Cycle sort column
            sort_cycle = ['ip', 'status', 'latency', 'hostname', 'mac']
            try:
                idx = sort_cycle.index(app_state.sort_by)
                app_state.sort_by = sort_cycle[(idx + 1) % len(sort_cycle)]
            except ValueError:
                app_state.sort_by = 'ip'
            return True
        
        elif ch == ord('O'):
            # Toggle sort direction
            app_state.sort_desc = not app_state.sort_desc
            return True
        
        # Let other keys pass through to global handlers
        return False
    
    def on_enter(self, app_state: Any) -> None:
        """Called when entering host list view."""
        super().on_enter(app_state)
        if hasattr(app_state, 'activity_feed'):
            app_state.activity_feed.add('view', 'Switched to Host List', severity='info')
    
    def get_title(self) -> str:
        """Get view title."""
        return "Host List"


class DetailView(View):
    """Detailed view of a single host."""
    
    def __init__(self):
        """Initialize detail view."""
        super().__init__("details")
        self.selected_ip: str = None
    
    def draw(self, stdscr, app_state: Any) -> None:
        """Draw the detail view."""
        h, w = stdscr.getmaxyx()
        
        # Get selected host
        host = None
        if self.selected_ip:
            with app_state.scan_lock:
                for r in app_state.scan_results:
                    if r.get('ip') == self.selected_ip:
                        host = r
                        break
        
        if not host:
            # No host selected, show message
            try:
                msg = "No host selected. Press F2 to view host list."
                stdscr.addstr(h // 2, (w - len(msg)) // 2, msg, curses.A_DIM)
            except curses.error:
                pass
            return
        
        # Draw detailed host information
        y = 4
        x = 2
        
        try:
            # Title
            stdscr.addstr(y, x, f"Host Details: {host.get('ip')}", curses.A_BOLD | curses.color_pair(4))
            y += 2
            
            # Basic info
            stdscr.addstr(y, x, f"Status: ", curses.A_BOLD)
            status = "UP" if host.get('up') else "DOWN"
            status_color = curses.color_pair(1) if host.get('up') else curses.color_pair(2)
            stdscr.addstr(y, x + 8, status, status_color | curses.A_BOLD)
            y += 1
            
            if host.get('latency_ms'):
                stdscr.addstr(y, x, f"Latency: {host.get('latency_ms'):.1f}ms")
                y += 1
            
            if host.get('hostname'):
                stdscr.addstr(y, x, f"Hostname: {host.get('hostname')}")
                y += 1
            
            if host.get('mac'):
                stdscr.addstr(y, x, f"MAC: {host.get('mac')}")
                y += 1
            
            if host.get('vendor'):
                stdscr.addstr(y, x, f"Vendor: {host.get('vendor')}")
                y += 1
            
            # Ports
            y += 1
            ports = host.get('ports', [])
            if ports:
                stdscr.addstr(y, x, f"Open Ports ({len(ports)}):", curses.A_BOLD)
                y += 1
                
                # Show ports in columns
                from .scanner import get_service_name
                col_width = 25
                cols = max(1, (w - 4) // col_width)
                
                for i, port in enumerate(ports[:50]):  # Limit to 50
                    service = get_service_name(port)
                    text = f"  {port:5d}  {service}"
                    col = i % cols
                    row = i // cols
                    if y + row < h - 2:
                        stdscr.addstr(y + row, x + (col * col_width), text[:col_width - 1])
            else:
                stdscr.addstr(y, x, "No open ports detected", curses.A_DIM)
            
        except curses.error:
            pass
    
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """Handle input for detail view."""
        # Enter to rescan ports
        if ch in (10, 13, curses.KEY_ENTER):
            if self.selected_ip:
                import threading
                threading.Thread(
                    target=app_state._portscan_worker,
                    args=(self.selected_ip,),
                    daemon=True
                ).start()
                app_state.activity_feed.add(
                    'port_scan',
                    f'Rescanning ports for {self.selected_ip}',
                    ip=self.selected_ip,
                    severity='info'
                )
            return True
        
        return False
    
    def on_enter(self, app_state: Any) -> None:
        """Called when entering detail view."""
        super().on_enter(app_state)
        
        # Set selected IP from current selection in host list
        if hasattr(app_state, 'scan_results') and hasattr(app_state, 'sel'):
            with app_state.scan_lock:
                rows = app_state.scan_results[:]
            
            if rows and 0 <= app_state.sel < len(rows):
                self.selected_ip = rows[app_state.sel].get('ip')
                
                if hasattr(app_state, 'activity_feed'):
                    app_state.activity_feed.add(
                        'view',
                        f'Viewing details for {self.selected_ip}',
                        ip=self.selected_ip,
                        severity='info'
                    )
    
    def get_title(self) -> str:
        """Get view title."""
        if self.selected_ip:
            return f"Details: {self.selected_ip}"
        return "Details"
