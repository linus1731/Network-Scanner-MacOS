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
    """Traditional host list view (current implementation)."""
    
    def __init__(self):
        """Initialize host list view."""
        super().__init__("hosts")
    
    def draw(self, stdscr, app_state: Any) -> None:
        """Draw the host list view."""
        # This will use the existing host list drawing code from TuiApp
        # For now, delegate to the app's existing draw logic
        h, w = stdscr.getmaxyx()
        
        # Calculate layout similar to current TUI
        panel_w = max(45, min(70, w // 3))
        if w - panel_w - 2 < 50:
            panel_w = max(40, w - 52)
        if panel_w < 40:
            panel_w = 40
        if w < 100:
            panel_w = max(35, w // 2)
        
        header_y = 4  # Below title and help
        table_x = panel_w + 1
        
        # Get scan results
        with app_state.scan_lock:
            progress = len(app_state.scan_results)
            up_count = sum(1 for r in app_state.scan_results if r.get('up'))
        
        # Show scan status
        if app_state.scanning and app_state.scan_current_host:
            state = f'scanning {app_state.scan_current_host}'
        elif app_state.scanning:
            state = 'running'
        else:
            state = 'idle'
        
        try:
            stdscr.addstr(header_y, table_x, f"Scan results ({state})  hosts={progress}", curses.A_BOLD)
        except curses.error:
            pass
        
        # Note: Full host list drawing would go here
        # For now, this is a placeholder that will be integrated with existing code
    
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """Handle input for host list view."""
        # Most inputs will be handled by existing TuiApp logic
        # Just handle view-specific keys here
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
