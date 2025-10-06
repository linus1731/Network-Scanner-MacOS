from __future__ import annotations

import ipaddress
import os
import platform
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import time
from dataclasses import dataclass
from typing import Generator, List, Optional, Iterable

from .ratelimit import get_global_limiter


@dataclass(frozen=True)
class PingResult:
    ip: str
    up: bool
    latency_ms: Optional[float]

    def as_dict(self) -> dict:
        return {"ip": self.ip, "up": self.up, "latency_ms": self.latency_ms}


def _build_ping_cmd(ip: str, count: int, timeout: float) -> List[str]:
    system = platform.system().lower()
    if system == "darwin":
        # macOS BSD ping uses -W in milliseconds
        ms = max(1, int(timeout * 1000))
        return [
            "/sbin/ping" if os.path.exists("/sbin/ping") else "ping",
            "-c",
            str(count),
            "-W",
            str(ms),
            ip,
        ]
    else:
        # Linux ping uses -W in seconds for per-packet timeout
        sec = max(1, int(round(timeout)))
        return [
            "/bin/ping" if os.path.exists("/bin/ping") else "ping",
            "-c",
            str(count),
            "-W",
            str(sec),
            ip,
        ]


def ping(ip: str, count: int = 1, timeout: float = 1.0) -> PingResult:
    # Apply rate limiting
    limiter = get_global_limiter()
    limiter.acquire(1)
    
    cmd = _build_ping_cmd(ip, count=count, timeout=timeout)
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=max(timeout * count + 0.5, timeout + 0.5),
            check=False,
        )
        output = proc.stdout or ""
        # Normalize decimal commas to dots for locales where ping prints e.g. "time=0,23 ms"
        output_norm = output.replace(",", ".")
        success = proc.returncode == 0 or ("bytes from" in output.lower())

        latency = None
        # Try to parse first reply line: time=XX ms
        m = re.search(r"time[=<]\s*([0-9]+(?:\.[0-9]+)?)\s*ms", output_norm, re.IGNORECASE)
        if m:
            latency = float(m.group(1))
        else:
            # Linux summary: rtt min/avg/max/mdev = a/b/c/d ms
            m2 = re.search(r"=\s*([0-9]+(?:\.[0-9]+)?)/([0-9]+(?:\.[0-9]+)?)/", output_norm)
            if m2:
                latency = float(m2.group(2))
            else:
                # BSD summary: "round-trip min/avg/max/stddev = 14.654/14.654/14.654/0.000 ms"
                m3 = re.search(r"round-trip .*?=\s*([0-9]+(?:\.[0-9]+)?)/([0-9]+(?:\.[0-9]+)?)/", output_norm, re.IGNORECASE)
                if m3:
                    latency = float(m3.group(2))

        return PingResult(ip=ip, up=bool(success), latency_ms=latency)
    except subprocess.TimeoutExpired:
        return PingResult(ip=ip, up=False, latency_ms=None)
    except Exception:
        # In case ping binary missing or other error
        return PingResult(ip=ip, up=False, latency_ms=None)


def expand_targets(target: str) -> List[str]:
    target = target.strip()
    # Range form: a.b.c.d-e or a.b.c.d-a.b.c.e
    if "-" in target and "/" not in target:
        start, end = target.split("-", 1)
        start_ip = ipaddress.ip_address(start)
        try:
            end_ip = ipaddress.ip_address(end)
        except ValueError:
            # If end is just the last octet
            base = start.split(".")
            if len(base) == 4 and end.isdigit():
                end_ip = ipaddress.ip_address(".".join(base[:3] + [end]))
            else:
                raise
        if int(end_ip) < int(start_ip):
            start_ip, end_ip = end_ip, start_ip
        return [str(ipaddress.ip_address(i)) for i in range(int(start_ip), int(end_ip) + 1)]

    # CIDR or single IP
    try:
        net = ipaddress.ip_network(target, strict=False)
        return [str(h) for h in net.hosts()] if net.num_addresses > 1 else [str(net.network_address)]
    except ValueError:
        # Single IP format may land here if not network
        ipaddress.ip_address(target)  # validate
        return [target]


def _tcp_probe(ip: str, ports: tuple[int, ...] = (80, 443, 22), timeout: float = 0.3) -> Optional[float]:
    """Try TCP connect to common ports; return latency_ms on first success, else None."""
    # Apply rate limiting for TCP probes
    limiter = get_global_limiter()
    
    for port in ports:
        limiter.acquire(1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            t0 = time.perf_counter()
            s.connect((ip, port))
            s.close()
            dt = (time.perf_counter() - t0) * 1000.0
            return dt
        except Exception:
            try:
                s.close()
            except Exception:
                pass
            continue
    return None


def scan_cidr(target: str, concurrency: int = 128, timeout: float = 1.0, count: int = 1, tcp_fallback: bool = False) -> Generator[dict, None, None]:
    hosts = expand_targets(target)
    if not hosts:
        return

    # Bound concurrency
    workers = max(1, min(concurrency, len(hosts), 1024))

    def worker(ip: str) -> dict:
        res = ping(ip, count=count, timeout=timeout)
        if (not res.up) and tcp_fallback:
            lat = _tcp_probe(ip)
            if lat is not None:
                res = PingResult(ip=ip, up=True, latency_ms=lat)
        return res.as_dict()

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netscan") as ex:
        future_map = {ex.submit(worker, ip): ip for ip in hosts}
        for fut in as_completed(future_map):
            res = fut.result()
            yield res


def _tcp_connect(ip: str, port: int, timeout: float = 0.5) -> bool:
    # Apply rate limiting for port scans
    limiter = get_global_limiter()
    limiter.acquire(1)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        return False


def port_scan(ip: str, ports: Iterable[int], concurrency: int = 256, timeout: float = 0.5) -> List[int]:
    """Return list of open ports using TCP connect scanning."""
    ports = list(ports)
    if not ports:
        return []
    workers = max(1, min(concurrency, len(ports), 1024))
    open_ports: List[int] = []
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netscan-ports") as ex:
        futs = {ex.submit(_tcp_connect, ip, p, timeout): p for p in ports}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                if fut.result():
                    open_ports.append(p)
            except Exception:
                pass
    open_ports.sort()
    return open_ports
