"""
TUI Widgets - Visual components for the dashboard.

Provides reusable UI widgets for displaying network statistics:
- Health bars with color gradients
- Horizontal bar charts
- Activity feeds
- Traffic graphs
- Quick action buttons
"""

import curses
from typing import List, Dict, Optional, Tuple
from .activity import ActivityFeed, Event
from .stats import NetworkStats, DeviceCategorizer


def draw_box(
    stdscr,
    y: int,
    x: int,
    height: int,
    width: int,
    title: str = "",
    color: int = 0
) -> None:
    """
    Draw a bordered box with optional title.
    
    Args:
        stdscr: Curses window
        y: Top-left Y coordinate
        x: Top-left X coordinate
        height: Box height
        width: Box width
        title: Optional title text
        color: Color pair number
    """
    if height < 2 or width < 2:
        return
    
    try:
        # Draw corners
        stdscr.addstr(y, x, "┌", color)
        stdscr.addstr(y, x + width - 1, "┐", color)
        stdscr.addstr(y + height - 1, x, "└", color)
        stdscr.addstr(y + height - 1, x + width - 1, "┘", color)
        
        # Draw horizontal lines
        for i in range(1, width - 1):
            stdscr.addstr(y, x + i, "─", color)
            stdscr.addstr(y + height - 1, x + i, "─", color)
        
        # Draw vertical lines
        for i in range(1, height - 1):
            stdscr.addstr(y + i, x, "│", color)
            stdscr.addstr(y + i, x + width - 1, "│", color)
        
        # Draw title if provided
        if title and len(title) < width - 4:
            title_text = f" {title} "
            title_x = x + (width - len(title_text)) // 2
            stdscr.addstr(y, title_x, title_text, color | curses.A_BOLD)
    except curses.error:
        pass  # Ignore if drawing outside screen


def draw_progress_bar(
    stdscr,
    y: int,
    x: int,
    width: int,
    value: float,
    max_value: float = 100.0,
    label: str = "",
    show_percentage: bool = True,
    color_low: int = 0,
    color_mid: int = 0,
    color_high: int = 0
) -> None:
    """
    Draw a progress bar with color gradient.
    
    Args:
        stdscr: Curses window
        y: Y coordinate
        x: X coordinate
        width: Bar width
        value: Current value
        max_value: Maximum value
        label: Label text
        show_percentage: Show percentage value
        color_low: Color for low values (red)
        color_mid: Color for medium values (yellow)
        color_high: Color for high values (green)
    """
    if width < 3:
        return
    
    percentage = (value / max_value * 100) if max_value > 0 else 0
    percentage = min(100, max(0, percentage))
    
    # Choose color based on percentage
    if percentage >= 70:
        bar_color = color_high  # Green
    elif percentage >= 40:
        bar_color = color_mid   # Yellow
    else:
        bar_color = color_low   # Red
    
    # Calculate filled portion
    bar_width = width - 2 if show_percentage else width
    filled = int(bar_width * percentage / 100)
    
    try:
        # Draw the bar
        bar = "█" * filled + "░" * (bar_width - filled)
        stdscr.addstr(y, x, bar, bar_color)
        
        # Draw percentage
        if show_percentage:
            pct_text = f" {int(percentage)}%"
            stdscr.addstr(y, x + bar_width, pct_text)
        
        # Draw label
        if label:
            stdscr.addstr(y, x + width + 2, label)
    except curses.error:
        pass


def draw_horizontal_bar_chart(
    stdscr,
    y: int,
    x: int,
    width: int,
    items: List[Tuple[str, int]],
    max_items: int = 5,
    color: int = 0
) -> int:
    """
    Draw a horizontal bar chart.
    
    Args:
        stdscr: Curses window
        y: Starting Y coordinate
        x: Starting X coordinate
        width: Chart width
        items: List of (label, value) tuples
        max_items: Maximum number of items to display
        color: Color pair number
        
    Returns:
        Number of lines drawn
    """
    if not items or width < 10:
        return 0
    
    # Sort by value and take top N
    sorted_items = sorted(items, key=lambda x: x[1], reverse=True)[:max_items]
    
    if not sorted_items:
        return 0
    
    # Find max value for scaling
    max_val = max(item[1] for item in sorted_items)
    if max_val == 0:
        return 0
    
    # Calculate label width (longest label + 2)
    label_width = min(20, max(len(item[0]) for item in sorted_items) + 2)
    bar_width = width - label_width - 8  # Reserve space for label + count
    
    if bar_width < 5:
        return 0
    
    lines_drawn = 0
    
    try:
        for i, (label, value) in enumerate(sorted_items):
            if y + i >= curses.LINES - 1:
                break
            
            # Truncate label if needed
            display_label = label[:label_width - 1].ljust(label_width)
            
            # Draw label
            stdscr.addstr(y + i, x, display_label, color)
            
            # Draw bar
            filled = int(bar_width * value / max_val)
            bar = "█" * filled
            stdscr.addstr(y + i, x + label_width, bar, color)
            
            # Draw value
            value_text = f" {value}"
            stdscr.addstr(y + i, x + label_width + bar_width, value_text)
            
            lines_drawn += 1
    except curses.error:
        pass
    
    return lines_drawn


class NetworkHealthWidget:
    """Widget displaying network health score and statistics."""
    
    def __init__(self):
        """Initialize the health widget."""
        self.last_score = 0.0
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        height: int,
        width: int,
        hosts: List[dict],
        color_map: dict
    ) -> None:
        """
        Draw the network health widget.
        
        Args:
            stdscr: Curses window
            y: Top-left Y coordinate
            x: Top-left X coordinate
            height: Widget height
            width: Widget width
            hosts: List of host dictionaries
            color_map: Dictionary of color pairs
        """
        # Draw border
        draw_box(stdscr, y, x, height, width, "Network Health", color_map.get('border', 0))
        
        # Calculate stats
        score = NetworkStats.calculate_health_score(hosts)
        self.last_score = score
        rating = NetworkStats.get_health_rating(score)
        
        up_count = sum(1 for h in hosts if h.get('up'))
        down_count = len(hosts) - up_count
        total_ports, unique_ports = NetworkStats.get_port_count(hosts)
        
        # Draw content (inside the box)
        content_y = y + 2
        content_x = x + 2
        content_width = width - 4
        
        try:
            # Health score bar
            if height > 3:
                draw_progress_bar(
                    stdscr,
                    content_y,
                    content_x,
                    content_width - 10,
                    score,
                    100.0,
                    label=rating,
                    color_low=color_map.get('red', 0),
                    color_mid=color_map.get('yellow', 0),
                    color_high=color_map.get('green', 0)
                )
            
            # Stats
            if height > 5:
                stdscr.addstr(content_y + 2, content_x, f"UP: {up_count:3d}  DOWN: {down_count:3d}")
            
            if height > 6:
                stdscr.addstr(content_y + 3, content_x, f"Ports: {total_ports:,} open ({unique_ports} unique)")
            
            if height > 7 and hosts:
                response_stats = NetworkStats.get_response_time_stats(hosts)
                avg_lat = response_stats.get('avg', 0)
                stdscr.addstr(content_y + 4, content_x, f"Avg Latency: {avg_lat:.1f}ms")
        except curses.error:
            pass


class DeviceBreakdownWidget:
    """Widget showing device type distribution."""
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        height: int,
        width: int,
        hosts: List[dict],
        color_map: dict
    ) -> None:
        """Draw the device breakdown widget."""
        draw_box(stdscr, y, x, height, width, "Device Breakdown", color_map.get('border', 0))
        
        # Get device breakdown
        breakdown = NetworkStats.get_device_breakdown(hosts)
        
        # Filter out zero counts
        items = [(f"{DeviceCategorizer.get_device_icon(k)} {k.title()}", v) 
                 for k, v in breakdown.items() if v > 0]
        
        if items:
            draw_horizontal_bar_chart(
                stdscr,
                y + 2,
                x + 2,
                width - 4,
                items,
                max_items=min(height - 3, 6),
                color=color_map.get('cyan', 0)
            )
        else:
            try:
                stdscr.addstr(y + 2, x + 2, "No devices detected", color_map.get('dim', 0))
            except curses.error:
                pass


class TopServicesWidget:
    """Widget showing most common services."""
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        height: int,
        width: int,
        hosts: List[dict],
        color_map: dict
    ) -> None:
        """Draw the top services widget."""
        draw_box(stdscr, y, x, height, width, "Top Services", color_map.get('border', 0))
        
        # Get service distribution
        services = NetworkStats.get_service_distribution(hosts)
        
        # Convert to list of tuples
        items = list(services.items())
        
        if items:
            draw_horizontal_bar_chart(
                stdscr,
                y + 2,
                x + 2,
                width - 4,
                items,
                max_items=min(height - 3, 5),
                color=color_map.get('magenta', 0)
            )
        else:
            try:
                stdscr.addstr(y + 2, x + 2, "No services detected", color_map.get('dim', 0))
            except curses.error:
                pass


class ActivityFeedWidget:
    """Widget displaying recent activity events."""
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        height: int,
        width: int,
        activity_feed: ActivityFeed,
        color_map: dict
    ) -> None:
        """Draw the activity feed widget."""
        draw_box(stdscr, y, x, height, width, "Recent Activity", color_map.get('border', 0))
        
        # Get recent events
        max_events = height - 3
        events = activity_feed.get_recent(n=max_events)
        
        content_y = y + 2
        content_x = x + 2
        content_width = width - 4
        
        if not events:
            try:
                stdscr.addstr(content_y, content_x, "No activity yet", color_map.get('dim', 0))
            except curses.error:
                pass
            return
        
        try:
            for i, event in enumerate(events):
                if content_y + i >= y + height - 1:
                    break
                
                # Choose color based on severity
                if event.severity == 'error':
                    event_color = color_map.get('red', 0)
                elif event.severity == 'warning':
                    event_color = color_map.get('yellow', 0)
                elif event.severity == 'success':
                    event_color = color_map.get('green', 0)
                else:
                    event_color = color_map.get('normal', 0)
                
                # Format and truncate event text
                text = event.format(include_time=True)
                if len(text) > content_width:
                    text = text[:content_width - 3] + "..."
                
                stdscr.addstr(content_y + i, content_x, text, event_color)
        except curses.error:
            pass


class NetworkTrafficWidget:
    """Widget showing network traffic graphs."""
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        height: int,
        width: int,
        rx_rate: float,
        tx_rate: float,
        rx_hist: List[float],
        tx_hist: List[float],
        color_map: dict
    ) -> None:
        """Draw the network traffic widget."""
        draw_box(stdscr, y, x, height, width, "Network Traffic", color_map.get('border', 0))
        
        def fmt(bps: float) -> str:
            """Format bytes per second."""
            units = ["B/s", "KB/s", "MB/s", "GB/s"]
            i = 0
            while bps >= 1024 and i < len(units) - 1:
                bps /= 1024.0
                i += 1
            return f"{bps:6.1f} {units[i]}"
        
        def sparkline(series: List[float], width: int) -> str:
            """Generate sparkline graph."""
            if width <= 0 or not series:
                return " " * width
            
            data = series[-width:]
            if not data or max(data) == 0:
                return "▁" * width
            
            maxv = max(data)
            blocks = "▁▂▃▄▅▆▇█"
            out = []
            for v in data:
                lvl = int(round((len(blocks) - 1) * (v / maxv)))
                out.append(blocks[min(len(blocks) - 1, max(0, lvl))])
            
            return "".join(out).ljust(width)
        
        content_y = y + 2
        content_x = x + 2
        content_width = width - 4
        
        try:
            # RX line
            if height > 3:
                rx_label = "RX: "
                rx_value = f" {fmt(rx_rate)}"
                graph_width = content_width - len(rx_label) - len(rx_value)
                rx_graph = sparkline(rx_hist, graph_width)
                
                stdscr.addstr(content_y, content_x, rx_label)
                stdscr.addstr(content_y, content_x + len(rx_label), rx_graph, color_map.get('magenta', 0))
                stdscr.addstr(content_y, content_x + len(rx_label) + len(rx_graph), rx_value)
            
            # TX line
            if height > 4:
                tx_label = "TX: "
                tx_value = f" {fmt(tx_rate)}"
                graph_width = content_width - len(tx_label) - len(tx_value)
                tx_graph = sparkline(tx_hist, graph_width)
                
                stdscr.addstr(content_y + 1, content_x, tx_label)
                stdscr.addstr(content_y + 1, content_x + len(tx_label), tx_graph, color_map.get('blue', 0))
                stdscr.addstr(content_y + 1, content_x + len(tx_label) + len(tx_graph), tx_value)
        except curses.error:
            pass


class QuickActionsBar:
    """Widget showing quick action buttons."""
    
    def draw(
        self,
        stdscr,
        y: int,
        x: int,
        width: int,
        color_map: dict
    ) -> None:
        """Draw the quick actions bar."""
        actions = [
            "[F5] Rescan",
            "[F6] Export",
            "[F7] Profile",
            "[F8] Rate",
            "[F9] Clear",
            "[F10] Quit"
        ]
        
        # Join with spaces
        text = "  ".join(actions)
        
        # Center and truncate if needed
        if len(text) > width:
            text = text[:width - 3] + "..."
        else:
            text = text.center(width)
        
        try:
            stdscr.addstr(y, x, text, color_map.get('yellow', 0) | curses.A_BOLD)
        except curses.error:
            pass
