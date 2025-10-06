from __future__ import annotations

import curses
import time
import threading
import textwrap
import socket
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from .netinfo import get_default_interface, get_local_network_cidr
from .traffic import get_bytes_counters
from .scanner import scan_cidr, port_scan, expand_targets
from .resolve import resolve_ptrs
from .arp import get_arp_table
from .export import export_to_csv


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
        with self.scan_lock:
            # Pre-fill all hosts in the CIDR so every IP is visible immediately
            ips_all = expand_targets(self.cidr)
            self.scan_results = [
                {"ip": ip, "up": False, "latency_ms": None, "hostname": None, "mac": None}
                for ip in ips_all
            ]
            self._ip_index = {ip: i for i, ip in enumerate(ips_all)}
        
        # Single scan pass with batched enrichment
        batch: List[dict] = []
        for r in scan_cidr(self.cidr, concurrency=128, timeout=1.0, count=1, tcp_fallback=True):
            batch.append(r)
            if len(batch) >= 32:
                self._enrich_and_store(batch)
                batch = []
        if batch:
            self._enrich_and_store(batch)
        self.last_scan_ts = time.time()
        self.scanning = False

    def _portscan_worker(self, ip: str) -> None:
        # top 1000 ports: here we use 1-1000 for simplicity. Can be replaced by nmap's top ports list.
        ports = list(range(1, 10001))
        try:
            openp = port_scan(ip, ports, concurrency=256, timeout=0.5)
        except Exception:
            openp = []
        self.portscan_open = openp
        self.portscan_running = False

    def _show_export_dialog(self, stdscr) -> None:
        """Show export dialog and handle CSV export."""
        h, w = stdscr.getmaxyx()
        
        # Dialog dimensions
        dialog_h = 15
        dialog_w = min(70, w - 10)
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
        include_down = False
        filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cursor_pos = len(filename)
        
        def refresh_dialog():
            dialog.erase()
            dialog.box()
            
            # Title
            title = " Export to CSV "
            try:
                dialog.addstr(0, (dialog_w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))
            except curses.error:
                pass
            
            # Instructions
            try:
                dialog.addstr(2, 2, "Filename:", curses.A_BOLD)
                dialog.addstr(3, 2, f" {filename}", curses.A_NORMAL)
                # Show cursor
                try:
                    dialog.addstr(3, 3 + cursor_pos, "", curses.A_REVERSE)
                except curses.error:
                    pass
                
                dialog.addstr(5, 2, "Options:", curses.A_BOLD)
                check = "[X]" if include_down else "[ ]"
                dialog.addstr(6, 2, f" {check} Include DOWN hosts")
                
                # Stats
                with self.scan_lock:
                    total = len(self.scan_results)
                    up_count = sum(1 for r in self.scan_results if r.get('up'))
                    down_count = total - up_count
                
                dialog.addstr(8, 2, "Preview:", curses.A_BOLD)
                if include_down:
                    dialog.addstr(9, 2, f" → Exporting {total} hosts ({up_count} UP, {down_count} DOWN)")
                else:
                    dialog.addstr(9, 2, f" → Exporting {up_count} hosts (UP only)")
                
                # Controls
                dialog.addstr(11, 2, "Controls:", curses.A_DIM)
                dialog.addstr(12, 2, " [Enter] Export  [Space] Toggle option  [Esc] Cancel", curses.A_DIM)
                
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
                    
                    output_path = export_to_csv(hosts_dict, filename, include_down=include_down)
                    self.export_message = f"✅ Exported to: {output_path}"
                    self.export_message_color = 1
                    
                except Exception as e:
                    self.export_message = f"❌ Export failed: {str(e)[:40]}"
                    self.export_message_color = 2
                
                self.export_message_time = time.time()
                break
                
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

            title = f"netscan-tui  iface={self.iface}  net={self.cidr}  rx={fmt(rx)}  tx={fmt(tx)}  filter={'UP' if self.only_up else 'ALL'}  sort={self.sort_by}{'↓' if self.sort_desc else '↑'}"
            stdscr.addstr(0, 0, title[: max(0, w - 1)], curses.A_BOLD | cpair(4))

            # Help line
            help_line = "[s]can  [r]efresh  [a]ctive-only  [e]xport CSV  [1-5] sort col  [o]cycle  [O]asc/desc  [Enter] re-scan ports  ↑/↓ select  [q]uit"
            stdscr.addstr(1, 0, help_line[: max(0, w - 1)], curses.A_DIM | cpair(4))

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
            state = 'running' if self.scanning else 'idle'
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
                        put("│ ⟳ Scanning ports...", curses.A_DIM | cpair(4))
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

            if ch == ord('q'):
                self.stop = True
                break
            elif ch == ord('s') and not self.scanning:
                threading.Thread(target=self._scan, daemon=True).start()
            elif ch == ord('e'):
                # Show export dialog
                self._show_export_dialog(stdscr)
            elif ch == ord('r'):
                # refresh detection
                self.iface = get_default_interface() or self.iface
                self.cidr = get_local_network_cidr() or self.cidr
            elif ch == ord('a'):
                self.only_up = not self.only_up
                self.sel = 0
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
